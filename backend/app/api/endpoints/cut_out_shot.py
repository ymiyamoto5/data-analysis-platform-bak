import json
from typing import Any, Dict, List, Optional

from backend.app.api.deps import get_db
from backend.app.crud.crud_celery_task import CRUDCeleryTask
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.models.celery_task import CeleryTask
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
from backend.app.models.data_collect_history_sensor import DataCollectHistorySensor
from backend.app.models.sensor import Sensor
from backend.app.schemas.cut_out_shot import CutOutShotCancel, CutOutShotPulse, CutOutShotStrokeDisplacement
from backend.app.services.cut_out_shot_service import CutOutShotService
from backend.app.worker.celery import celery_app
from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from backend.file_manager.file_manager import FileInfo, FileManager
from fastapi import APIRouter, Depends, HTTPException, Query
from pandas.core.frame import DataFrame
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/target_dir")
def fetch_target_date_str(target_date_timestamp: str = Query(...)):
    """ショット切り出し対象となる日付文字列を返す"""
    target_dir_name: str = CutOutShotService.get_target_dir(target_date_timestamp)

    return target_dir_name


@router.get("/cut_out_sensor")
def fetch_cut_out_sensor(
    machine_id: str = Query(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """マスタデータから切り出しの基準となるセンサーがストローク変位、パルスどちらであるかを返す"""

    # 機器に紐づくセンサー情報を取得
    sensors: List[Sensor] = CRUDMachine.select_sensors_by_machine_id(db, machine_id)

    cut_out_sensor: Optional[Sensor] = common.get_cut_out_shot_sensor(sensors)
    if cut_out_sensor is None:
        raise HTTPException(status_code=500, detail="切り出し基準となるセンサーがありません")

    return {"cut_out_sensor": cut_out_sensor.sensor_type_id}


@router.get("/cut_out_sensor_from_history")
def fetch_cut_out_sensor_from_history(
    machine_id: str = Query(..., max_length=255, regex=common.ID_PATTERN),
    target_date_str: str = Query(...),  # yyyyMMddHHMMSS文字列
    db: Session = Depends(get_db),
):
    """履歴から切り出しの基準となるセンサーがストローク変位、パルスどちらであるかを返す"""

    # 機器に紐づく設定値を履歴から取得
    # NOTE: 1クエリで取得可能だが、複雑なクエリになるためひとまず2クエリに分けている。
    history: DataCollectHistory = CRUDDataCollectHistory.select_by_machine_id_started_at(db, machine_id, target_date_str)
    cut_out_target_handlers: List[DataCollectHistoryHandler] = CRUDDataCollectHistory.select_cut_out_target_handlers_by_hisotry_id(
        db, history.id
    )

    # 切り出し基準となるセンサーを特定
    for handler in cut_out_target_handlers:
        cut_out_sensor: Optional[DataCollectHistorySensor] = common.get_cut_out_shot_sensor(handler.data_collect_history_sensors)
        if cut_out_sensor is not None:
            break

    if cut_out_sensor is None:
        raise HTTPException(status_code=500, detail="切り出し基準となるセンサーがありません")

    return {"cut_out_sensor": cut_out_sensor.sensor_type_id}


@router.get("/shots")
def fetch_shots(
    machine_id: str = Query(..., max_length=255, regex=common.ID_PATTERN),
    target_date_str: str = Query(...),  # yyyyMMddHHMMSS文字列
    page: int = Query(...),
    db: Session = Depends(get_db),
):
    """対象区間の最初のpklファイルを読み込み、ストローク変位値をリサンプリングして返す"""

    history: DataCollectHistory = CRUDDataCollectHistory.select_by_machine_id_started_at(db, machine_id, target_date_str)
    cut_out_target_handlers: List[DataCollectHistoryHandler] = CRUDDataCollectHistory.select_cut_out_target_handlers_by_hisotry_id(
        db, history.id
    )

    if len(cut_out_target_handlers) == 0:
        raise HTTPException(status_code=500, detail="対象ハンドラーがありません")
    if len(cut_out_target_handlers) == 1:
        handler: DataCollectHistoryHandler = cut_out_target_handlers[0]
    if len(cut_out_target_handlers) >= 2:
        handler = [x for x in cut_out_target_handlers if x.is_primary][0]

    # ハンドラーのファイルリスト作成
    try:
        files_info: List[FileInfo] = FileManager.get_files_info(
            machine_id, handler.data_collect_history_gateway.gateway_id, handler.handler_id, target_date_str
        )
    except Exception:
        raise HTTPException(status_code=400, detail="対象ファイルがありません")

    if page > len(files_info) - 1:
        raise HTTPException(status_code=400, detail="データがありません")

    df: DataFrame = CutOutShotService.fetch_df(files_info[page].file_path)

    # リサンプリング
    sampling_frequency: int = handler.sampling_frequency
    resampled_df: DataFrame = CutOutShotService.resample_df(df, sampling_frequency)

    # データ数が1,000件を超える場合は先頭1,000件のみ取得
    if len(resampled_df) > 1000:
        resampled_df = resampled_df.head(1000)

    sensors: List[DataCollectHistorySensor] = []
    for handler in cut_out_target_handlers:
        sensors.append(handler.data_collect_history_sensors)
    sensors = [x for sensor in sensors for x in sensor]  # flatten

    # センサー値を物理変換
    converted_df: DataFrame = CutOutShotService.physical_convert_df(resampled_df, sensors)
    # NOTE: nanはJSON解釈できないので変換しておく
    converted_df = converted_df.fillna("")

    data: Dict[str, Any] = converted_df.to_dict(orient="records")

    return {"data": data, "fileCount": len(files_info)}


@router.post("/stroke_displacement")
def cut_out_shot_stroke_displacement(cut_out_shot_in: CutOutShotStrokeDisplacement, db: Session = Depends(get_db)):
    """ストローク変位値でのショット切り出しタスクを登録"""

    cut_out_shot_json = json.dumps(cut_out_shot_in.__dict__)

    task_name = "backend.app.worker.tasks.cut_out_shot.cut_out_shot_task"

    task = celery_app.send_task(
        task_name,
        (
            cut_out_shot_json,
            common.CUT_OUT_SHOT_SENSOR_TYPES[0],
        ),
    )

    logger.info(f"cut_out_shot started. task_id: {task.id}")

    save_task_info(cut_out_shot_in.machine_id, cut_out_shot_in.target_date_str, task.id, db)

    return {"task_id": task.id, "task_info": task.info}


@router.post("/pulse")
def cut_out_shot_pulse(cut_out_shot_in: CutOutShotPulse, db: Session = Depends(get_db)):
    """パルスでのショット切り出しタスクを登録"""

    cut_out_shot_json = json.dumps(cut_out_shot_in.__dict__)

    task_name = "backend.app.worker.tasks.cut_out_shot.cut_out_shot_task"

    task = celery_app.send_task(
        task_name,
        (
            cut_out_shot_json,
            common.CUT_OUT_SHOT_SENSOR_TYPES[1],
        ),
    )

    logger.info(f"cut_out_shot started. task_id: {task.id}")

    save_task_info(cut_out_shot_in.machine_id, cut_out_shot_in.target_date_str, task.id, db)

    return {"task_id": task.id, "task_info": task.info}


@router.post("/cancel")
def cut_out_shot_cancel(cut_out_shot_in: CutOutShotCancel):
    """ショット切り出しタスクを取り消し"""
    active_tasks = celery_app.control.inspect().active()
    for _, task_list in active_tasks.items():
        for task in task_list:
            if cut_out_shot_in.machine_id in task["args"][0]:
                celery_app.control.revoke(task["id"], terminate=True)

    return


def save_task_info(machine_id: str, target_date_str: str, task_id: str, db: Session) -> None:
    """タスク情報を保持する"""
    data_collect_history: DataCollectHistory = CRUDDataCollectHistory.select_by_machine_id_started_at(db, machine_id, target_date_str)

    new_data_celery_task = CeleryTask(
        task_id=task_id,
        data_collect_history_id=data_collect_history.id,
        task_type="cut_out_shot",
    )

    CRUDCeleryTask.insert(db, obj_in=new_data_celery_task)

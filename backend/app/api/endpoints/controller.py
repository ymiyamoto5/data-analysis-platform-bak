import glob
import os
import time
import traceback
from datetime import datetime
from typing import Final, List, Optional, Tuple, Union

from backend.app.api.deps import get_db
from backend.app.crud.crud_celery_task import CRUDCeleryTask
from backend.app.crud.crud_controller import CRUDController
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_handler import CRUDHandler
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.models.celery_task import CeleryTask
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_sensor import DataCollectHistorySensor
from backend.app.models.handler import Handler
from backend.app.models.machine import Machine
from backend.app.models.sensor import Sensor
from backend.app.services.data_recorder_service import DataRecorderService
from backend.app.worker.celery import celery_app
from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

router = APIRouter()


WAIT_SECONDS: Final[int] = 1


def validation(machine: Machine, collect_status: str, status) -> Tuple[bool, Optional[str], int]:
    """machineとmachineに紐づくgatewayのvalidation
    * Noneでないこと
    * 対応するGatewayが1つ以上あること
    * 収集ステータスが正しいこと
    * gateway_resultが-1でないこと
    * GWステータスが正しいこと
    """

    if machine is None:
        message: str = ErrorMessage.generate_message(ErrorTypes.NOT_EXISTS)
        return False, message, 404

    if len(machine.gateways) == 0:
        message = ErrorMessage.generate_message(ErrorTypes.NO_DATA)
        return False, message, 404

    if machine.collect_status != collect_status:
        message = ErrorMessage.generate_message(ErrorTypes.GW_STATUS_ERROR, machine.collect_status)
        return False, message, 400

    for gateway in machine.gateways:
        if gateway.gateway_result == -1:
            message = ErrorMessage.generate_message(ErrorTypes.GW_RESULT_ERROR, gateway.gateway_result)
            return False, message, 500

        if gateway.status != status:
            message = ErrorMessage.generate_message(ErrorTypes.GW_STATUS_ERROR, gateway.status)
            return False, message, 500

    return True, None, 200


def multi_handler_validation(handlers: List[Handler]) -> Tuple[bool, Optional[str], int]:
    """複数handler構成のvalidation
    * プライマリーハンドラーが1台のみ存在すること
    * sampling_frequencyが一致していること
    * sampling_ch_numが一致していること（物理的に数が一致しない場合、ダミーセンサーを登録）
    * handler_typeが一致していること
    """

    if len([handler for handler in handlers if handler.is_primary]) != 1:
        message = ErrorMessage.generate_message(ErrorTypes.MULTI_HANDLER_ERROR)
        return False, message, 400

    if not all(handler.sampling_frequency == handlers[0].sampling_frequency for handler in handlers):
        message = ErrorMessage.generate_message(ErrorTypes.MULTI_HANDLER_ERROR)
        return False, message, 400

    if not all(handler.sampling_ch_num == handlers[0].sampling_ch_num for handler in handlers):
        message = ErrorMessage.generate_message(ErrorTypes.MULTI_HANDLER_ERROR)
        return False, message, 400

    if not all(handler.handler_type == handlers[0].handler_type for handler in handlers):
        message = ErrorMessage.generate_message(ErrorTypes.MULTI_HANDLER_ERROR)
        return False, message, 400

    return True, None, 200


@router.post("/setup/{machine_id}")
def setup(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """指定機器のデータ収集段取開始"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集完了状態かつGW停止状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.RECORDED.value, common.STATUS.STOP.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    # gateway毎にチェックが必要
    for gateway in machine.gateways:
        # 複数ハンドラー構成のハンドラー情報取得
        handlers: List[Handler] = CRUDHandler.select_multi_handlers_by_gateway_id(db, gateway.gateway_id)

        # handlersが空リストなら複数ハンドラー構成はないのでmulti_handler_validation不要
        if not handlers:
            continue

        # multi_handler_validationを呼び出し、各種チェック
        is_valid, message, error_code = multi_handler_validation(handlers)
        if not is_valid:
            raise HTTPException(status_code=error_code, detail=message)

    # 退避ディレクトリ作成
    processed_dir_path: str = DataRecorderService.get_processed_dir_path(machine_id=machine_id, started_at=utc_now)

    try:
        CRUDController.setup(db, machine=machine, utc_now=utc_now, processed_dir_path=processed_dir_path)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/start/{machine_id}")
def start(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """指定機器のデータ収集開始"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 段取状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.SETUP.value, common.STATUS.RUNNING.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    try:
        CRUDController.start(db, machine=machine, utc_now=utc_now)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/pause/{machine_id}")
def pause(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """指定機器のデータ収集中断（中断中もデータ自体は収集されている。中断区間はショット切り出しの対象外となる。）"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集開始状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.START.value, common.STATUS.RUNNING.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    try:
        CRUDController.pause(db, machine=machine, utc_now=utc_now)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/resume/{machine_id}")
def resume(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """指定機器のデータ収集再開"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集中断状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.PAUSE.value, common.STATUS.RUNNING.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    # RESUMEはDBの状態としては保持しない。STARTに更新する。
    try:
        CRUDController.resume(db, machine=machine, utc_now=utc_now)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/stop/{machine_id}")
def stop(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """指定機器のデータ収集停止"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集開始状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.START.value, common.STATUS.RUNNING.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    # DB更新
    try:
        CRUDController.stop(db, machine=machine, utc_now=utc_now)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/check/{machine_id}")
def check(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """data_recorderによるデータ取り込みが完了したか確認。dataディレクトリにdatファイルが残っていなければ完了とみなす。"""

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集停止状態かつGW停止状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.STOP.value, common.STATUS.STOP.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    data_dir: str = os.environ["DATA_DIR"]

    latest_predictor_task: CeleryTask = CRUDCeleryTask.select_latest_by_task_type(db, machine_id, "predictor")

    while True:
        # gateway, handlerに関係なくすべてのdatファイルが捌けていること
        data_file_list: List[str] = glob.glob(os.path.join(data_dir, f"{machine_id}_*.dat"))

        if len(data_file_list) != 0:
            time.sleep(WAIT_SECONDS)
            continue

        if machine.auto_predict:
            preditor_task_info = CRUDCeleryTask.select_by_id(latest_predictor_task.task_id)
            if preditor_task_info["status"] == "PROGRESS":
                time.sleep(WAIT_SECONDS)
                continue

        utc_now: datetime = datetime.utcnow()

        try:
            CRUDController.record(db, machine=machine, utc_now=utc_now)
        except Exception:
            raise HTTPException(status_code=500, detail="DB update error.")

        return


@router.post("/reset/{machine_id}")
def reset(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """指定機器のデータ収集初期化"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    try:
        CRUDController.reset(db, machine=machine, utc_now=utc_now)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="DB update error.")

    # celeryタスク取り消し
    active_tasks = celery_app.control.inspect().active()
    for _, task_list in active_tasks.items():
        for task in task_list:
            if machine_id in task["args"]:
                celery_app.control.revoke(task["id"], terminate=True)

    return


@router.post("/run-data-recorder/{machine_id}")
def run_data_recorder(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """data_recorderタスクを登録"""

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 段取状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.SETUP.value, common.STATUS.RUNNING.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    try:
        latest_data_collect_history: DataCollectHistory = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="DB read error.")

    task_name = "backend.app.worker.tasks.data_recorder.data_recorder_task"

    for gateway in machine.gateways:
        for handler in gateway.handlers:
            # 複数ハンドラーでプライマリーハンドラーでないものは生データが生成されないため記録する必要がない。
            if handler.is_multi and not handler.is_primary:
                continue
            task = celery_app.send_task(task_name, (machine_id, gateway.gateway_id, handler.handler_id))
            logger.info(f"data_recorder started. task_id: {task.id}")

            # タスク情報を保持する
            new_data_celery_task = CeleryTask(
                task_id=task.id,
                data_collect_history_id=latest_data_collect_history.id,
                task_type="data_recoder",
            )

    CRUDCeleryTask.insert(db, obj_in=new_data_celery_task)

    return {"task_id": task.id, "task_info": task.info}


@router.post("/run-cut-out-shot/{machine_id}")
def run_cut_out_shot(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """auto_cut_out_shotタスクを登録"""

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 段取状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.START.value, common.STATUS.RUNNING.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    try:
        latest_data_collect_history: DataCollectHistory = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)
        cut_out_target_sensors: List[DataCollectHistorySensor] = CRUDDataCollectHistory.select_cut_out_target_sensors_by_history_id(
            db, latest_data_collect_history.id
        )
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="DB read error.")

    sensors: List[DataCollectHistorySensor] = cut_out_target_sensors
    cut_out_shot_sensor: Optional[Union[Sensor, DataCollectHistorySensor]] = common.get_cut_out_shot_sensor(sensors)
    if cut_out_shot_sensor is None:
        raise HTTPException(status_code=500, detail="切り出し基準となるセンサーがありません")
    sensor_type: str = cut_out_shot_sensor.sensor_type_id

    task_name = "backend.app.worker.tasks.cut_out_shot.auto_cut_out_shot_task"

    task = celery_app.send_task(
        task_name,
        (
            machine_id,
            sensor_type,
        ),
    )

    logger.info(f"cut_out_shot started. task_id: {task.id}")

    # タスク情報を保持する
    new_data_celery_task = CeleryTask(
        task_id=task.id,
        data_collect_history_id=latest_data_collect_history.id,
        task_type="auto_cut_out_shot",
    )

    CRUDCeleryTask.insert(db, obj_in=new_data_celery_task)

    return {"task_id": task.id, "task_info": task.info}


@router.post("/run-predictor/{machine_id}")
def run_predictor(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """predictorタスクを登録"""

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 段取状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.START.value, common.STATUS.RUNNING.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    task_name = "backend.app.worker.tasks.predictor.predictor_task"

    task = celery_app.send_task(task_name, (machine_id,))

    logger.info(f"predictor started. task_id: {task.id}")

    # タスク情報を保持する
    latest_data_collect_history: DataCollectHistory = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)

    new_data_celery_task = CeleryTask(
        task_id=task.id,
        data_collect_history_id=latest_data_collect_history.id,
        task_type="predictor",
    )

    CRUDCeleryTask.insert(db, obj_in=new_data_celery_task)

    return {"task_id": task.id, "task_info": task.info}

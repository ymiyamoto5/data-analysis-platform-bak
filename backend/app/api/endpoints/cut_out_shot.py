from typing import Any, Dict, List, Optional

from backend.app.api.deps import get_db
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_detail import DataCollectHistoryDetail
from backend.app.schemas.cut_out_shot import CutOutShotDisplacement, CutOutShotPulse
from backend.app.services.cut_out_shot_service import CutOutShotService
from backend.common import common
from backend.cut_out_shot.cut_out_shot import CutOutShot
from backend.cut_out_shot.displacement_cutter import DisplacementCutter
from backend.cut_out_shot.pulse_cutter import PulseCutter
from backend.file_manager.file_manager import FileInfo
from fastapi import APIRouter, Depends, HTTPException, Query
from pandas.core.frame import DataFrame
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/target_dir")
def fetch_target_date_str(target_date_timestamp: str = Query(...)):
    """ショット切り出し対象となる日付文字列を返す"""
    target_dir_name: str = CutOutShotService.get_target_dir(target_date_timestamp)

    return target_dir_name


@router.get("/shots")
def fetch_shots(
    machine_id: str = Query(..., max_length=255, regex=common.ID_PATTERN),
    target_date_str: str = Query(...),  # yyyyMMddHHMMSS文字列
    page: int = Query(...),
    db: Session = Depends(get_db),
):
    """対象区間の最初のpklファイルを読み込み、変位値をリサンプリングして返す"""

    files_info: Optional[List[FileInfo]] = CutOutShotService.get_files_info(machine_id, target_date_str)

    if files_info is None:
        raise HTTPException(status_code=400, detail="対象ファイルがありません")

    # リクエストされたファイルがファイル数を超えている場合
    if page > len(files_info) - 1:
        raise HTTPException(status_code=400, detail="データがありません")

    # 対象ディレクトリから1ファイル取得
    target_file = files_info[page].file_path
    df: DataFrame = CutOutShotService.fetch_df(target_file)

    # 機器に紐づく設定値を履歴から取得
    history: DataCollectHistory = CRUDDataCollectHistory.select_by_machine_id_started_at(
        db, machine_id, target_date_str
    )

    # リサンプリング
    resampled_df: DataFrame = CutOutShotService.resample_df(df, history.sampling_frequency)

    # DataCollectHistoryDetailはセンサー毎の設定値
    sensors: List[DataCollectHistoryDetail] = history.data_collect_history_details

    # センサー値を物理変換
    converted_df: DataFrame = CutOutShotService.physical_convert_df(resampled_df, sensors)

    data: Dict[str, Any] = converted_df.to_dict(orient="records")

    return {"data": data, "fileCount": len(files_info)}


@router.post("/displacement")
def cut_out_shot_displacement(cut_out_shot_in: CutOutShotDisplacement, db: Session = Depends(get_db)):
    """変位値でのショット切り出し"""

    cutter = DisplacementCutter(cut_out_shot_in.start_displacement, cut_out_shot_in.end_displacement, margin=0.1)

    # TODO: サブプロセスでcut_out_shot実行
    cut_out_shot = CutOutShot(
        cutter=cutter, machine_id=cut_out_shot_in.machine_id, target=cut_out_shot_in.target_date_str, db=db
    )
    cut_out_shot.cut_out_shot()

    return


@router.post("/pulse")
def cut_out_shot_pulse(cut_out_shot_in: CutOutShotPulse, db: Session = Depends(get_db)):
    """変位値でのショット切り出し"""

    cutter = PulseCutter(cut_out_shot_in.threshold)

    # TODO: サブプロセスでcut_out_shot実行
    cut_out_shot = CutOutShot(
        cutter=cutter, machine_id=cut_out_shot_in.machine_id, target=cut_out_shot_in.target_date_str, db=db
    )
    cut_out_shot.cut_out_shot()

    return

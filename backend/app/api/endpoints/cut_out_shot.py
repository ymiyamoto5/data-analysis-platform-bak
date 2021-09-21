import os
import pandas as pd
from typing import List, Optional
from datetime import datetime
from backend.file_manager.file_manager import FileManager, FileInfo
from backend.data_converter.data_converter import DataConverter
from backend.common import common
from backend.cut_out_shot.cut_out_shot import CutOutShot
from backend.app.crud.crud_sensor import CRUDSensor
from backend.app.schemas.cut_out_shot import CutOutShotBase
from fastapi import Depends, APIRouter, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db


router = APIRouter()


@router.get("/target_dir")
def fetch_target_dir(
    machine_id: str = Query(..., max_length=255, regex=common.ID_PATTERN), target_date_timestamp: str = Query(...)
):
    """ショット切り出し対象となるディレクトリ名を返す"""

    # NOTE: ブラウザからは文字列のUNIXTIME(ミリ秒)で与えられる。秒単位に直して変換。
    target_date: datetime = datetime.fromtimestamp(int(target_date_timestamp) / 1000)
    target_date_str: str = datetime.strftime(target_date, "%Y%m%d%H%M%S")
    target_dir_name = machine_id + "-" + target_date_str

    return target_dir_name


@router.get("/shots")
def fetch_shots(
    machine_id: str = Query(..., max_length=255, regex=common.ID_PATTERN),
    target_dir: str = Query(...),
    page: int = Query(...),
    db: Session = Depends(get_db),
):
    """対象区間の最初のpklファイルを読み込み、変位値をリサンプリングして返す"""

    data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")
    data_full_path: str = os.path.join(data_dir, target_dir)

    files_info: Optional[List[FileInfo]] = FileManager.create_files_info(data_full_path, machine_id, "pkl")

    if files_info is None:
        raise HTTPException(status_code=400, detail="対象ファイルがありません")

    # リクエストされたファイルがファイル数を超えている場合
    if page > len(files_info) - 1:
        raise HTTPException(status_code=400, detail="データがありません")

    # 対象ディレクトリから1ファイル取得
    target_file = files_info[page].file_path

    df = pd.read_pickle(target_file)
    # timestampを日時に戻しdaterange indexとする。
    df["timestamp"] = df["timestamp"].map(lambda x: datetime.fromtimestamp(x))
    df = df.set_index(["timestamp"])

    # TODO: リサンプリングは別モジュール化して、間隔を可変にする
    df = df.resample("10ms").mean()
    df = df.reset_index()

    sensors = CRUDSensor.fetch_sensors_by_machine_id(db, machine_id)
    for sensor in sensors:
        func = DataConverter.get_physical_conversion_formula(sensor)
        df.loc[:, sensor.sensor_id] = df[sensor.sensor_id].map(func)

    data = df.to_dict(orient="records")

    return {"data": data, "fileCount": len(files_info)}


@router.post("/")
def cut_out_shot(cut_out_shot_in: CutOutShotBase):
    """ショット切り出し"""

    # TODO: サブプロセスでcut_out_shot実行
    cut_out_shot = CutOutShot(machine_id=cut_out_shot_in.machine_id)
    cut_out_shot.cut_out_shot(
        rawdata_dir_name=cut_out_shot_in.target_dir,
        start_displacement=cut_out_shot_in.start_displacement,
        end_displacement=cut_out_shot_in.end_displacement,
    )

    return

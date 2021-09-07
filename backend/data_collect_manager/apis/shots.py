from backend.data_collect_manager.dao.sensor_dao import SensorDAO
import os
import pandas as pd
from typing import List, Optional
from datetime import datetime
from flask import Blueprint, jsonify, request
from backend.file_manager.file_manager import FileManager, FileInfo
from backend.data_converter.data_converter import DataConverter
from backend.common import common
from backend.common.common_logger import logger

shots = Blueprint("shots", __name__)


@shots.route("/shots", methods=["GET"])
def fetch_shots():
    """対象区間の先頭N件を取得する"""

    machine_id = request.args.get("machineId")
    target_date_param = request.args.get("targetDate")

    # NOTE: ブラウザからは文字列のUNIXTIME(ミリ秒)で与えられる。秒単位に直して変換。
    target_date: datetime = datetime.fromtimestamp(int(target_date_param) / 1000)
    target_date_str: str = datetime.strftime(target_date, "%Y%m%d%H%M%S")
    target_dir_name = machine_id + "-" + target_date_str

    data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")
    data_full_path: str = os.path.join(data_dir, target_dir_name)

    files_info: Optional[List[FileInfo]] = FileManager.create_files_info(data_full_path, machine_id, "pkl")

    if files_info is None:
        pass

    # 対象ディレクトリから1ファイル取得
    target_file = files_info[0].file_path

    df = pd.read_pickle(target_file)
    # timestampを日時に戻しdaterange indexとする。
    df = df[["timestamp", "displacement"]]
    df["timestamp"] = df["timestamp"].map(lambda x: datetime.fromtimestamp(x))
    df = df.set_index(["timestamp"])

    # リサンプリング
    df = df.resample("10ms").mean()
    df = df.reset_index()

    # TODO: displacement以外の対応
    sensor = SensorDAO.select_by_id(machine_id, "displacement")
    func = DataConverter.get_physical_conversion_formula(sensor)
    df.loc[:, sensor.sensor_id] = df[sensor.sensor_id].map(func)

    data = df.to_dict(orient="records")

    return jsonify(data), 200

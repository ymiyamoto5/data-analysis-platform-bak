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
from marshmallow import Schema, fields, ValidationError, validate
from backend.data_collect_manager.apis.api_common import character_validate
from backend.common.error_message import ErrorMessage, ErrorTypes
from backend.cut_out_shot.cut_out_shot import CutOutShot
import traceback

shots = Blueprint("shots", __name__)


class CutOutShotSchema(Schema):
    machine_id = fields.Str(required=True, validate=[character_validate, validate.Length(min=1, max=255)])
    start_displacement = fields.Float(validate=validate.Range(min=0.0, max=100.0))
    end_displacement = fields.Float(validate=validate.Range(min=0.0, max=100.0))
    target_dir = fields.Str(required=True)


cut_out_shot_schema = CutOutShotSchema()


@shots.route("/target_dir", methods=["GET"])
def fetch_target_dir():
    """ショット切り出し対象となるディレクトリ名を返す"""

    machine_id = request.args.get("machine_id")
    target_date_param = request.args.get("targetDate")

    # NOTE: ブラウザからは文字列のUNIXTIME(ミリ秒)で与えられる。秒単位に直して変換。
    target_date: datetime = datetime.fromtimestamp(int(target_date_param) / 1000)
    target_date_str: str = datetime.strftime(target_date, "%Y%m%d%H%M%S")
    target_dir_name = machine_id + "-" + target_date_str

    return jsonify(target_dir_name), 200


@shots.route("/shots", methods=["GET"])
def fetch_shots():
    """対象区間の最初のpklファイルを読み込み、変位値をリサンプリングして返す"""

    machine_id = request.args.get("machine_id")
    target_dir = request.args.get("targetDir")

    data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")
    data_full_path: str = os.path.join(data_dir, target_dir)

    files_info: Optional[List[FileInfo]] = FileManager.create_files_info(data_full_path, machine_id, "pkl")

    if files_info is None:
        message: str = "対象ファイルがありません"
        return jsonify({"message": message}), 500

    # 対象ディレクトリから1ファイル取得
    target_file = files_info[0].file_path

    df = pd.read_pickle(target_file)
    # timestampを日時に戻しdaterange indexとする。
    df = df[["timestamp", "displacement"]]
    df["timestamp"] = df["timestamp"].map(lambda x: datetime.fromtimestamp(x))
    df = df.set_index(["timestamp"])

    # TODO: リサンプリングは別モジュール化して、間隔を可変にする
    df = df.resample("10ms").mean()
    df = df.reset_index()

    # TODO: displacement以外の対応
    sensor = SensorDAO.select_by_id(machine_id, "displacement")
    func = DataConverter.get_physical_conversion_formula(sensor)
    df.loc[:, sensor.sensor_id] = df[sensor.sensor_id].map(func)

    data = df.to_dict(orient="records")

    return jsonify(data), 200


@shots.route("/cut_out_shot", methods=["POST"])
def cut_out_shot():
    """ショット切り出し"""

    json_data = request.get_json()

    if not json_data:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.NO_INPUT_DATA)
        return jsonify({"message": message}), 400

    try:
        data = cut_out_shot_schema.load(json_data)
    except ValidationError as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.VALID_ERROR, e.messages)
        return jsonify({"message": message}), 400

    # サブプロセスでcut_out_shot実行
    cut_out_shot = CutOutShot(machine_id=data["machine_id"], margin=0.3)
    try:
        cut_out_shot.cut_out_shot(
            rawdata_dir_name=data["target_dir"],
            start_displacement=data["start_displacement"],
            end_displacement=data["end_displacement"],
        )
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.CUT_OUT_SHOT_ERROR, e.messages)
        return jsonify({"message": message}), 500

    return jsonify({}), 200

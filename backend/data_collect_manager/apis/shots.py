from datetime import datetime
from flask import Blueprint, jsonify, request
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

    # 対象ディレクトリから1ファイル取得
    data = {}

    return jsonify(data), 200

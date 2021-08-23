from datetime import datetime
from typing import List
from flask import Blueprint, jsonify
from backend.data_collect_manager.dao.data_collect_history_dao import DataCollectHistoryDAO

data_collect_history = Blueprint("data_collect_history", __name__)


@data_collect_history.route("/data_collect_history", methods=["GET"])
def fetch_data_collect_history():
    """データ収集履歴を返す"""

    history = DataCollectHistoryDAO.select_all()

    # 表示用に変換
    def _convert_date_time(x):
        x.started_at = datetime.strftime(x.started_at, "%Y-%m-%d %H:%M:%S.%f")
        if x.ended_at is not None:
            x.ended_at = datetime.strftime(x.ended_at, "%Y-%m-%d %H:%M:%S.%f")
        return x

    history = list(map(_convert_date_time, history))

    return jsonify(history)

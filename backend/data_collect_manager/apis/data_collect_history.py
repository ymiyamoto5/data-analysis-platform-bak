from datetime import datetime
from flask import Blueprint, jsonify, request
from backend.data_collect_manager.models.data_collect_history import DataCollectHistory
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.db import db
from sqlalchemy.orm import joinedload
from sqlalchemy import desc

data_collect_history = Blueprint("data_collect_history", __name__)


@data_collect_history.route("/data_collect_history", methods=["GET"])
def fetch_data_collect_history():
    """データ収集履歴を返す"""

    history = (
        DataCollectHistory.query.order_by(desc(DataCollectHistory.started_at))
        .options(
            joinedload(DataCollectHistory.machine),
        )
        .all()
    )

    # 表示用に変換
    def _convert_date_time(x):
        x.started_at = datetime.strftime(x.started_at, "%Y-%m-%d %H:%M:%S.%f")
        if x.ended_at is not None:
            x.ended_at = datetime.strftime(x.ended_at, "%Y-%m-%d %H:%M:%S.%f")
        return x

    history = list(map(_convert_date_time, history))

    return jsonify(history)

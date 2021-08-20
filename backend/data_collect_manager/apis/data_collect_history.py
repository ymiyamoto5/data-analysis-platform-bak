from flask import Blueprint, jsonify, request
from backend.data_collect_manager.models.data_collect_history import DataCollectHistory
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.db import db
from sqlalchemy.orm import joinedload

data_collect_history = Blueprint("data_collect_history", __name__)


@data_collect_history.route("/data_collect_history", methods=["GET"])
def fetch_data_collect_history():
    """データ収集履歴を返す"""

    hisotry = DataCollectHistory.query.options(
        joinedload(DataCollectHistory.machine_id),
    ).all()

    return jsonify(hisotry)

from datetime import datetime
from typing import List
from flask import Blueprint, jsonify
from backend.data_collect_manager.models.data_collect_history import DataCollectHistory
from backend.data_collect_manager.dao.data_collect_history_dao import DataCollectHistoryDAO

data_collect_history = Blueprint("data_collect_history", __name__)


@data_collect_history.route("/data_collect_history", methods=["GET"])
def fetch_data_collect_history():
    """データ収集履歴を返す"""

    history: List[DataCollectHistory] = DataCollectHistoryDAO.select_all()

    return jsonify(history)


@data_collect_history.route("/data_collect_history/<string:machine_id>", methods=["GET"])
def fetch_data_collect_history_by_machine(machine_id):
    """特定機器のデータ収集履歴を返す"""

    history: List[DataCollectHistory] = DataCollectHistoryDAO.select_by_machine_id(machine_id)

    return jsonify(history)

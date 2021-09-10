from datetime import datetime
from typing import List
from flask import Blueprint, jsonify
from backend.data_collect_manager.models.data_collect_history import DataCollectHistory
from backend.data_collect_manager.dao.data_collect_history_dao import (
    DataCollectHistoryDAO,
)
import traceback
from backend.common.common_logger import logger
from backend.common.error_message import ErrorMessage, ErrorTypes

data_collect_history = Blueprint("data_collect_history", __name__)


@data_collect_history.route("/data_collect_history", methods=["GET"])
def fetch_data_collect_history():
    """データ収集履歴を返す"""

    try:
        history: List[DataCollectHistory] = DataCollectHistoryDAO.select_all()
        return jsonify(history), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.READ_FAIL, str(e))
        return jsonify({"message": message}), 500

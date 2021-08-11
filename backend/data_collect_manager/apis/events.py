from flask import Blueprint, jsonify, request
from marshmallow import Schema, fields, ValidationError, validate
from typing import Optional, List
import traceback
from backend.common.error_message import ErrorMessage, ErrorTypes
from backend.common import common
from backend.common.common_logger import logger
from backend.event_manager.event_manager import EventManager

events = Blueprint("events", __name__)


# @events.route("/events/<string:gateway_id>", methods=["GET"])
# def fetch_latest_event(gateway_id):
#     """指定Gatewayの最新イベントを取得"""

#     latest_events_index: Optional[str] = EventManager.get_latest_events_index()

#     if latest_events_index is None:
#         message: str = "events_indexがありません。"
#         logger.error(message)
#         return jsonify({"message": message}), 500

#     latest_event: List[dict] = EventManager.get_latest_event(latest_events_index)

#     if len(latest_event) == 0:
#         message: str = "イベントがありません。"
#         logger.error(message)
#         return jsonify({"message": message}), 500

#     return jsonify(latest_event)

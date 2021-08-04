from flask import Blueprint, jsonify, request
from data_collect_manager.models.gateway import Handler
from data_collect_manager.models.db import db
import re
import logging

# TODO: data_collect_managerのloggerを引き継ぐように設定したい。
logger = logging.getLogger("data_collect_manager")

handlers = Blueprint("handlers", __name__)


@handlers.route("/handlers", methods=["GET"])
def fetch_handlers():
    """ handlerを起点に関連エンティティを全結合したデータを返す。"""

    handlers = Handler.query.all()

    return jsonify(handlers)


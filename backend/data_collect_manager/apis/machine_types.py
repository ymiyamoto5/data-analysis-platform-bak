from flask import Blueprint, jsonify
from marshmallow import Schema, fields, ValidationError, validate
from backend.data_collect_manager.apis.api_common import character_validate
from backend.data_collect_manager.dao.machine_type_dao import MachineTypeDAO
import traceback
from backend.common.common_logger import logger
from backend.common.error_message import ErrorMessage, ErrorTypes

machine_types = Blueprint("machine_types", __name__)


class MachineTypeSchema(Schema):
    """POSTパラメータのvalidation用スキーマ"""

    machine_type_id = fields.Int(required=True)


machine_type_create_schema = MachineTypeSchema()
machine_type_update_schema = MachineTypeSchema()


@machine_types.route("/machine_types", methods=["GET"])
def fetch_machine_types():

    try:
        machine_types = MachineTypeDAO.select_all()
        return jsonify(machine_types), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.READ_FAIL, str(e))
        return jsonify({"message": message}), 500

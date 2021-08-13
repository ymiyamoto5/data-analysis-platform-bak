from typing import Final
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.handler import Handler
from backend.common import common
from backend.common.common_logger import logger  # noqa


def fetch_handler(machine_id: str) -> Handler:
    """DBからmachine_idをkeyにHandler情報を取得する。"""

    app_config_path: str = common.APP_CONFIG_PATH
    DB_URI: Final[str] = common.get_config_value(app_config_path, "SQLALCHEMY_DATABASE_URI")

    engine = create_engine(DB_URI)
    SessionClass = sessionmaker(engine)
    session = SessionClass()
    machine: Machine = session.query(Machine).get(machine_id)

    # NOTE: 1つ目のGW, 1つ目のHandlerを採用。複数GW, 複数Handlerには対応していない。
    # NOTE: machineがない/gatewayがない/handlerがない場合はException
    handler: Handler = machine.gateways[0].handlers[0]

    return handler

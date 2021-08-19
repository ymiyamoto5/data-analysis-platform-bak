from typing import Final, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.gateway import Gateway
from backend.data_collect_manager.models.handler import Handler
from backend.data_collect_manager.models.sensor import Sensor
from backend.common import common
from backend.common.common_logger import logger  # noqa
from sqlalchemy.orm import joinedload


class MachineDAO:
    app_config_path: str = common.APP_CONFIG_PATH
    DB_URI: Final[str] = common.get_config_value(app_config_path, "SQLALCHEMY_DATABASE_URI")

    engine = create_engine(DB_URI)
    SessionClass = sessionmaker(engine)
    session = SessionClass()

    @classmethod
    def fetch_machines(cls) -> List[Machine]:
        """DBからmachineリストを取得する。"""

        machines: List[Machine] = (
            cls.session.query(Machine)
            .options(
                joinedload(Machine.machine_type),
                joinedload(Machine.gateways)
                .joinedload(Gateway.handlers)
                .joinedload(Handler.sensors)
                .joinedload(Sensor.sensor_type),
            )
            .all()
        )

        return machines

    @classmethod
    def fetch_machines_has_handler(cls) -> List[Machine]:
        """DBからHandlerが紐づいている機器を取得する。"""

        machines: List[Machine] = (
            cls.session.query(Machine).join(Gateway, Machine.gateways).join(Handler, Gateway.handlers).all()
        )

        return machines


class HandlerDAO:
    app_config_path: str = common.APP_CONFIG_PATH
    DB_URI: Final[str] = common.get_config_value(app_config_path, "SQLALCHEMY_DATABASE_URI")

    engine = create_engine(DB_URI)
    SessionClass = sessionmaker(engine)
    session = SessionClass()

    @classmethod
    def fetch_handler(cls, machine_id: str) -> Handler:
        """DBからmachine_idをkeyにHandler情報を取得する。"""

        machine: Machine = cls.session.query(Machine).get(machine_id)

        # NOTE: 1つ目のGW, 1つ目のHandlerを採用。複数GW, 複数Handlerには対応していない。
        # NOTE: machineがない/gatewayがない/handlerがない場合はException
        handler: Handler = machine.gateways[0].handlers[0]

        return handler

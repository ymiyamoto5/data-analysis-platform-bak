from typing import List
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.gateway import Gateway
from backend.data_collect_manager.models.handler import Handler
from backend.data_collect_manager.models.sensor import Sensor
from backend.common.dao.create_session import db_session
from backend.common.common_logger import logger  # noqa
from sqlalchemy.orm import joinedload


class MachineDAO:
    @staticmethod
    def select_machines_has_handler() -> List[Machine]:
        """DBからMachine-Gateway-Handlerをinner joinした結果を取得する。"""

        with db_session() as db:
            machines: List[Machine] = (
                db.query(Machine).join(Gateway, Machine.gateways).join(Handler, Gateway.handlers).all()
            )

        return machines

from typing import List

# NOTE: 関連するエンティティをあらかじめimportしておく必要がある。
from backend.data_collect_manager.models.data_collect_history import DataCollectHistory  # noqa
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.gateway import Gateway
from backend.data_collect_manager.models.handler import Handler
from backend.common.dao.create_session import db_session
from backend.common.common_logger import logger  # noqa


class HandlerDAO:
    @staticmethod
    def fetch_handler(machine_id: str) -> Handler:
        """DBからmachine_idをkeyにHandler情報を取得する。"""

        with db_session() as db:
            handlers: List[Handler] = (
                db.query(Handler)
                .join(Gateway, Handler.gateways)
                .join(Machine, Gateway.machines)
                .filter(Machine.machine_id == machine_id)
                .all()
            )

            # NOTE: 1つ目のGW, 1つ目のHandlerを採用。複数GW, 複数Handlerには対応していない。
            # NOTE: handlerがない場合はException
            handler: Handler = handlers[0]

        return handler

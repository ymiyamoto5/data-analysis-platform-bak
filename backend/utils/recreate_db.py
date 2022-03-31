"""
DB再作成
データを再インポートしたい場合等に利用する。
"""

import os
import sys
from typing import Final

# backend配下のモジュールをimportするために、プロジェクト直下へのpathを通す
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from backend.app.db.session import Base, engine

# NOTE: importしておかないとdrop対象として認識されない
from backend.app.models.celery_task import CeleryTask  # noqa
from backend.app.models.data_collect_history import DataCollectHistory  # noqa
from backend.app.models.data_collect_history_event import DataCollectHistoryEvent  # noqa
from backend.app.models.data_collect_history_gateway import DataCollectHistoryGateway  # noqa
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler  # noqa
from backend.app.models.data_collect_history_sensor import DataCollectHistorySensor  # noqa
from backend.app.models.gateway import Gateway  # noqa
from backend.app.models.gateway_event import GatewayEvent  # noqa
from backend.app.models.handler import Handler  # noqa
from backend.app.models.machine import Machine  # noqa
from backend.app.models.machine_type import MachineType  # noqa
from backend.app.models.sensor import Sensor  # noqa
from backend.app.models.sensor_type import SensorType  # noqa
from dotenv import load_dotenv
from sqlalchemy import event

env_file = ".env.local"
load_dotenv(env_file)

DATA_DIR: Final[str] = os.environ["DATA_DIR"]


# NOTE: 外部キー制約無効化
def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute("pragma foreign_keys=OFF")


event.listen(engine, "connect", _fk_pragma_on_connect)

Base.metadata.drop_all(bind=engine)

print("drop DB finished.")

Base.metadata.create_all(bind=engine)

print("recreate finished.")

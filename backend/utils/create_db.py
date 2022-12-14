"""
!!! DBが削除されます !!!
DB再作成スクリプト。alembic適用前環境で利用していたスクリプトのため、非推奨。
通常はalembicによりスキーマを管理し、データ投入はcreate_dummy_data.pyを利用すること。
"""

import os
import sys
from typing import Final

# backend配下のモジュールをimportするために、プロジェクト直下へのpathを通す
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from backend.app.db.session import Base, SessionLocal, engine
from backend.app.models.celery_task import CeleryTask  # noqa
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_event import DataCollectHistoryEvent
from backend.app.models.data_collect_history_gateway import DataCollectHistoryGateway
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
from backend.app.models.data_collect_history_sensor import DataCollectHistorySensor
from backend.app.models.gateway import Gateway
from backend.app.models.gateway_event import GatewayEvent  # noqa
from backend.app.models.handler import Handler
from backend.app.models.machine import Machine
from backend.app.models.machine_type import MachineType
from backend.app.models.sensor import Sensor
from backend.app.models.sensor_type import SensorType
from backend.common import common
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
Base.metadata.create_all(bind=engine)

db = SessionLocal()


# MachineType
machine_type_01 = MachineType(machine_type_name="プレス")
machine_type_02 = MachineType(machine_type_name="圧力プレート")
db.add(machine_type_01)
db.add(machine_type_02)

# SensorType
sensor_type_01 = SensorType(sensor_type_id="load", sensor_type_name="荷重")
sensor_type_02 = SensorType(sensor_type_id="stroke_displacement", sensor_type_name="ストローク変位")
sensor_type_03 = SensorType(sensor_type_id="pulse", sensor_type_name="パルス")
sensor_type_04 = SensorType(sensor_type_id="bolt", sensor_type_name="ボルト")
sensor_type_05 = SensorType(sensor_type_id="displacement", sensor_type_name="変位")
sensor_type_06 = SensorType(sensor_type_id="dummy", sensor_type_name="ダミー")
db.add(sensor_type_01)
db.add(sensor_type_02)
db.add(sensor_type_03)
db.add(sensor_type_04)
db.add(sensor_type_05)
db.add(sensor_type_06)

# ローカルテスト用（複数ハンドラー）
machine_01 = Machine(
    machine_id="unittest-machine-01",
    machine_name="ユニットテスト機器(複数ハンドラー)",
    collect_status=common.COLLECT_STATUS.RECORDED.value,
    machine_type_id=1,
    auto_cut_out_shot=False,
    start_displacement=None,
    end_displacement=None,
    margin=None,
    threshold=None,
    auto_predict=False,
    predict_model=None,
    model_version=None,
    gateways=[
        Gateway(
            gateway_id="unittest-gateway-01",
            sequence_number=1,
            gateway_result=0,
            status=common.STATUS.STOP.value,
            log_level=5,
            handlers=[
                Handler(
                    handler_id="unittest-handler-01-1",
                    handler_type="USB-204",
                    adc_serial_num="00002222",
                    sampling_frequency=100,
                    sampling_ch_num=3,
                    filewrite_time=1,
                    is_primary=True,
                    is_cut_out_target=True,
                    is_multi=True,
                    sensors=[
                        Sensor(
                            machine_id="unittest-machine-01",
                            sensor_id="stroke_displacement",
                            sensor_name="stroke_displacement",
                            sensor_type_id="stroke_displacement",
                            slope=1.0,
                            intercept=0.0,
                            sort_order=0,
                        ),
                        Sensor(
                            machine_id="unittest-machine-01",
                            sensor_id="load01",
                            sensor_name="load01",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                            start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                            max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                            break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            sort_order=1,
                        ),
                        Sensor(
                            machine_id="unittest-machine-01",
                            sensor_id="load02",
                            sensor_name="load02",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                            start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                            max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                            break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            sort_order=2,
                        ),
                    ],
                ),
                Handler(
                    handler_id="unittest-handler-01-2",
                    handler_type="USB-204",
                    adc_serial_num="00003333",
                    sampling_frequency=100,
                    sampling_ch_num=3,
                    filewrite_time=1,
                    is_primary=False,
                    is_cut_out_target=True,
                    is_multi=True,
                    sensors=[
                        Sensor(
                            machine_id="unittest-machine-01",
                            sensor_id="load03",
                            sensor_name="load03",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                            start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                            max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                            break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            sort_order=3,
                        ),
                        Sensor(
                            machine_id="unittest-machine-01",
                            sensor_id="load04",
                            sensor_name="load04",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                            start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                            max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                            break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            sort_order=4,
                        ),
                        Sensor(
                            machine_id="unittest-machine-01",
                            sensor_id="dummy01",
                            sensor_name="dummy01",
                            sensor_type_id="dummy",
                            slope=1.0,
                            intercept=0.0,
                            sort_order=5,
                        ),
                    ],
                ),
            ],
        )
    ],
)
db.add(machine_01)

# ローカルテスト用（単一ハンドラー）
machine_02 = Machine(
    machine_id="unittest-machine-02",
    machine_name="ユニットテスト機器(単一ハンドラー)",
    collect_status=common.COLLECT_STATUS.RECORDED.value,
    machine_type_id=1,
    auto_cut_out_shot=False,
    start_displacement=None,
    end_displacement=None,
    margin=None,
    threshold=None,
    auto_predict=False,
    predict_model=None,
    model_version=None,
    gateways=[
        Gateway(
            gateway_id="unittest-gateway-02",
            sequence_number=1,
            gateway_result=0,
            status=common.STATUS.STOP.value,
            log_level=5,
            handlers=[
                Handler(
                    handler_id="unittest-handler-02",
                    handler_type="USB-1608HS",
                    adc_serial_num="00002222",
                    sampling_frequency=100,
                    sampling_ch_num=3,
                    filewrite_time=1,
                    is_primary=False,
                    is_cut_out_target=True,
                    is_multi=False,
                    sensors=[
                        Sensor(
                            machine_id="unittest-machine-02",
                            sensor_id="stroke_displacement",
                            sensor_name="stroke_displacement",
                            sensor_type_id="stroke_displacement",
                            slope=1.0,
                            intercept=0.0,
                            sort_order=0,
                        ),
                        Sensor(
                            machine_id="unittest-machine-02",
                            sensor_id="load01",
                            sensor_name="load01",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                            start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                            max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                            break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            sort_order=1,
                        ),
                        Sensor(
                            machine_id="unittest-machine-02",
                            sensor_id="load02",
                            sensor_name="load02",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                            start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                            max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                            break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            sort_order=2,
                        ),
                        Sensor(
                            machine_id="unittest-machine-02",
                            sensor_id="load03",
                            sensor_name="load03",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                            start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                            max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                            break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            sort_order=3,
                        ),
                        Sensor(
                            machine_id="unittest-machine-02",
                            sensor_id="load04",
                            sensor_name="load04",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                            start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                            max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                            break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            sort_order=4,
                        ),
                    ],
                ),
            ],
        )
    ],
)
db.add(machine_02)

# 結合テスト用（複数ハンドラー）
integ_test_machine = Machine(
    machine_id="test-machine",
    machine_name="結合テスト機器(複数ハンドラー)",
    collect_status=common.COLLECT_STATUS.RECORDED.value,
    machine_type_id=1,
    auto_cut_out_shot=False,
    start_displacement=None,
    end_displacement=None,
    margin=None,
    threshold=None,
    auto_predict=False,
    predict_model=None,
    model_version=None,
    gateways=[
        Gateway(
            gateway_id="test-GW",
            sequence_number=1,
            gateway_result=0,
            status=common.STATUS.STOP.value,
            log_level=5,
            handlers=[
                Handler(
                    handler_id="test-handler-1",
                    handler_type="USB-204",
                    adc_serial_num="01ED23FA",
                    sampling_frequency=1000,
                    sampling_ch_num=3,
                    filewrite_time=1,
                    is_primary=True,
                    is_cut_out_target=True,
                    is_multi=True,
                    sensors=[
                        Sensor(
                            machine_id="test-machine",
                            sensor_id="stroke_displacement",
                            sensor_name="変位センサー",
                            sensor_type_id="stroke_displacement",
                            slope=1.0,
                            intercept=0.0,
                            sort_order=0,
                        ),
                        Sensor(
                            machine_id="test-machine",
                            sensor_id="load01",
                            sensor_name="荷重センサー01",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                            start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                            max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                            break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            sort_order=1,
                        ),
                        Sensor(
                            machine_id="test-machine",
                            sensor_id="load02",
                            sensor_name="荷重センサー02",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                            start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                            max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                            break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            sort_order=2,
                        ),
                    ],
                ),
                Handler(
                    handler_id="test-handler-2",
                    handler_type="USB-204",
                    adc_serial_num="01E42EF8",
                    sampling_frequency=1000,
                    sampling_ch_num=3,
                    filewrite_time=1,
                    is_primary=False,
                    is_cut_out_target=True,
                    is_multi=True,
                    sensors=[
                        Sensor(
                            machine_id="test-machine",
                            sensor_id="load03",
                            sensor_name="荷重センサー03",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                            start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                            max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                            break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            sort_order=3,
                        ),
                        Sensor(
                            machine_id="test-machine",
                            sensor_id="load04",
                            sensor_name="荷重センサー04",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                            start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                            max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                            break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            sort_order=4,
                        ),
                        Sensor(
                            machine_id="test-machine",
                            sensor_id="dummy01",
                            sensor_name="ダミーセンサー",
                            sensor_type_id="dummy",
                            slope=1.0,
                            intercept=0.0,
                            sort_order=5,
                        ),
                    ],
                ),
            ],
        )
    ],
)
db.add(integ_test_machine)

# demo_started_at = datetime(2021, 7, 9, 19, 0, 0, 0)

# data_collect_history_demo = DataCollectHistory(
#     machine_id="machine-01",
#     machine_name="デモ用プレス機",
#     machine_type_id=1,
#     started_at=demo_started_at + timedelta(hours=-9),
#     ended_at=demo_started_at + timedelta(hours=-9) + timedelta(hours=1),
#     processed_dir_path=os.path.join(DATA_DIR, "machine-01-20210709190000"),
#     data_collect_history_events=[
#         DataCollectHistoryEvent(
#             event_id=0,
#             event_name=common.COLLECT_STATUS.SETUP.value,
#             occurred_at=demo_started_at + timedelta(hours=-9),
#         ),
#         DataCollectHistoryEvent(
#             event_id=1,
#             event_name=common.COLLECT_STATUS.START.value,
#             occurred_at=demo_started_at + timedelta(hours=-9),
#         ),
#         DataCollectHistoryEvent(
#             event_id=2,
#             event_name=common.COLLECT_STATUS.STOP.value,
#             occurred_at=demo_started_at + timedelta(hours=-9) + timedelta(minutes=120),
#         ),
#         DataCollectHistoryEvent(
#             event_id=3,
#             event_name=common.COLLECT_STATUS.RECORDED.value,
#             occurred_at=demo_started_at + timedelta(hours=-9) + timedelta(minutes=121),
#         ),
#     ],
#     data_collect_history_gateways=[
#         DataCollectHistoryGateway(
#             gateway_id="gw-01",
#             log_level=5,
#             data_collect_history_handlers=[
#                 DataCollectHistoryHandler(
#                     data_collect_history_id=1,
#                     handler_id="handler-01",
#                     handler_type="USB-1608HS",
#                     adc_serial_num="00002222",
#                     sampling_frequency=100,
#                     sampling_ch_num=3,
#                     filewrite_time=1,
#                     is_cut_out_target=True,
#                     data_collect_history_sensors=[
#                         DataCollectHistorySensor(
#                             data_collect_history_id=1,
#                             sensor_id="stroke_displacement",
#                             sensor_name="stroke_displacement",
#                             sensor_type_id="stroke_displacement",
#                             slope=1.0,
#                             intercept=0.0,
#                         ),
#                         DataCollectHistorySensor(
#                             data_collect_history_id=1,
#                             sensor_id="load01",
#                             sensor_name="load01",
#                             sensor_type_id="load",
#                             slope=1.0,
#                             intercept=0.0,
#                             start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
#                             max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
#                             break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
#                         ),
#                         DataCollectHistorySensor(
#                             data_collect_history_id=1,
#                             sensor_id="load02",
#                             sensor_name="load02",
#                             sensor_type_id="load",
#                             slope=1.0,
#                             intercept=0.0,
#                             start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
#                             max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
#                             break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
#                         ),
#                     ],
#                 ),
#                 DataCollectHistoryHandler(
#                     data_collect_history_id=1,
#                     handler_id="handler-02",
#                     handler_type="USB-1608HS",
#                     adc_serial_num="00003333",
#                     sampling_frequency=100,
#                     sampling_ch_num=2,
#                     filewrite_time=1,
#                     is_cut_out_target=True,
#                     data_collect_history_sensors=[
#                         DataCollectHistorySensor(
#                             data_collect_history_id=1,
#                             sensor_id="load03",
#                             sensor_name="load03",
#                             sensor_type_id="load",
#                             slope=1.0,
#                             intercept=0.0,
#                             start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
#                             max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
#                             break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
#                         ),
#                         DataCollectHistorySensor(
#                             data_collect_history_id=1,
#                             sensor_id="load04",
#                             sensor_name="load04",
#                             sensor_type_id="load",
#                             slope=1.0,
#                             intercept=0.0,
#                             start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
#                             max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
#                             break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
#                         ),
#                     ],
#                 ),
#             ],
#         )
#     ],
# )
# db.add(data_collect_history_demo)

# machine_j = Machine(
#     machine_id="machine-j",
#     machine_name="デモ用プレス機",
#     collect_status=common.COLLECT_STATUS.RECORDED.value,
#     machine_type_id=1,
#     auto_cut_out_shot=False,
#     start_displacement=None,
#     end_displacement=None,
#     margin=None,
#     threshold=None,
#     auto_predict=False,
#     predict_model=None,
#     model_version=None,
#     gateways=[
#         Gateway(
#             gateway_id="GW-j",
#             sequence_number=1,
#             gateway_result=0,
#             status=common.STATUS.STOP.value,
#             log_level=5,
#             handlers=[
#                 Handler(
#                     handler_id="handler-j",
#                     handler_type="USB-1608HS",
#                     adc_serial_num="00002222",
#                     sampling_frequency=100000,
#                     sampling_ch_num=2,
#                     filewrite_time=1,
#                     sensors=[
#                         Sensor(
#                             machine_id="machine-j",
#                             sensor_id="stroke_displacement",
#                             sensor_name="stroke_displacement",
#                             sensor_type_id="stroke_displacement",
#                             slope=1.0,
#                             intercept=0.0,
#                             start_point_dsl=None,
#                             max_point_dsl=None,
#                             break_point_dsl=None,
#                         ),
#                         Sensor(
#                             machine_id="machine-j",
#                             sensor_id="load01",
#                             sensor_name="歪み",
#                             sensor_type_id="load",
#                             slope=1.0,
#                             intercept=0.0,
#                             start_point_dsl=None,
#                             max_point_dsl=None,
#                             break_point_dsl=None,
#                         ),
#                     ],
#                 ),
#             ],
#         )
#     ],
# )
# db.add(machine_j)

# j_started_at_1 = datetime(2021, 8, 1, 9, 40, 30, 0)

# data_collect_history_j_1 = DataCollectHistory(
#     machine_id="machine-j",
#     machine_name="デモ用プレス機",
#     machine_type_id=1,
#     started_at=j_started_at_1 + timedelta(hours=-9),
#     ended_at=j_started_at_1 + timedelta(hours=-9) + timedelta(hours=1),
#     sampling_frequency=100000,
#     sampling_ch_num=2,
#     processed_dir_path="/mnt/datadrive/data/machine-j-20210801094030",
#     sample_count=0,
#     data_collect_history_events=[
#         DataCollectHistoryEvent(
#             event_id=0,
#             event_name=common.COLLECT_STATUS.SETUP.value,
#             occurred_at=j_started_at_1 + timedelta(hours=-9),
#         ),
#         DataCollectHistoryEvent(
#             event_id=1,
#             event_name=common.COLLECT_STATUS.START.value,
#             occurred_at=j_started_at_1 + timedelta(hours=-9),
#         ),
#         DataCollectHistoryEvent(
#             event_id=2,
#             event_name=common.COLLECT_STATUS.STOP.value,
#             occurred_at=j_started_at_1 + timedelta(hours=-9) + timedelta(minutes=120),
#         ),
#         DataCollectHistoryEvent(
#             event_id=3,
#             event_name=common.COLLECT_STATUS.RECORDED.value,
#             occurred_at=j_started_at_1 + timedelta(hours=-9) + timedelta(minutes=121),
#         ),
#     ],
#     data_collect_history_sensors=[
#         DataCollectHistorySensor(
#             sensor_id="stroke_displacement",
#             sensor_name="ストローク変位",
#             sensor_type_id="stroke_displacement",
#             slope=1.0,
#             intercept=0.0,
#         ),
#         DataCollectHistorySensor(
#             sensor_id="load01",
#             sensor_name="歪み",
#             sensor_type_id="load",
#             slope=1.0,
#             intercept=0.0,
#         ),
#     ],
# )
# db.add(data_collect_history_j_1)

# j_started_at_2 = datetime(2021, 10, 9, 15, 56, 26, 0)

# data_collect_history_j_2 = DataCollectHistory(
#     machine_id="machine-j",
#     machine_name="デモ用プレス機",
#     machine_type_id=1,
#     started_at=j_started_at_2 + timedelta(hours=-9),
#     ended_at=j_started_at_2 + timedelta(hours=-9) + timedelta(hours=1),
#     sampling_frequency=100000,
#     sampling_ch_num=2,
#     processed_dir_path=os.path.join(DATA_DIR, "machine-j-20211009155626"),
#     sample_count=0,
#     data_collect_history_events=[
#         DataCollectHistoryEvent(
#             event_id=0,
#             event_name=common.COLLECT_STATUS.SETUP.value,
#             occurred_at=j_started_at_2 + timedelta(hours=-9),
#         ),
#         DataCollectHistoryEvent(
#             event_id=1,
#             event_name=common.COLLECT_STATUS.START.value,
#             occurred_at=j_started_at_2 + timedelta(hours=-9),
#         ),
#         DataCollectHistoryEvent(
#             event_id=2,
#             event_name=common.COLLECT_STATUS.STOP.value,
#             occurred_at=j_started_at_2 + timedelta(hours=-9) + timedelta(minutes=120),
#         ),
#         DataCollectHistoryEvent(
#             event_id=3,
#             event_name=common.COLLECT_STATUS.RECORDED.value,
#             occurred_at=j_started_at_2 + timedelta(hours=-9) + timedelta(minutes=121),
#         ),
#     ],
#     data_collect_history_sensors=[
#         DataCollectHistorySensor(
#             sensor_id="stroke_displacement",
#             sensor_name="ストローク変位",
#             sensor_type_id="stroke_displacement",
#             slope=1.0,
#             intercept=0.0,
#         ),
#         DataCollectHistorySensor(
#             sensor_id="load01",
#             sensor_name="歪み",
#             sensor_type_id="load",
#             slope=1.0,
#             intercept=0.0,
#         ),
#     ],
# )
# db.add(data_collect_history_j_2)

db.commit()

[print(vars(x)) for x in db.query(MachineType).all()]  # type: ignore
[print(vars(x)) for x in db.query(Machine).all()]  # type: ignore
[print(vars(x)) for x in db.query(Gateway).all()]  # type: ignore
[print(vars(x)) for x in db.query(Handler).all()]  # type: ignore
[print(vars(x)) for x in db.query(Sensor).all()]  # type: ignore
[print(vars(x)) for x in db.query(SensorType).all()]  # type: ignore
[print(vars(x)) for x in db.query(DataCollectHistory).all()]  # type: ignore
[print(vars(x)) for x in db.query(DataCollectHistoryGateway).all()]  # type: ignore
[print(vars(x)) for x in db.query(DataCollectHistoryHandler).all()]  # type: ignore
[print(vars(x)) for x in db.query(DataCollectHistorySensor).all()]  # type: ignore
[print(vars(x)) for x in db.query(DataCollectHistoryEvent).all()]  # type: ignore

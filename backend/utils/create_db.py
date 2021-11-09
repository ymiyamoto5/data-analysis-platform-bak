import os
import sys
from datetime import datetime, timedelta

# backend配下のモジュールをimportするために、プロジェクト直下へのpathを通す
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from backend.app.db.session import Base, SessionLocal, engine
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_detail import DataCollectHistoryDetail
from backend.app.models.data_collect_history_event import DataCollectHistoryEvent
from backend.app.models.gateway import Gateway
from backend.app.models.handler import Handler
from backend.app.models.machine import Machine
from backend.app.models.machine_type import MachineType
from backend.app.models.sensor import Sensor
from backend.app.models.sensor_type import SensorType
from backend.common import common
from sqlalchemy import event


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
sensor_type_04 = SensorType(sensor_type_id="volt", sensor_type_name="ボルト")
sensor_type_05 = SensorType(sensor_type_id="displacement", sensor_type_name="変位")
db.add(sensor_type_01)
db.add(sensor_type_02)
db.add(sensor_type_03)
db.add(sensor_type_04)
db.add(sensor_type_05)

# H社用
# machine_01 = Machine(
#     machine_id="machine-01",
#     machine_name="テストプレス01",
#     collect_status=common.COLLECT_STATUS.RECORDED.value,
#     machine_type_id=1,
#     gateways=[
#         Gateway(
#             gateway_id="GW-01",
#             sequence_number=1,
#             gateway_result=0,
#             status=common.STATUS.STOP.value,
#             log_level=5,
#             handlers=[
#                 Handler(
#                     handler_id="AD-USB-1608",
#                     handler_type="USB_1608HS",
#                     adc_serial_num="00001111",
#                     sampling_frequency=100000,
#                     sampling_ch_num=5,
#                     filewrite_time=1,
#                     sensors=[
#                         Sensor(
#                             machine_id="machine-01",
#                             sensor_id="stroke_displacement",
#                             sensor_name="stroke_displacement",
#                             sensor_type_id="stroke_displacement",
#                             slope=1.0,
#                             intercept=0.0,
#                         ),
#                         Sensor(
#                             machine_id="machine-01",
#                             sensor_id="load01",
#                             sensor_name="load01",
#                             sensor_type_id="load",
#                             slope=1.0,
#                             intercept=0.0,
#                         ),
#                         Sensor(
#                             machine_id="machine-01",
#                             sensor_id="load02",
#                             sensor_name="load02",
#                             sensor_type_id="load",
#                             slope=1.0,
#                             intercept=0.0,
#                         ),
#                         Sensor(
#                             machine_id="machine-01",
#                             sensor_id="load03",
#                             sensor_name="load03",
#                             sensor_type_id="load",
#                             slope=1.0,
#                             intercept=0.0,
#                         ),
#                         Sensor(
#                             machine_id="machine-01",
#                             sensor_id="load04",
#                             sensor_name="load04",
#                             sensor_type_id="load",
#                             slope=1.0,
#                             intercept=0.0,
#                         ),
#                     ],
#                 )
#             ],
#         )
#     ],
# )
# db.add(machine_01)

# data_collect_history_01 = DataCollectHistory(
#     machine_id="machine-01",
#     machine_name="テストプレス01",
#     machine_type_id=1,
#     started_at=datetime(2021, 3, 27, 14, 15, 14, 0) + timedelta(hours=-9),
#     ended_at=datetime(2021, 3, 27, 14, 15, 14, 0) + timedelta(hours=-9) + timedelta(hours=1),
#     sampling_frequency=100000,
#     sampling_ch_num=5,
#     sample_count=0,
#     data_collect_history_events=[
#         DataCollectHistoryEvent(
#             event_id=0,
#             event_name=common.COLLECT_STATUS.SETUP.value,
#             occurred_at=datetime(2021, 3, 27, 14, 15, 14, 0) + timedelta(hours=-9),
#         ),
#         DataCollectHistoryEvent(
#             event_id=1,
#             event_name=common.COLLECT_STATUS.START.value,
#             occurred_at=datetime(2021, 3, 27, 14, 15, 14, 0) + timedelta(hours=-9),
#         ),
#         DataCollectHistoryEvent(
#             event_id=2,
#             event_name=common.COLLECT_STATUS.STOP.value,
#             occurred_at=datetime(2021, 3, 27, 14, 15, 14, 0) + timedelta(hours=-9) + timedelta(minutes=120),
#         ),
#         DataCollectHistoryEvent(
#             event_id=3,
#             event_name=common.COLLECT_STATUS.RECORDED.value,
#             occurred_at=datetime(2021, 3, 27, 14, 15, 14, 0) + timedelta(hours=-9) + timedelta(minutes=120),
#         ),
#     ],
#     data_collect_history_details=[
#         DataCollectHistoryDetail(
#             sensor_id="stroke_displacement",
#             sensor_name="ストローク変位",
#             sensor_type_id="stroke_displacement",
#             slope=1.0,
#             intercept=0.0,
#         ),
#         DataCollectHistoryDetail(
#             sensor_id="load01",
#             sensor_name="荷重01",
#             sensor_type_id="load",
#             slope=1.0,
#             intercept=0.0,
#         ),
#         DataCollectHistoryDetail(
#             sensor_id="load02",
#             sensor_name="荷重02",
#             sensor_type_id="load",
#             slope=1.0,
#             intercept=0.0,
#         ),
#         DataCollectHistoryDetail(
#             sensor_id="load03",
#             sensor_name="荷重03",
#             sensor_type_id="load",
#             slope=1.0,
#             intercept=0.0,
#         ),
#         DataCollectHistoryDetail(
#             sensor_id="load04",
#             sensor_name="荷重04",
#             sensor_type_id="load",
#             slope=1.0,
#             intercept=0.0,
#         ),
#     ],
# )
# db.add(data_collect_history_01)

# 結合テスト用
test_machine = Machine(
    machine_id="test-machine",
    machine_name="結合テスト用",
    collect_status=common.COLLECT_STATUS.RECORDED.value,
    machine_type_id=1,
    gateways=[
        Gateway(
            gateway_id="test-GW",
            sequence_number=1,
            gateway_result=0,
            status=common.STATUS.STOP.value,
            log_level=5,
            handlers=[
                Handler(
                    handler_id="test-handler",
                    handler_type="USB_1608HS",
                    adc_serial_num="01ED23FA",
                    sampling_frequency=100000,
                    sampling_ch_num=5,
                    filewrite_time=10,
                    sensors=[
                        Sensor(
                            machine_id="test-machine",
                            sensor_id="stroke_displacement",
                            sensor_name="stroke_displacement",
                            sensor_type_id="stroke_displacement",
                            slope=1.0,
                            intercept=0.0,
                        ),
                        Sensor(
                            machine_id="test-machine",
                            sensor_id="load01",
                            sensor_name="load01",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                        ),
                        Sensor(
                            machine_id="test-machine",
                            sensor_id="load02",
                            sensor_name="load02",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                        ),
                        Sensor(
                            machine_id="test-machine",
                            sensor_id="load03",
                            sensor_name="load03",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                        ),
                        Sensor(
                            machine_id="test-machine",
                            sensor_id="load04",
                            sensor_name="load04",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                        ),
                    ],
                )
            ],
        )
    ],
)

db.add(test_machine)

# デモシナリオ（刃がなまるシナリオ）
machine_01 = Machine(
    machine_id="machine-01",
    machine_name="デモ用プレス機",
    collect_status=common.COLLECT_STATUS.RECORDED.value,
    machine_type_id=1,
    gateways=[
        Gateway(
            gateway_id="gw-01",
            sequence_number=1,
            gateway_result=0,
            status=common.STATUS.STOP.value,
            log_level=5,
            handlers=[
                Handler(
                    handler_id="handler-01",
                    handler_type="USB_1608HS",
                    adc_serial_num="00002222",
                    sampling_frequency=100000,
                    sampling_ch_num=3,
                    filewrite_time=1,
                    sensors=[
                        Sensor(
                            machine_id="machine-01",
                            sensor_id="stroke_displacement",
                            sensor_name="stroke_displacement",
                            sensor_type_id="stroke_displacement",
                            slope=1.0,
                            intercept=0.0,
                        ),
                        Sensor(
                            machine_id="machine-01",
                            sensor_id="load01",
                            sensor_name="load01",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                        ),
                        Sensor(
                            machine_id="machine-01",
                            sensor_id="load02",
                            sensor_name="load02",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                        ),
                    ],
                ),
                Handler(
                    handler_id="handler-02",
                    handler_type="USB_1608HS",
                    adc_serial_num="00003333",
                    sampling_frequency=100000,
                    sampling_ch_num=2,
                    filewrite_time=1,
                    sensors=[
                        Sensor(
                            machine_id="machine-01",
                            sensor_id="load03",
                            sensor_name="load03",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                        ),
                        Sensor(
                            machine_id="machine-01",
                            sensor_id="load04",
                            sensor_name="load04",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                        ),
                    ],
                ),
            ],
        )
    ],
)
db.add(machine_01)

demo_started_at = datetime(2021, 7, 9, 19, 0, 0, 0)

data_collect_history_demo = DataCollectHistory(
    machine_id="machine-01",
    machine_name="デモ用プレス機",
    machine_type_id=1,
    started_at=demo_started_at + timedelta(hours=-9),
    ended_at=demo_started_at + timedelta(hours=-9) + timedelta(hours=1),
    sampling_frequency=100000,
    sampling_ch_num=5,
    sample_count=0,
    data_collect_history_events=[
        DataCollectHistoryEvent(
            event_id=0,
            event_name=common.COLLECT_STATUS.SETUP.value,
            occurred_at=demo_started_at + timedelta(hours=-9),
        ),
        DataCollectHistoryEvent(
            event_id=1,
            event_name=common.COLLECT_STATUS.START.value,
            occurred_at=demo_started_at + timedelta(hours=-9),
        ),
        DataCollectHistoryEvent(
            event_id=2,
            event_name=common.COLLECT_STATUS.STOP.value,
            occurred_at=demo_started_at + timedelta(hours=-9) + timedelta(minutes=120),
        ),
        DataCollectHistoryEvent(
            event_id=3,
            event_name=common.COLLECT_STATUS.RECORDED.value,
            occurred_at=demo_started_at + timedelta(hours=-9) + timedelta(minutes=121),
        ),
    ],
    data_collect_history_details=[
        DataCollectHistoryDetail(
            sensor_id="stroke_displacement",
            sensor_name="ストローク変位",
            sensor_type_id="stroke_displacement",
            slope=1.0,
            intercept=0.0,
        ),
        DataCollectHistoryDetail(
            sensor_id="load01",
            sensor_name="荷重01",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
        DataCollectHistoryDetail(
            sensor_id="load02",
            sensor_name="荷重02",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
        DataCollectHistoryDetail(
            sensor_id="load03",
            sensor_name="荷重03",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
        DataCollectHistoryDetail(
            sensor_id="load04",
            sensor_name="荷重04",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
    ],
)
db.add(data_collect_history_demo)

machine_j = Machine(
    machine_id="machine-j",
    machine_name="デモ用プレス機",
    collect_status=common.COLLECT_STATUS.RECORDED.value,
    machine_type_id=1,
    gateways=[
        Gateway(
            gateway_id="GW-j",
            sequence_number=1,
            gateway_result=0,
            status=common.STATUS.STOP.value,
            log_level=5,
            handlers=[
                Handler(
                    handler_id="handler-j",
                    handler_type="USB_1608HS",
                    adc_serial_num="00002222",
                    sampling_frequency=100000,
                    sampling_ch_num=2,
                    filewrite_time=1,
                    sensors=[
                        Sensor(
                            machine_id="machine-j",
                            sensor_id="stroke_displacement",
                            sensor_name="stroke_displacement",
                            sensor_type_id="stroke_displacement",
                            slope=1.0,
                            intercept=0.0,
                        ),
                        Sensor(
                            machine_id="machine-j",
                            sensor_id="load01",
                            sensor_name="歪み",
                            sensor_type_id="load",
                            slope=1.0,
                            intercept=0.0,
                        ),
                    ],
                ),
            ],
        )
    ],
)
db.add(machine_j)

j_started_at_1 = datetime(2021, 8, 1, 9, 40, 30, 0)

data_collect_history_j_1 = DataCollectHistory(
    machine_id="machine-j",
    machine_name="デモ用プレス機",
    machine_type_id=1,
    started_at=j_started_at_1 + timedelta(hours=-9),
    ended_at=j_started_at_1 + timedelta(hours=-9) + timedelta(hours=1),
    sampling_frequency=100000,
    sampling_ch_num=2,
    sample_count=0,
    data_collect_history_events=[
        DataCollectHistoryEvent(
            event_id=0,
            event_name=common.COLLECT_STATUS.SETUP.value,
            occurred_at=j_started_at_1 + timedelta(hours=-9),
        ),
        DataCollectHistoryEvent(
            event_id=1,
            event_name=common.COLLECT_STATUS.START.value,
            occurred_at=j_started_at_1 + timedelta(hours=-9),
        ),
        DataCollectHistoryEvent(
            event_id=2,
            event_name=common.COLLECT_STATUS.STOP.value,
            occurred_at=j_started_at_1 + timedelta(hours=-9) + timedelta(minutes=120),
        ),
        DataCollectHistoryEvent(
            event_id=3,
            event_name=common.COLLECT_STATUS.RECORDED.value,
            occurred_at=j_started_at_1 + timedelta(hours=-9) + timedelta(minutes=121),
        ),
    ],
    data_collect_history_details=[
        DataCollectHistoryDetail(
            sensor_id="stroke_displacement",
            sensor_name="ストローク変位",
            sensor_type_id="stroke_displacement",
            slope=1.0,
            intercept=0.0,
        ),
        DataCollectHistoryDetail(
            sensor_id="load01",
            sensor_name="歪み",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
    ],
)
db.add(data_collect_history_j_1)

j_started_at_2 = datetime(2021, 10, 9, 15, 56, 26, 0)

data_collect_history_j_2 = DataCollectHistory(
    machine_id="machine-j",
    machine_name="デモ用プレス機",
    machine_type_id=1,
    started_at=j_started_at_2 + timedelta(hours=-9),
    ended_at=j_started_at_2 + timedelta(hours=-9) + timedelta(hours=1),
    sampling_frequency=100000,
    sampling_ch_num=2,
    sample_count=0,
    data_collect_history_events=[
        DataCollectHistoryEvent(
            event_id=0,
            event_name=common.COLLECT_STATUS.SETUP.value,
            occurred_at=j_started_at_2 + timedelta(hours=-9),
        ),
        DataCollectHistoryEvent(
            event_id=1,
            event_name=common.COLLECT_STATUS.START.value,
            occurred_at=j_started_at_2 + timedelta(hours=-9),
        ),
        DataCollectHistoryEvent(
            event_id=2,
            event_name=common.COLLECT_STATUS.STOP.value,
            occurred_at=j_started_at_2 + timedelta(hours=-9) + timedelta(minutes=120),
        ),
        DataCollectHistoryEvent(
            event_id=3,
            event_name=common.COLLECT_STATUS.RECORDED.value,
            occurred_at=j_started_at_2 + timedelta(hours=-9) + timedelta(minutes=121),
        ),
    ],
    data_collect_history_details=[
        DataCollectHistoryDetail(
            sensor_id="stroke_displacement",
            sensor_name="ストローク変位",
            sensor_type_id="stroke_displacement",
            slope=1.0,
            intercept=0.0,
        ),
        DataCollectHistoryDetail(
            sensor_id="load01",
            sensor_name="歪み",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
    ],
)
db.add(data_collect_history_j_2)

db.commit()

[print(vars(x)) for x in db.query(MachineType).all()]  # type: ignore
[print(vars(x)) for x in db.query(Machine).all()]  # type: ignore
[print(vars(x)) for x in db.query(Gateway).all()]  # type: ignore
[print(vars(x)) for x in db.query(Handler).all()]  # type: ignore
[print(vars(x)) for x in db.query(Sensor).all()]  # type: ignore
[print(vars(x)) for x in db.query(SensorType).all()]  # type: ignore
[print(vars(x)) for x in db.query(DataCollectHistory).all()]  # type: ignore
[print(vars(x)) for x in db.query(DataCollectHistoryDetail).all()]  # type: ignore
[print(vars(x)) for x in db.query(DataCollectHistoryEvent).all()]  # type: ignore

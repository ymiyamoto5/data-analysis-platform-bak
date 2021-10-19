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

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# MachineType
machine_type_01 = MachineType(machine_type_name="プレス")
machine_type_02 = MachineType(machine_type_name="圧力プレート")

# SensorType
sensor_type_01 = SensorType(sensor_type_id="load", sensor_type_name="荷重")
sensor_type_02 = SensorType(sensor_type_id="stroke_displacement", sensor_type_name="ストローク変位")
sensor_type_03 = SensorType(sensor_type_id="pulse", sensor_type_name="パルス")
sensor_type_04 = SensorType(sensor_type_id="volt", sensor_type_name="ボルト")
sensor_type_05 = SensorType(sensor_type_id="displacement", sensor_type_name="変位")


# Machine
machine_01 = Machine(
    machine_id="machine-01",
    machine_name="テストプレス01",
    collect_status=common.COLLECT_STATUS.RECORDED.value,
    machine_type_id=1,
)
machine_02 = Machine(
    machine_id="machine-02",
    machine_name="テストプレス02",
    collect_status=common.COLLECT_STATUS.RECORDED.value,
    machine_type_id=1,
)
machine_03 = Machine(
    machine_id="machine-03",
    machine_name="テスト圧力プレート01",
    collect_status=common.COLLECT_STATUS.RECORDED.value,
    machine_type_id=2,
)
demo_machine = Machine(
    machine_id="demo-machine",
    machine_name="デモ用プレス機",
    collect_status=common.COLLECT_STATUS.RECORDED.value,
    machine_type_id=1,
)
machine_j = Machine(
    machine_id="machine-j",
    machine_name="プレス機J",
    collect_status=common.COLLECT_STATUS.RECORDED.value,
    machine_type_id=1,
)

# Gateway
gateway_01 = Gateway(
    gateway_id="GW-01",
    sequence_number=6,
    gateway_result=0,
    status=common.STATUS.STOP.value,
    log_level=5,
)
gateway_02 = Gateway(
    gateway_id="GW-02",
    sequence_number=3,
    gateway_result=0,
    status=common.STATUS.STOP.value,
    log_level=5,
)
gateway_03 = Gateway(
    gateway_id="GW-03",
    sequence_number=3,
    gateway_result=0,
    status=common.STATUS.STOP.value,
    log_level=5,
)
demo_gateway = Gateway(
    gateway_id="demo-GW",
    sequence_number=0,
    gateway_result=1,
    status=common.STATUS.STOP.value,
    log_level=5,
)
gateway_j = Gateway(
    gateway_id="GW-j",
    sequence_number=0,
    gateway_result=1,
    status=common.STATUS.STOP.value,
    log_level=5,
)

# Handler
handler_01 = Handler(
    handler_id="AD-USB-1608",
    handler_type="USB_1608HS",
    adc_serial_num="01F3D39C",
    sampling_frequency=100000,
    sampling_ch_num=5,
    filewrite_time=1,
)
handler_02 = Handler(
    handler_id="AD-USB-xxxx",
    handler_type="USB_xxxxHS",
    adc_serial_num="ZZZZZZZ",
    sampling_frequency=1000,
    sampling_ch_num=2,
    filewrite_time=1,
)
handler_03 = Handler(
    handler_id="AD-USB-yyy1",
    handler_type="USB_yyyyHS",
    adc_serial_num="YYYYYYY1",
    sampling_frequency=1000,
    sampling_ch_num=16,
    filewrite_time=1,
)
demo_handler = Handler(
    handler_id="demo-handler",
    handler_type="USB",
    adc_serial_num="sample",
    sampling_frequency=100000,
    sampling_ch_num=2,
    filewrite_time=1,
)
handler_j = Handler(
    handler_id="handler-j",
    handler_type="USB",
    adc_serial_num="sample-j",
    sampling_frequency=10000,
    sampling_ch_num=2,
    filewrite_time=1,
)

# Sensor
sensor_01 = Sensor(
    machine_id="machine-01",
    sensor_id="load01",
    sensor_name="load01",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_02 = Sensor(
    machine_id="machine-01",
    sensor_id="load02",
    sensor_name="load02",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_03 = Sensor(
    machine_id="machine-01",
    sensor_id="stroke_displacement",
    sensor_name="stroke_displacement",
    sensor_type_id="stroke_displacement",
)
sensor_04 = Sensor(
    machine_id="machine-02",
    sensor_id="load01",
    sensor_name="load01",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_05 = Sensor(
    machine_id="machine-02",
    sensor_id="stroke_displacement",
    sensor_name="stroke_displacement",
    sensor_type_id="stroke_displacement",
)
sensor_06 = Sensor(
    machine_id="machine-03",
    sensor_id="load01",
    sensor_name="load01",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_07 = Sensor(
    machine_id="machine-03",
    sensor_id="load02",
    sensor_name="load02",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_08 = Sensor(
    machine_id="machine-03",
    sensor_id="load03",
    sensor_name="load03",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_09 = Sensor(
    machine_id="machine-03",
    sensor_id="load04",
    sensor_name="load04",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_10 = Sensor(
    machine_id="machine-03",
    sensor_id="load05",
    sensor_name="load05",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_11 = Sensor(
    machine_id="machine-03",
    sensor_id="load06",
    sensor_name="load06",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_12 = Sensor(
    machine_id="machine-03",
    sensor_id="load07",
    sensor_name="load07",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_13 = Sensor(
    machine_id="machine-03",
    sensor_id="load08",
    sensor_name="load08",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_14 = Sensor(
    machine_id="machine-03",
    sensor_id="load09",
    sensor_name="load09",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_15 = Sensor(
    machine_id="machine-03",
    sensor_id="load10",
    sensor_name="load10",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_16 = Sensor(
    machine_id="machine-03",
    sensor_id="load11",
    sensor_name="load11",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_17 = Sensor(
    machine_id="machine-03",
    sensor_id="load12",
    sensor_name="load12",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_18 = Sensor(
    machine_id="machine-03",
    sensor_id="load13",
    sensor_name="load13",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_19 = Sensor(
    machine_id="machine-03",
    sensor_id="load14",
    sensor_name="load14",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_20 = Sensor(
    machine_id="machine-03",
    sensor_id="load15",
    sensor_name="load15",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_21 = Sensor(
    machine_id="machine-03",
    sensor_id="pulse",
    sensor_name="パルス",
    sensor_type_id="pulse",
)
sensor_22 = Sensor(
    machine_id="machine-01",
    sensor_id="load03",
    sensor_name="load03",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)
sensor_23 = Sensor(
    machine_id="machine-01",
    sensor_id="load04",
    sensor_name="load04",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)

demo_sensor_1 = Sensor(
    machine_id="demo-machine",
    sensor_id="pulse",
    sensor_name="パルス",
    sensor_type_id="pulse",
)

demo_sensor_2 = Sensor(
    machine_id="demo-machine",
    sensor_id="load01",
    sensor_name="load01",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)

j_sensor_1 = Sensor(
    machine_id="machine-j",
    sensor_id="stroke_displacement",
    sensor_name="ストローク変位",
    sensor_type_id="stroke_displacement",
)
j_sensor_2 = Sensor(
    machine_id="machine-j",
    sensor_id="load01",
    sensor_name="歪量",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
)

handler_01.sensors.append(sensor_01)
handler_01.sensors.append(sensor_02)
handler_01.sensors.append(sensor_22)
handler_01.sensors.append(sensor_23)
handler_01.sensors.append(sensor_03)

handler_02.sensors.append(sensor_04)
handler_02.sensors.append(sensor_05)
handler_03.sensors.append(sensor_06)
handler_03.sensors.append(sensor_07)
handler_03.sensors.append(sensor_08)
handler_03.sensors.append(sensor_09)
handler_03.sensors.append(sensor_10)
handler_03.sensors.append(sensor_11)
handler_03.sensors.append(sensor_12)
handler_03.sensors.append(sensor_13)
demo_handler.sensors.append(demo_sensor_1)
demo_handler.sensors.append(demo_sensor_2)
handler_j.sensors.append(j_sensor_1)
handler_j.sensors.append(j_sensor_2)

gateway_01.handlers.append(handler_01)
gateway_02.handlers.append(handler_02)
gateway_03.handlers.append(handler_03)
demo_gateway.handlers.append(demo_handler)
gateway_j.handlers.append(handler_j)

machine_01.gateways.append(gateway_01)
machine_02.gateways.append(gateway_02)
machine_03.gateways.append(gateway_03)
demo_machine.gateways.append(demo_gateway)
machine_j.gateways.append(gateway_j)

db.add(machine_type_01)
db.add(machine_type_02)

db.add(sensor_type_01)
db.add(sensor_type_02)
db.add(sensor_type_03)
db.add(sensor_type_04)
db.add(sensor_type_05)

db.add(machine_01)
db.add(machine_02)
db.add(machine_03)
db.add(demo_machine)
db.add(machine_j)

db.add(gateway_01)
db.add(gateway_02)
db.add(gateway_03)
db.add(demo_gateway)
db.add(gateway_j)

db.add(sensor_01)
db.add(sensor_02)
db.add(sensor_03)
db.add(sensor_04)
db.add(sensor_05)
db.add(demo_sensor_1)
db.add(demo_sensor_2)
db.add(j_sensor_1)
db.add(j_sensor_2)

data_collect_history_1 = DataCollectHistory(
    machine_id="machine-01",
    machine_name="テストプレス01",
    machine_type_id=1,
    started_at=datetime(2020, 12, 1, 10, 30, 11, 0) + timedelta(hours=-9),
    ended_at=datetime(2020, 12, 1, 10, 30, 11, 0) + timedelta(hours=-9) + timedelta(hours=1),
    sampling_frequency=100_000,
    sampling_ch_num=5,
    sample_count=0,
)

data_collect_history_2 = DataCollectHistory(
    machine_id="machine-01",
    machine_name="テストプレス01",
    machine_type_id=1,
    started_at=datetime(2021, 3, 27, 14, 15, 14, 0) + timedelta(hours=-9),
    ended_at=datetime(2021, 3, 27, 14, 15, 14, 0) + timedelta(hours=-9) + timedelta(hours=1),
    sampling_frequency=100_000,
    sampling_ch_num=5,
    sample_count=0,
)

data_collect_history_3 = DataCollectHistory(
    machine_id="demo-machine",
    machine_name="デモ用プレス機",
    machine_type_id=1,
    started_at=datetime(2021, 7, 9, 19, 0, 0, 0) + timedelta(hours=-9),
    ended_at=datetime(2021, 7, 9, 19, 0, 0, 0) + timedelta(hours=-9) + timedelta(minutes=5),
    sampling_frequency=100_000,
    sampling_ch_num=2,
    sample_count=0,
)

# pulse unittest用
data_collect_history_4 = DataCollectHistory(
    machine_id="machine-02",
    machine_name="テストプレス02",
    machine_type_id=1,
    started_at=datetime(2020, 12, 1, 10, 30, 11, 0) + timedelta(hours=-9),
    ended_at=datetime(2020, 12, 1, 10, 30, 11, 0) + timedelta(hours=-9) + timedelta(hours=1),
    sampling_frequency=100_000,
    sampling_ch_num=5,
    sample_count=0,
)

# J社用
data_collect_history_5 = DataCollectHistory(
    machine_id="machine-j",
    machine_name="プレス機J",
    machine_type_id=1,
    started_at=datetime(2021, 7, 31, 16, 54, 25, 0) + timedelta(hours=-9),
    ended_at=datetime(2021, 7, 31, 16, 54, 25, 0) + timedelta(hours=-9) + timedelta(hours=1),
    sampling_frequency=10_000,
    sampling_ch_num=2,
    sample_count=0,
)

db.add(data_collect_history_1)
db.add(data_collect_history_2)
db.add(data_collect_history_3)
db.add(data_collect_history_4)
db.add(data_collect_history_5)

data_collect_history_detail_1 = DataCollectHistoryDetail(
    data_collect_history_id=1,
    sensor_id="load01",
    sensor_name="荷重01",
    sensor_type_id="load",
    base_volt=1.0,
    base_load=1.0,
    initial_volt=1.0,
)

data_collect_history_detail_2 = DataCollectHistoryDetail(
    data_collect_history_id=1,
    sensor_id="load02",
    sensor_name="荷重02",
    sensor_type_id="load",
    base_volt=1.0,
    base_load=1.0,
    initial_volt=1.0,
)

data_collect_history_detail_3 = DataCollectHistoryDetail(
    data_collect_history_id=1,
    sensor_id="load03",
    sensor_name="荷重03",
    sensor_type_id="load",
    base_volt=1.0,
    base_load=1.0,
    initial_volt=1.0,
)

data_collect_history_detail_4 = DataCollectHistoryDetail(
    data_collect_history_id=1,
    sensor_id="load04",
    sensor_name="荷重04",
    sensor_type_id="load",
    base_volt=1.0,
    base_load=1.0,
    initial_volt=1.0,
)

data_collect_history_detail_5 = DataCollectHistoryDetail(
    data_collect_history_id=1,
    sensor_id="stroke_displacement",
    sensor_name="ストローク変位",
    sensor_type_id="stroke_displacement",
    base_volt=None,
    base_load=None,
    initial_volt=None,
)

data_collect_history_detail_2_1 = DataCollectHistoryDetail(
    data_collect_history_id=2,
    sensor_id="load01",
    sensor_name="荷重01",
    sensor_type_id="load",
    base_volt=1.0,
    base_load=1.0,
    initial_volt=1.0,
)

data_collect_history_detail_2_2 = DataCollectHistoryDetail(
    data_collect_history_id=2,
    sensor_id="load02",
    sensor_name="荷重02",
    sensor_type_id="load",
    base_volt=1.0,
    base_load=1.0,
    initial_volt=1.0,
)

data_collect_history_detail_2_3 = DataCollectHistoryDetail(
    data_collect_history_id=2,
    sensor_id="load03",
    sensor_name="荷重03",
    sensor_type_id="load",
    base_volt=1.0,
    base_load=1.0,
    initial_volt=1.0,
)

data_collect_history_detail_2_4 = DataCollectHistoryDetail(
    data_collect_history_id=2,
    sensor_id="load04",
    sensor_name="荷重04",
    sensor_type_id="load",
    base_volt=1.0,
    base_load=1.0,
    initial_volt=1.0,
)

data_collect_history_detail_2_5 = DataCollectHistoryDetail(
    data_collect_history_id=2,
    sensor_id="stroke_displacement",
    sensor_name="ストローク変位",
    sensor_type_id="stroke_displacement",
    base_volt=None,
    base_load=None,
    initial_volt=None,
)


# デモ用
data_collect_history_detail_3_1 = DataCollectHistoryDetail(
    data_collect_history_id=3,
    sensor_id="load01",
    sensor_name="荷重01",
    sensor_type_id="load",
    base_volt=1.0,
    base_load=1.0,
    initial_volt=1.0,
)

data_collect_history_detail_3_2 = DataCollectHistoryDetail(
    data_collect_history_id=3,
    sensor_id="pulse",
    sensor_name="パルス",
    sensor_type_id="pulse",
    base_volt=None,
    base_load=None,
    initial_volt=None,
)

# pulse unittest用
data_collect_history_detail_4_1 = DataCollectHistoryDetail(
    data_collect_history_id=4,
    sensor_id="load01",
    sensor_name="荷重01",
    sensor_type_id="load",
    base_volt=1.0,
    base_load=1.0,
    initial_volt=1.0,
)

data_collect_history_detail_4_2 = DataCollectHistoryDetail(
    data_collect_history_id=4,
    sensor_id="load02",
    sensor_name="荷重02",
    sensor_type_id="load",
    base_volt=1.0,
    base_load=1.0,
    initial_volt=1.0,
)

data_collect_history_detail_4_3 = DataCollectHistoryDetail(
    data_collect_history_id=4,
    sensor_id="load03",
    sensor_name="荷重03",
    sensor_type_id="load",
    base_volt=1.0,
    base_load=1.0,
    initial_volt=1.0,
)

data_collect_history_detail_4_4 = DataCollectHistoryDetail(
    data_collect_history_id=4,
    sensor_id="load04",
    sensor_name="荷重04",
    sensor_type_id="load",
    base_volt=1.0,
    base_load=1.0,
    initial_volt=1.0,
)

data_collect_history_detail_4_5 = DataCollectHistoryDetail(
    data_collect_history_id=4,
    sensor_id="pulse",
    sensor_name="パルス",
    sensor_type_id="pulse",
    base_volt=None,
    base_load=None,
    initial_volt=None,
)

# J社用
data_collect_history_detail_5_1 = DataCollectHistoryDetail(
    data_collect_history_id=5,
    sensor_id="stroke_displacement",
    sensor_name="ストローク変位",
    sensor_type_id="stroke_displacement",
    base_volt=None,
    base_load=None,
    initial_volt=None,
)
data_collect_history_detail_5_2 = DataCollectHistoryDetail(
    data_collect_history_id=5,
    sensor_id="load01",
    sensor_name="歪量",
    sensor_type_id="load",
    base_volt=2.5,
    base_load=2.5,
    initial_volt=None,
)


db.add(data_collect_history_detail_1)
db.add(data_collect_history_detail_2)
db.add(data_collect_history_detail_3)
db.add(data_collect_history_detail_4)
db.add(data_collect_history_detail_5)
db.add(data_collect_history_detail_2_1)
db.add(data_collect_history_detail_2_2)
db.add(data_collect_history_detail_2_3)
db.add(data_collect_history_detail_2_4)
db.add(data_collect_history_detail_2_5)
db.add(data_collect_history_detail_3_1)
db.add(data_collect_history_detail_3_2)
db.add(data_collect_history_detail_4_1)
db.add(data_collect_history_detail_4_2)
db.add(data_collect_history_detail_4_3)
db.add(data_collect_history_detail_4_4)
db.add(data_collect_history_detail_4_5)
db.add(data_collect_history_detail_5_1)
db.add(data_collect_history_detail_5_2)

data_collect_history_event_1 = DataCollectHistoryEvent(
    data_collect_history_id=2,
    event_id=0,
    event_name=common.COLLECT_STATUS.SETUP.value,
    occurred_at=datetime(2021, 3, 27, 14, 15, 14, 0) + timedelta(hours=-9),
)
data_collect_history_event_2 = DataCollectHistoryEvent(
    data_collect_history_id=2,
    event_id=1,
    event_name=common.COLLECT_STATUS.START.value,
    occurred_at=datetime(2021, 3, 27, 14, 15, 14, 0) + timedelta(hours=-9),
)
data_collect_history_event_3 = DataCollectHistoryEvent(
    data_collect_history_id=2,
    event_id=2,
    event_name=common.COLLECT_STATUS.STOP.value,
    occurred_at=datetime(2021, 3, 27, 14, 15, 14, 0) + timedelta(hours=-9) + timedelta(minutes=120),
)
data_collect_history_event_4 = DataCollectHistoryEvent(
    data_collect_history_id=2,
    event_id=3,
    event_name=common.COLLECT_STATUS.RECORDED.value,
    occurred_at=datetime(2021, 3, 27, 14, 15, 14, 0) + timedelta(hours=-9) + timedelta(minutes=121),
)

# J社用
data_collect_history_event_j_1 = DataCollectHistoryEvent(
    data_collect_history_id=5,
    event_id=0,
    event_name=common.COLLECT_STATUS.SETUP.value,
    occurred_at=datetime(2021, 7, 31, 16, 54, 25, 0) + timedelta(hours=-9),
)
data_collect_history_event_j_2 = DataCollectHistoryEvent(
    data_collect_history_id=5,
    event_id=1,
    event_name=common.COLLECT_STATUS.START.value,
    occurred_at=datetime(2021, 7, 31, 16, 54, 25, 0) + timedelta(hours=-9),
)
data_collect_history_event_j_3 = DataCollectHistoryEvent(
    data_collect_history_id=5,
    event_id=2,
    event_name=common.COLLECT_STATUS.STOP.value,
    occurred_at=datetime(2021, 7, 31, 16, 54, 25, 0) + timedelta(hours=-9) + timedelta(minutes=120),
)
data_collect_history_event_j_4 = DataCollectHistoryEvent(
    data_collect_history_id=5,
    event_id=3,
    event_name=common.COLLECT_STATUS.RECORDED.value,
    occurred_at=datetime(2021, 7, 31, 16, 54, 25, 0) + timedelta(hours=-9) + timedelta(minutes=121),
)

db.add(data_collect_history_event_1)
db.add(data_collect_history_event_2)
db.add(data_collect_history_event_3)
db.add(data_collect_history_event_4)

db.add(data_collect_history_event_j_1)
db.add(data_collect_history_event_j_2)
db.add(data_collect_history_event_j_3)
db.add(data_collect_history_event_j_4)

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

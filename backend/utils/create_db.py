import os
import sys

# backend配下のモジュールをimportするために、プロジェクト直下へのpathを通す
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from backend.data_collect_manager.models.machine_type import MachineType
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.gateway import Gateway
from backend.data_collect_manager.models.handler import Handler
from backend.data_collect_manager.models.sensor_type import SensorType
from backend.data_collect_manager.models.sensor import Sensor
from backend.data_collect_manager.models.db import register_db
from backend.common import common
from flask import Flask

app = Flask("app")
db = register_db(app)
db.drop_all()
db.create_all()

# MachineType
machine_type_01 = MachineType(machine_type_name="プレス")
machine_type_02 = MachineType(machine_type_name="圧力プレート")

# SensorType
sensor_type_01 = SensorType(sensor_type_name="荷重")
sensor_type_02 = SensorType(sensor_type_name="変位")
sensor_type_03 = SensorType(sensor_type_name="パルス")

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
    collect_status=common.COLLECT_STATUS.START.value,
    machine_type_id=1,
)
machine_03 = Machine(
    machine_id="machine-03",
    machine_name="テスト圧力プレート01",
    collect_status=common.COLLECT_STATUS.PAUSE.value,
    machine_type_id=2,
)
machine_04 = Machine(
    machine_id="machine-04",
    machine_name="テストマシン01",
    collect_status=common.COLLECT_STATUS.STOP.value,
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
    status=common.STATUS.RUNNING.value,
    log_level=5,
)
gateway_03 = Gateway(
    gateway_id="GW-03",
    sequence_number=3,
    gateway_result=0,
    status=common.STATUS.RUNNING.value,
    log_level=5,
)
gateway_04 = Gateway(
    gateway_id="GW-04",
    sequence_number=4,
    gateway_result=0,
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
    sampling_ch_num=16,
    filewrite_time=1,
)
handler_03 = Handler(
    handler_id="AD-USB-yyyy",
    handler_type="USB_yyyyHS",
    adc_serial_num="YYYYYYYY",
    sampling_frequency=1000,
    sampling_ch_num=16,
    filewrite_time=1,
)

# Sensor
sensor_01 = Sensor(sensor_name="load01", sensor_type_id=1)
sensor_02 = Sensor(sensor_name="load02", sensor_type_id=1)
sensor_03 = Sensor(sensor_name="displacement", sensor_type_id=2)
sensor_04 = Sensor(sensor_name="load01", sensor_type_id=1)
sensor_05 = Sensor(sensor_name="pulse", sensor_type_id=3)

handler_01.sensors.append(sensor_01)
handler_01.sensors.append(sensor_02)
handler_01.sensors.append(sensor_03)
handler_02.sensors.append(sensor_04)
handler_02.sensors.append(sensor_05)

gateway_01.handlers.append(handler_01)
gateway_02.handlers.append(handler_02)
gateway_03.handlers.append(handler_03)

machine_01.gateways.append(gateway_01)
machine_02.gateways.append(gateway_02)
machine_03.gateways.append(gateway_03)
machine_04.gateways.append(gateway_04)

db.session.add(machine_type_01)
db.session.add(machine_type_02)

db.session.add(sensor_type_01)
db.session.add(sensor_type_02)
db.session.add(sensor_type_03)

db.session.add(machine_01)
db.session.add(machine_02)
db.session.add(machine_03)
db.session.add(machine_04)

db.session.add(gateway_01)
db.session.add(gateway_02)
db.session.add(gateway_03)
db.session.add(gateway_04)

db.session.add(sensor_01)
db.session.add(sensor_02)
db.session.add(sensor_03)
db.session.add(sensor_04)
db.session.add(sensor_05)

db.session.commit()

[print(vars(x)) for x in MachineType.query.all()]
[print(vars(x)) for x in Machine.query.all()]
[print(vars(x)) for x in Gateway.query.all()]
[print(vars(x)) for x in Handler.query.all()]
[print(vars(x)) for x in Sensor.query.all()]
[print(vars(x)) for x in SensorType.query.all()]

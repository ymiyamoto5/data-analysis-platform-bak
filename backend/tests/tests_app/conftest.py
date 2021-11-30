"""
 ==================================
  conftest.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import dataclasses
import os
import pathlib
import struct
from datetime import datetime, timedelta
from typing import Final

import pytest
from backend.app.api.deps import get_db
from backend.app.db.session import Base
from backend.app.main import app
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
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

env_file = ".env"
load_dotenv(env_file)

DATA_DIR: Final[str] = os.environ["data_dir"]
DB_URL = "sqlite:////mnt/datadrive/temp.db"


@pytest.fixture
def client():
    """APIのクライアントのfixture。DBはtemp.dbとして用意する。"""

    client = TestClient(app)

    engine = create_engine(DB_URL, echo=True, connect_args={"check_same_thread": False})

    # NOTE: sqliteは既定で外部キー制約無効のため有効化する
    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute("pragma foreign_keys=ON")

    event.listen(engine, "connect", _fk_pragma_on_connect)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # テスト用DBを初期化（関数ごとにリセット）
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # NOTE: データ投入
    create_testdb(db)

    # DIを使ってFastAPIのDBの向き先をテスト用DBに変更
    def get_test_db():
        try:
            db = SessionLocal()
            yield db
        finally:
            db.close

    app.dependency_overrides[get_db] = get_test_db

    yield client


def create_testdb(db):
    """テスト用のデータ投入"""

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

    # TestMachine01
    test_machine_01 = Machine(
        machine_id="test-machine-01",
        machine_name="テスト機器01",
        collect_status=common.COLLECT_STATUS.RECORDED.value,
        machine_type_id=1,
        gateways=[
            Gateway(
                gateway_id="test-gw-01",
                sequence_number=1,
                gateway_result=0,
                status=common.STATUS.STOP.value,
                log_level=5,
                handlers=[
                    Handler(
                        handler_id="test-handler-01",
                        handler_type="USB_1608HS",
                        adc_serial_num="01ED23FA",
                        sampling_frequency=100000,
                        sampling_ch_num=5,
                        filewrite_time=10,
                        sensors=[
                            Sensor(
                                machine_id="test-machine-01",
                                sensor_id="stroke_displacement",
                                sensor_name="stroke_displacement",
                                sensor_type_id="stroke_displacement",
                                slope=1.0,
                                intercept=0.0,
                            ),
                            Sensor(
                                machine_id="test-machine-01",
                                sensor_id="load01",
                                sensor_name="load01",
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
    db.add(test_machine_01)

    test_machine_01_started_at = datetime(2021, 11, 11, 11, 0, 0, 0)

    test_data_collect_history_01 = DataCollectHistory(
        machine_id="test-machine-01",
        machine_name="テスト機器01",
        machine_type_id=1,
        started_at=test_machine_01_started_at + timedelta(hours=-9),
        ended_at=test_machine_01_started_at + timedelta(hours=-9) + timedelta(hours=1),
        sampling_frequency=100000,
        sampling_ch_num=5,
        processed_dir_path=os.path.join(DATA_DIR, "test-machine-01-20211111110000"),
        sample_count=0,
        data_collect_history_events=[
            DataCollectHistoryEvent(
                event_id=0,
                event_name=common.COLLECT_STATUS.SETUP.value,
                occurred_at=test_machine_01_started_at + timedelta(hours=-9),
            ),
            DataCollectHistoryEvent(
                event_id=1,
                event_name=common.COLLECT_STATUS.START.value,
                occurred_at=test_machine_01_started_at + timedelta(hours=-9),
            ),
            DataCollectHistoryEvent(
                event_id=2,
                event_name=common.COLLECT_STATUS.STOP.value,
                occurred_at=test_machine_01_started_at + timedelta(hours=-9) + timedelta(minutes=120),
            ),
            DataCollectHistoryEvent(
                event_id=3,
                event_name=common.COLLECT_STATUS.RECORDED.value,
                occurred_at=test_machine_01_started_at + timedelta(hours=-9) + timedelta(minutes=121),
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
        ],
    )
    db.add(test_data_collect_history_01)

    # TestMachine02
    test_machine_02 = Machine(
        machine_id="test-machine-02",
        machine_name="テスト機器02",
        collect_status=common.COLLECT_STATUS.RECORDED.value,
        machine_type_id=2,
        gateways=[
            Gateway(
                gateway_id="test-gw-02",
                sequence_number=1,
                gateway_result=0,
                status=common.STATUS.STOP.value,
                log_level=5,
                handlers=[
                    Handler(
                        handler_id="test-handler-02",
                        handler_type="USB_1608HS",
                        adc_serial_num="00002222",
                        sampling_frequency=100000,
                        sampling_ch_num=3,
                        filewrite_time=1,
                        sensors=[
                            Sensor(
                                machine_id="test-machine-02",
                                sensor_id="pulse",
                                sensor_name="pulse",
                                sensor_type_id="pulse",
                                slope=1.0,
                                intercept=0.0,
                            ),
                            Sensor(
                                machine_id="test-machine-02",
                                sensor_id="load01",
                                sensor_name="load01",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                            ),
                            Sensor(
                                machine_id="test-machine-02",
                                sensor_id="load02",
                                sensor_name="load02",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                            ),
                        ],
                    ),
                    Handler(
                        handler_id="test-handler-03",
                        handler_type="USB_1608HS",
                        adc_serial_num="00003333",
                        sampling_frequency=100000,
                        sampling_ch_num=2,
                        filewrite_time=1,
                        sensors=[
                            Sensor(
                                machine_id="test-machine-02",
                                sensor_id="load03",
                                sensor_name="load03",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                            ),
                            Sensor(
                                machine_id="test-machine-02",
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
    db.add(test_machine_02)

    test_machine_02_started_at = datetime(2021, 7, 9, 19, 0, 0, 0)

    test_data_collect_history_02 = DataCollectHistory(
        machine_id="test-machine-02",
        machine_name="テスト機器02",
        machine_type_id=1,
        started_at=test_machine_02_started_at + timedelta(hours=-9),
        ended_at=test_machine_02_started_at + timedelta(hours=-9) + timedelta(hours=1),
        sampling_frequency=100000,
        sampling_ch_num=5,
        processed_dir_path=os.path.join(DATA_DIR, "test-machine-02-20210709190000"),
        sample_count=0,
        data_collect_history_events=[
            DataCollectHistoryEvent(
                event_id=0,
                event_name=common.COLLECT_STATUS.SETUP.value,
                occurred_at=test_machine_02_started_at + timedelta(hours=-9),
            ),
            DataCollectHistoryEvent(
                event_id=1,
                event_name=common.COLLECT_STATUS.START.value,
                occurred_at=test_machine_02_started_at + timedelta(hours=-9),
            ),
            DataCollectHistoryEvent(
                event_id=2,
                event_name=common.COLLECT_STATUS.STOP.value,
                occurred_at=test_machine_02_started_at + timedelta(hours=-9) + timedelta(minutes=120),
            ),
            DataCollectHistoryEvent(
                event_id=3,
                event_name=common.COLLECT_STATUS.RECORDED.value,
                occurred_at=test_machine_02_started_at + timedelta(hours=-9) + timedelta(minutes=121),
            ),
        ],
        data_collect_history_details=[
            DataCollectHistoryDetail(
                sensor_id="pulse",
                sensor_name="パルス",
                sensor_type_id="pulse",
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
    db.add(test_data_collect_history_02)

    # TestMachine03
    test_machine_03 = Machine(
        machine_id="test-machine-03",
        machine_name="テスト機器03",
        collect_status=common.COLLECT_STATUS.RECORDED.value,
        machine_type_id=1,
        gateways=[
            Gateway(
                gateway_id="test-gw-03",
                sequence_number=1,
                gateway_result=0,
                status=common.STATUS.STOP.value,
                log_level=5,
                handlers=[
                    Handler(
                        handler_id="test-handler-04",
                        handler_type="USB_1608HS",
                        adc_serial_num="00004444",
                        sampling_frequency=100000,
                        sampling_ch_num=2,
                        filewrite_time=1,
                        sensors=[
                            Sensor(
                                machine_id="test-machine-03",
                                sensor_id="stroke_displacement",
                                sensor_name="stroke_displacement",
                                sensor_type_id="stroke_displacement",
                                slope=1.0,
                                intercept=0.0,
                            ),
                            Sensor(
                                machine_id="test-machine-03",
                                sensor_id="load01",
                                sensor_name="歪み",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                            ),
                        ],
                    ),
                ],
            ),
            Gateway(
                gateway_id="test-gw-04",
                sequence_number=1,
                gateway_result=0,
                status=common.STATUS.STOP.value,
                log_level=5,
                handlers=[
                    Handler(
                        handler_id="test-handler-05",
                        handler_type="USB_1608HS",
                        adc_serial_num="00005555",
                        sampling_frequency=100000,
                        sampling_ch_num=2,
                        filewrite_time=1,
                        sensors=[],
                    ),
                ],
            ),
        ],
    )
    db.add(test_machine_03)

    test_machine_03_started_at_1 = datetime(2021, 8, 1, 9, 40, 30, 0)

    test_data_collect_history_03_1 = DataCollectHistory(
        machine_id="test-machine-03",
        machine_name="テスト機器03",
        machine_type_id=1,
        started_at=test_machine_03_started_at_1 + timedelta(hours=-9),
        ended_at=test_machine_03_started_at_1 + timedelta(hours=-9) + timedelta(hours=1),
        sampling_frequency=100000,
        sampling_ch_num=2,
        processed_dir_path=os.path.join(DATA_DIR, "test-machine-03-20210801094030"),
        sample_count=0,
        data_collect_history_events=[
            DataCollectHistoryEvent(
                event_id=0,
                event_name=common.COLLECT_STATUS.SETUP.value,
                occurred_at=test_machine_03_started_at_1 + timedelta(hours=-9),
            ),
            DataCollectHistoryEvent(
                event_id=1,
                event_name=common.COLLECT_STATUS.START.value,
                occurred_at=test_machine_03_started_at_1 + timedelta(hours=-9),
            ),
            DataCollectHistoryEvent(
                event_id=2,
                event_name=common.COLLECT_STATUS.STOP.value,
                occurred_at=test_machine_03_started_at_1 + timedelta(hours=-9) + timedelta(minutes=120),
            ),
            DataCollectHistoryEvent(
                event_id=3,
                event_name=common.COLLECT_STATUS.RECORDED.value,
                occurred_at=test_machine_03_started_at_1 + timedelta(hours=-9) + timedelta(minutes=121),
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
    db.add(test_data_collect_history_03_1)

    test_machine_03_started_at_2 = datetime(2021, 10, 9, 15, 56, 26, 0)

    test_data_collect_history_03_2 = DataCollectHistory(
        machine_id="test-machine-03",
        machine_name="テスト機器03",
        machine_type_id=1,
        started_at=test_machine_03_started_at_2 + timedelta(hours=-9),
        ended_at=test_machine_03_started_at_2 + timedelta(hours=-9) + timedelta(hours=1),
        sampling_frequency=100000,
        sampling_ch_num=2,
        processed_dir_path=os.path.join(DATA_DIR, "test-machine-03-20211009155626"),
        sample_count=0,
        data_collect_history_events=[
            DataCollectHistoryEvent(
                event_id=0,
                event_name=common.COLLECT_STATUS.SETUP.value,
                occurred_at=test_machine_03_started_at_2 + timedelta(hours=-9),
            ),
            DataCollectHistoryEvent(
                event_id=1,
                event_name=common.COLLECT_STATUS.START.value,
                occurred_at=test_machine_03_started_at_2 + timedelta(hours=-9),
            ),
            DataCollectHistoryEvent(
                event_id=2,
                event_name=common.COLLECT_STATUS.STOP.value,
                occurred_at=test_machine_03_started_at_2 + timedelta(hours=-9) + timedelta(minutes=120),
            ),
            DataCollectHistoryEvent(
                event_id=3,
                event_name=common.COLLECT_STATUS.RECORDED.value,
                occurred_at=test_machine_03_started_at_2 + timedelta(hours=-9) + timedelta(minutes=121),
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
    db.add(test_data_collect_history_03_2)

    # 子が存在しないデータの作成
    test_machine_04 = Machine(
        machine_id="test-machine-04",
        machine_name="テスト機器04",
        collect_status=common.COLLECT_STATUS.RECORDED.value,
        machine_type_id=1,
        gateways=[],
    )

    test_gw_05 = Gateway(
        gateway_id="test-gw-05",
        sequence_number=1,
        gateway_result=0,
        status=common.STATUS.STOP.value,
        machine_id="test-machine-01",
        log_level=5,
        handlers=[],
    )

    db.add(test_machine_04)
    db.add(test_gw_05)

    db.commit()


@dataclasses.dataclass
class DatFiles:
    tmp_path: pathlib.Path
    tmp_dat_1: pathlib.Path
    tmp_dat_2: pathlib.Path
    tmp_dat_3: pathlib.Path
    tmp_dat_4: pathlib.Path
    tmp_dat_5: pathlib.Path


@pytest.fixture
def dat_files(tmp_path):
    """datファイルのfixture"""

    machine_id: str = "machine-01"

    tmp_dat_1: pathlib.Path = tmp_path / f"{machine_id}_AD-00_20201216-080058.620753.dat"
    tmp_dat_2: pathlib.Path = tmp_path / f"{machine_id}_AD-00_20201216-080059.620753.dat"
    tmp_dat_3: pathlib.Path = tmp_path / f"{machine_id}_AD-00_20201216-080100.620753.dat"
    tmp_dat_4: pathlib.Path = tmp_path / f"{machine_id}_AD-00_20201216-080101.620753.dat"
    tmp_dat_5: pathlib.Path = tmp_path / f"{machine_id}_AD-00_20201216-080102.620753.dat"

    binary = struct.pack("<ddddd", 10.0, 1.1, 2.2, 3.3, 4.4) + struct.pack("<ddddd", 9.0, 1.2, 2.3, 3.4, 4.5)

    tmp_dat_1.write_bytes(binary)
    tmp_dat_2.write_bytes(binary)
    tmp_dat_3.write_bytes(binary)
    tmp_dat_4.write_bytes(binary)
    tmp_dat_5.write_bytes(binary)

    dat_files = DatFiles(tmp_path, tmp_dat_1, tmp_dat_2, tmp_dat_3, tmp_dat_4, tmp_dat_5)

    yield dat_files

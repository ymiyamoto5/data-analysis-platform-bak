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

import pandas as pd
import pytest
from backend.app.api.deps import get_db
from backend.app.db.session import Base
from backend.app.main import app
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_event import DataCollectHistoryEvent
from backend.app.models.data_collect_history_gateway import DataCollectHistoryGateway
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
from backend.app.models.data_collect_history_sensor import DataCollectHistorySensor
from backend.app.models.gateway import Gateway
from backend.app.models.handler import Handler
from backend.app.models.machine import Machine
from backend.app.models.machine_type import MachineType
from backend.app.models.sensor import Sensor
from backend.app.models.sensor_type import SensorType
from backend.common import common
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

DATA_DIR: Final[str] = os.environ["DATA_DIR"]
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

    db: Session = SessionLocal()

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


@pytest.fixture
def db():
    """DBのみのfixture"""

    engine = create_engine(DB_URL, echo=True, connect_args={"check_same_thread": False})

    # NOTE: sqliteは既定で外部キー制約無効のため有効化する
    # def _fk_pragma_on_connect(dbapi_con, con_record):
    #     dbapi_con.execute("pragma foreign_keys=ON")

    # event.listen(engine, "connect", _fk_pragma_on_connect)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # テスト用DBを初期化（関数ごとにリセット）
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    create_testdb(db)
    yield db
    db.close()


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
    sensor_type_04 = SensorType(sensor_type_id="bolt", sensor_type_name="ボルト")
    sensor_type_05 = SensorType(sensor_type_id="displacement", sensor_type_name="変位")
    sensor_type_06 = SensorType(sensor_type_id="dummy", sensor_type_name="ダミー")
    db.add(sensor_type_01)
    db.add(sensor_type_02)
    db.add(sensor_type_03)
    db.add(sensor_type_04)
    db.add(sensor_type_05)
    db.add(sensor_type_06)

    # 複数ハンドラーの機器
    test_machine_01 = Machine(
        machine_id="test-machine-01",
        machine_name="テスト機器01",
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
                gateway_id="test-gateway-01",
                sequence_number=1,
                gateway_result=0,
                status=common.STATUS.STOP.value,
                log_level=5,
                handlers=[
                    Handler(
                        handler_id="test-handler-01-1",
                        handler_type="USB_1608HS",
                        adc_serial_num="01ED23FA",
                        sampling_frequency=100000,
                        sampling_ch_num=3,
                        filewrite_time=1,
                        is_primary=True,
                        is_cut_out_target=True,
                        is_multi=True,
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
                            Sensor(
                                machine_id="test-machine-01",
                                sensor_id="load02",
                                sensor_name="load02",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                            ),
                        ],
                    ),
                    Handler(
                        handler_id="test-handler-01-2",
                        handler_type="USB_1608HS",
                        adc_serial_num="01ED23FB",
                        sampling_frequency=100000,
                        sampling_ch_num=3,
                        filewrite_time=1,
                        is_primary=False,
                        is_cut_out_target=True,
                        is_multi=True,
                        sensors=[
                            Sensor(
                                machine_id="test-machine-01",
                                sensor_id="load03",
                                sensor_name="load03",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                            ),
                            Sensor(
                                machine_id="test-machine-01",
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
    db.add(test_machine_01)

    test_machine_01_started_at = datetime(2021, 11, 11, 11, 0, 0, 0)

    test_data_collect_history_01 = DataCollectHistory(
        machine_id="test-machine-01",
        machine_name="テスト機器01",
        machine_type_id=1,
        started_at=test_machine_01_started_at + timedelta(hours=-9),
        ended_at=test_machine_01_started_at + timedelta(hours=-9) + timedelta(hours=1),
        processed_dir_path=os.path.join(DATA_DIR, "test-machine-01-20211111110000"),
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
        data_collect_history_gateways=[
            DataCollectHistoryGateway(
                gateway_id="test-gateway-01",
                log_level=5,
                data_collect_history_handlers=[
                    DataCollectHistoryHandler(
                        data_collect_history_id=1,
                        handler_id="test-handler-01-1",
                        handler_type="USB_1608HS",
                        adc_serial_num="01ED23FA",
                        sampling_frequency=100000,
                        sampling_ch_num=3,
                        filewrite_time=1,
                        is_primary=True,
                        is_cut_out_target=True,
                        is_multi=True,
                        data_collect_history_sensors=[
                            DataCollectHistorySensor(
                                data_collect_history_id=1,
                                sensor_id="stroke_displacement",
                                sensor_name="stroke_displacement",
                                sensor_type_id="stroke_displacement",
                                slope=1.0,
                                intercept=0.0,
                            ),
                            DataCollectHistorySensor(
                                data_collect_history_id=1,
                                sensor_id="load01",
                                sensor_name="load01",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                                start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            ),
                            DataCollectHistorySensor(
                                data_collect_history_id=1,
                                sensor_id="load02",
                                sensor_name="load02",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                                start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            ),
                        ],
                    ),
                    DataCollectHistoryHandler(
                        data_collect_history_id=1,
                        handler_id="test-handler-01-2",
                        handler_type="USB_1608HS",
                        adc_serial_num="01ED23FB",
                        sampling_frequency=100000,
                        sampling_ch_num=3,
                        filewrite_time=1,
                        is_primary=False,
                        is_cut_out_target=True,
                        is_multi=True,
                        data_collect_history_sensors=[
                            DataCollectHistorySensor(
                                data_collect_history_id=1,
                                sensor_id="load03",
                                sensor_name="load03",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                                start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            ),
                            DataCollectHistorySensor(
                                data_collect_history_id=1,
                                sensor_id="load04",
                                sensor_name="load04",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                                start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            ),
                        ],
                    ),
                ],
            )
        ],
    )
    db.add(test_data_collect_history_01)

    # 単一ハンドラー
    test_machine_02 = Machine(
        machine_id="test-machine-02",
        machine_name="テスト機器02",
        collect_status=common.COLLECT_STATUS.RECORDED.value,
        machine_type_id=2,
        gateways=[
            Gateway(
                gateway_id="test-gateway-02",
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
                        is_primary=False,
                        is_cut_out_target=True,
                        is_multi=False,
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
        processed_dir_path=os.path.join(DATA_DIR, "test-machine-02-20210709190000"),
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
        data_collect_history_gateways=[
            DataCollectHistoryGateway(
                gateway_id="test-gateway-02",
                log_level=5,
                data_collect_history_handlers=[
                    DataCollectHistoryHandler(
                        data_collect_history_id=1,
                        handler_id="test-handler-02",
                        handler_type="USB_1608HS",
                        adc_serial_num="01ED23FA",
                        sampling_frequency=100000,
                        sampling_ch_num=5,
                        filewrite_time=1,
                        is_primary=False,
                        is_cut_out_target=True,
                        is_multi=False,
                        data_collect_history_sensors=[
                            DataCollectHistorySensor(
                                data_collect_history_id=1,
                                sensor_id="stroke_displacement",
                                sensor_name="stroke_displacement",
                                sensor_type_id="stroke_displacement",
                                slope=1.0,
                                intercept=0.0,
                            ),
                            DataCollectHistorySensor(
                                data_collect_history_id=1,
                                sensor_id="load01",
                                sensor_name="load01",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                                start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            ),
                            DataCollectHistorySensor(
                                data_collect_history_id=1,
                                sensor_id="load02",
                                sensor_name="load02",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                                start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            ),
                            DataCollectHistorySensor(
                                data_collect_history_id=1,
                                sensor_id="load03",
                                sensor_name="load03",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                                start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            ),
                            DataCollectHistorySensor(
                                data_collect_history_id=1,
                                sensor_id="load04",
                                sensor_name="load04",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                                start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                            ),
                        ],
                    ),
                ],
            )
        ],
    )
    db.add(test_data_collect_history_02)

    # # TestMachine03
    # test_machine_03 = Machine(
    #     machine_id="test-machine-03",
    #     machine_name="テスト機器03",
    #     collect_status=common.COLLECT_STATUS.RECORDED.value,
    #     machine_type_id=1,
    #     gateways=[
    #         Gateway(
    #             gateway_id="test-gateway-03",
    #             sequence_number=1,
    #             gateway_result=0,
    #             status=common.STATUS.STOP.value,
    #             log_level=5,
    #             handlers=[
    #                 Handler(
    #                     handler_id="test-handler-04",
    #                     handler_type="USB_1608HS",
    #                     adc_serial_num="00004444",
    #                     sampling_frequency=100000,
    #                     sampling_ch_num=2,
    #                     filewrite_time=1,
    #                     sensors=[
    #                         Sensor(
    #                             machine_id="test-machine-03",
    #                             sensor_id="stroke_displacement",
    #                             sensor_name="stroke_displacement",
    #                             sensor_type_id="stroke_displacement",
    #                             slope=1.0,
    #                             intercept=0.0,
    #                         ),
    #                         Sensor(
    #                             machine_id="test-machine-03",
    #                             sensor_id="load01",
    #                             sensor_name="歪み",
    #                             sensor_type_id="load",
    #                             slope=1.0,
    #                             intercept=0.0,
    #                         ),
    #                     ],
    #                 ),
    #             ],
    #         ),
    #         Gateway(
    #             gateway_id="test-gateway-04",
    #             sequence_number=1,
    #             gateway_result=0,
    #             status=common.STATUS.STOP.value,
    #             log_level=5,
    #             handlers=[
    #                 Handler(
    #                     handler_id="test-handler-05",
    #                     handler_type="USB_1608HS",
    #                     adc_serial_num="00005555",
    #                     sampling_frequency=100000,
    #                     sampling_ch_num=2,
    #                     filewrite_time=1,
    #                     sensors=[],
    #                 ),
    #             ],
    #         ),
    #     ],
    # )
    # db.add(test_machine_03)

    # test_machine_03_started_at_1 = datetime(2021, 8, 1, 9, 40, 30, 0)

    # test_data_collect_history_03_1 = DataCollectHistory(
    #     machine_id="test-machine-03",
    #     machine_name="テスト機器03",
    #     machine_type_id=1,
    #     started_at=test_machine_03_started_at_1 + timedelta(hours=-9),
    #     ended_at=test_machine_03_started_at_1 + timedelta(hours=-9) + timedelta(hours=1),
    #     sampling_frequency=100000,
    #     sampling_ch_num=2,
    #     processed_dir_path=os.path.join(DATA_DIR, "test-machine-03-20210801094030"),
    #     sample_count=0,
    #     data_collect_history_events=[
    #         DataCollectHistoryEvent(
    #             event_id=0,
    #             event_name=common.COLLECT_STATUS.SETUP.value,
    #             occurred_at=test_machine_03_started_at_1 + timedelta(hours=-9),
    #         ),
    #         DataCollectHistoryEvent(
    #             event_id=1,
    #             event_name=common.COLLECT_STATUS.START.value,
    #             occurred_at=test_machine_03_started_at_1 + timedelta(hours=-9),
    #         ),
    #         DataCollectHistoryEvent(
    #             event_id=2,
    #             event_name=common.COLLECT_STATUS.STOP.value,
    #             occurred_at=test_machine_03_started_at_1 + timedelta(hours=-9) + timedelta(minutes=120),
    #         ),
    #         DataCollectHistoryEvent(
    #             event_id=3,
    #             event_name=common.COLLECT_STATUS.RECORDED.value,
    #             occurred_at=test_machine_03_started_at_1 + timedelta(hours=-9) + timedelta(minutes=121),
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
    # db.add(test_data_collect_history_03_1)

    # test_machine_03_started_at_2 = datetime(2021, 10, 9, 15, 56, 26, 0)

    # test_data_collect_history_03_2 = DataCollectHistory(
    #     machine_id="test-machine-03",
    #     machine_name="テスト機器03",
    #     machine_type_id=1,
    #     started_at=test_machine_03_started_at_2 + timedelta(hours=-9),
    #     ended_at=test_machine_03_started_at_2 + timedelta(hours=-9) + timedelta(hours=1),
    #     sampling_frequency=100000,
    #     sampling_ch_num=2,
    #     processed_dir_path=os.path.join(DATA_DIR, "test-machine-03-20211009155626"),
    #     sample_count=0,
    #     data_collect_history_events=[
    #         DataCollectHistoryEvent(
    #             event_id=0,
    #             event_name=common.COLLECT_STATUS.SETUP.value,
    #             occurred_at=test_machine_03_started_at_2 + timedelta(hours=-9),
    #         ),
    #         DataCollectHistoryEvent(
    #             event_id=1,
    #             event_name=common.COLLECT_STATUS.START.value,
    #             occurred_at=test_machine_03_started_at_2 + timedelta(hours=-9),
    #         ),
    #         DataCollectHistoryEvent(
    #             event_id=2,
    #             event_name=common.COLLECT_STATUS.STOP.value,
    #             occurred_at=test_machine_03_started_at_2 + timedelta(hours=-9) + timedelta(minutes=120),
    #         ),
    #         DataCollectHistoryEvent(
    #             event_id=3,
    #             event_name=common.COLLECT_STATUS.RECORDED.value,
    #             occurred_at=test_machine_03_started_at_2 + timedelta(hours=-9) + timedelta(minutes=121),
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
    # db.add(test_data_collect_history_03_2)

    # 子が存在しないデータの作成
    test_machine_no_gateway = Machine(
        machine_id="test-machine-04",
        machine_name="テスト機器04",
        collect_status=common.COLLECT_STATUS.RECORDED.value,
        machine_type_id=1,
        gateways=[],
    )

    test_gateway_no_handler = Gateway(
        gateway_id="test-gateway-no-handler",
        sequence_number=1,
        gateway_result=0,
        status=common.STATUS.STOP.value,
        machine_id="test-machine-01",
        log_level=5,
        handlers=[],
    )

    test_gw_no_sensor = Gateway(
        gateway_id="test-gateway-no-sensor",
        sequence_number=1,
        gateway_result=0,
        status=common.STATUS.STOP.value,
        machine_id="test-machine-01",
        log_level=5,
        handlers=[
            Handler(
                gateway_id="test-gateway-no-sensor",
                handler_id="test-handler-no-child",
                handler_type="USB_1608HS",
                adc_serial_num="01ED23FA",
                sampling_frequency=100000,
                sampling_ch_num=5,
                filewrite_time=1,
                is_primary=False,
                is_cut_out_target=True,
                is_multi=False,
                sensors=[],
            ),
        ],
    )

    db.add(test_machine_no_gateway)
    db.add(test_gateway_no_handler)
    db.add(test_gw_no_sensor)

    db.commit()


@dataclasses.dataclass
class DatFiles:
    tmp_path: pathlib.Path
    tmp_dat_1: pathlib.Path
    tmp_dat_2: pathlib.Path
    tmp_dat_3: pathlib.Path
    tmp_dat_4: pathlib.Path


@pytest.fixture
def dat_files(tmp_path):
    """datファイルのfixture"""

    machine_id: str = "test-machine-01"
    gateway_id: str = "test-gateway-01"
    handlers = ["test-handler-01-1", "test-handler-01-2"]

    tmp_dat_1: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handlers[0]}_20201216-080058.620753_1.dat"
    tmp_dat_2: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handlers[0]}_20201216-080059.620753_2.dat"
    tmp_dat_3: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handlers[1]}_20201216-080100.620753_1.dat"
    tmp_dat_4: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handlers[1]}_20201216-080101.620753_2.dat"

    binary_1 = struct.pack("<ddd", 10.0, 1.1, 2.2)
    binary_2 = struct.pack("<ddd", 9.0, 1.2, 2.3)
    binary_3 = struct.pack("<dd", 3.3, 4.4)
    binary_4 = struct.pack("<dd", 3.4, 4.5)

    tmp_dat_1.write_bytes(binary_1)
    tmp_dat_2.write_bytes(binary_2)
    tmp_dat_3.write_bytes(binary_3)
    tmp_dat_4.write_bytes(binary_4)

    dat_files = DatFiles(tmp_path, tmp_dat_1, tmp_dat_2, tmp_dat_3, tmp_dat_4)

    yield dat_files


@dataclasses.dataclass
class PklFiles:
    tmp_path: pathlib.Path
    tmp_pkl_1: pathlib.Path
    tmp_pkl_2: pathlib.Path
    tmp_pkl_3: pathlib.Path
    tmp_pkl_4: pathlib.Path
    tmp_pkl_5: pathlib.Path


@pytest.fixture
def pkl_files(tmp_path):
    """pklファイルのfixture"""

    processed_dir: str = "20211111110000"
    machine_id: str = "machine-01"
    tmp_processed_dir = tmp_path / f"{processed_dir}"

    os.mkdir(tmp_processed_dir)

    tmp_pkl_1: pathlib.Path = tmp_processed_dir / f"{machine_id}_AD-00_20211111-110001.620753.pkl"
    tmp_pkl_2: pathlib.Path = tmp_processed_dir / f"{machine_id}_AD-00_20211111-110002.620753.pkl"
    tmp_pkl_3: pathlib.Path = tmp_processed_dir / f"{machine_id}_AD-00_20211111-110003.620753.pkl"
    tmp_pkl_4: pathlib.Path = tmp_processed_dir / f"{machine_id}_AD-00_20211111-110004.620753.pkl"
    tmp_pkl_5: pathlib.Path = tmp_processed_dir / f"{machine_id}_AD-00_20211111-110005.620753.pkl"

    df = create_rawdata_df()
    df.to_pickle(tmp_pkl_1)
    df.to_pickle(tmp_pkl_2)
    df.to_pickle(tmp_pkl_3)
    df.to_pickle(tmp_pkl_4)
    df.to_pickle(tmp_pkl_5)

    pkl_files = PklFiles(tmp_processed_dir, tmp_pkl_1, tmp_pkl_2, tmp_pkl_3, tmp_pkl_4, tmp_pkl_5)

    yield pkl_files


def create_rawdata_df():
    """生データ（物理変換後）のDataFrame fixture。
    切り出しの開始ストローク変位値 47.0, 終了ストローク変位値 34.0 を想定したデータ。
    """

    rawdata = [
        # 切り出し区間前1
        {
            "sequential_number": 0,
            "timestamp": datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp(),
            "stroke_displacement": 49.284,
            "load01": 0.223,
            "load02": 0.211,
            "load03": 0.200,
            "load04": 0.218,
        },
        # 切り出し区間前2
        {
            "sequential_number": 1,
            "timestamp": datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp(),
            "stroke_displacement": 47.534,
            "load01": 0.155,
            "load02": 0.171,
            "load03": 0.180,
            "load04": 0.146,
        },
        # 切り出し区間1-1
        {
            "sequential_number": 2,
            "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
            "stroke_displacement": 47.0,
            "load01": 1.574,
            "load02": 1.308,
            "load03": 1.363,
            "load04": 1.432,
        },
        # 切り出し区間1-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
        {
            "sequential_number": 3,
            "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
            "stroke_displacement": 47.1,
            "load01": 1.500,
            "load02": 1.200,
            "load03": 1.300,
            "load04": 1.400,
        },
        # 切り出し区間1-3
        {
            "sequential_number": 4,
            "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
            "stroke_displacement": 34.961,
            "load01": -0.256,
            "load02": -0.078,
            "load03": 0.881,
            "load04": 0.454,
        },
        # 切り出し区間後1
        {
            "sequential_number": 5,
            "timestamp": datetime(2020, 12, 1, 10, 30, 15, 111111).timestamp(),
            "stroke_displacement": 30.599,
            "load01": -0.130,
            "load02": 0.020,
            "load03": 0.483,
            "load04": 0.419,
        },
        # 切り出し区間後2
        {
            "sequential_number": 6,
            "timestamp": datetime(2020, 12, 1, 10, 30, 16, 111111).timestamp(),
            "stroke_displacement": 24.867,
            "load01": -0.052,
            "load02": 0.035,
            "load03": 0.402,
            "load04": 0.278,
        },
        # 切り出し区間後3(ストローク変位にmargin=0.1を加算した場合、ショットの終了と見做されないストローク変位値)
        {
            "sequential_number": 7,
            "timestamp": datetime(2020, 12, 1, 10, 30, 17, 111111).timestamp(),
            "stroke_displacement": 47.100,
            "load01": 0.155,
            "load02": 0.171,
            "load03": 0.180,
            "load04": 0.146,
        },
        # 切り出し区間後4(ショット区間終了）
        {
            "sequential_number": 8,
            "timestamp": datetime(2020, 12, 1, 10, 30, 18, 111111).timestamp(),
            "stroke_displacement": 47.150,
            "load01": 0.156,
            "load02": 0.172,
            "load03": 0.181,
            "load04": 0.147,
        },
        # 切り出し区間2-1
        {
            "sequential_number": 9,
            "timestamp": datetime(2020, 12, 1, 10, 30, 19, 111111).timestamp(),
            "stroke_displacement": 47.0,
            "load01": 1.574,
            "load02": 1.308,
            "load03": 1.363,
            "load04": 1.432,
        },
        # 切り出し区間2-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
        {
            "sequential_number": 10,
            "timestamp": datetime(2020, 12, 1, 10, 30, 20, 111111).timestamp(),
            "stroke_displacement": 47.1,
            "load01": 1.500,
            "load02": 1.200,
            "load03": 1.300,
            "load04": 1.400,
        },
        # 切り出し区間2-3
        {
            "sequential_number": 11,
            "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
            "stroke_displacement": 34.961,
            "load01": -0.256,
            "load02": -0.078,
            "load03": 0.881,
            "load04": 0.454,
        },
        # 切り出し区間後
        {
            "sequential_number": 12,
            "timestamp": datetime(2020, 12, 1, 10, 30, 22, 111111).timestamp(),
            "stroke_displacement": 30.599,
            "load01": -0.130,
            "load02": 0.020,
            "load03": 0.483,
            "load04": 0.419,
        },
    ]

    rawdata_df = pd.DataFrame(rawdata)
    return rawdata_df

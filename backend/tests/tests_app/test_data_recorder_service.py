"""
 ==================================
  test_data_recorder.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import os
import shutil
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_event import DataCollectHistoryEvent
from backend.app.models.data_collect_history_gateway import DataCollectHistoryGateway
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
from backend.app.models.data_collect_history_sensor import DataCollectHistorySensor
from backend.app.models.machine import Machine
from backend.app.services.data_recorder_service import DataRecorderService
from backend.common import common
from backend.file_manager.file_manager import FileManager


class TestReadBinaryFiles:
    def test_normal(self, dat_files):
        """正常系：バイナリファイルが正常に読めること"""

        machine_id: str = "test-machine-01"
        gateway_id: str = "test-gateway-01"
        handler_id: str = "test-handler-01"

        file_infos = FileManager.create_files_info(dat_files.tmp_path._str, machine_id, "dat")
        file = file_infos[0]

        j_started_at_1 = datetime(2020, 8, 1, 9, 40, 30, 0)

        dummy_data_collect_history = DataCollectHistory(
            machine_id="test-machine-01",
            machine_name="デモ用プレス機",
            machine_type_id=1,
            started_at=j_started_at_1 + timedelta(hours=-9),
            ended_at=j_started_at_1 + timedelta(hours=-9) + timedelta(hours=1),
            sampling_frequency=100000,
            sampling_ch_num=5,
            processed_dir_path="/mnt/datadrive/data/xxx",
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
            data_collect_history_gateways=[
                DataCollectHistoryGateway(
                    gateway_id="gw-01",
                    log_level=5,
                    data_collect_history_handlers=[
                        DataCollectHistoryHandler(
                            data_collect_history_id=1,
                            handler_id="handler-01",
                            handler_type="USB_1608HS",
                            adc_serial_num="00002222",
                            sampling_frequency=100000,
                            sampling_ch_num=3,
                            filewrite_time=1,
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
                            handler_id="handler-02",
                            handler_type="USB_1608HS",
                            adc_serial_num="00003333",
                            sampling_frequency=100000,
                            sampling_ch_num=2,
                            filewrite_time=1,
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

        actual = DataRecorderService.read_binary_files(
            file=file,
            sequential_number=0,
            timestamp=Decimal(file.timestamp),
            data_collect_history=dummy_data_collect_history,
            displacement_sensor_id="stroke_displacement",
            sensor_ids_other_than_displacement=["load01", "load02", "load03", "load04"],
            sampling_interval=Decimal(1.0 / dummy_data_collect_history.sampling_frequency),
        )

        expected = (
            [
                {
                    "sequential_number": 0,
                    "timestamp": Decimal(file.timestamp),
                    "stroke_displacement": 10.0,
                    "load01": 1.1,
                    "load02": 2.2,
                    "load03": 3.3,
                    "load04": 4.4,
                },
                {
                    "sequential_number": 1,
                    "timestamp": Decimal(file.timestamp) + Decimal(0.00001),
                    "stroke_displacement": 9.0,
                    "load01": 1.2,
                    "load02": 2.3,
                    "load03": 3.4,
                    "load04": 4.5,
                },
            ],
            2,
            Decimal(file.timestamp) + Decimal(0.00001) + Decimal(0.00001),
        )

        assert actual == expected


class TestRecord:
    @pytest.fixture
    def init(self) -> None:
        self.machine_id: str = "test-machine-01"
        self.gateway_id: str = "test-gateway-01"
        self.handler_id: str = "test-handler-01"
        self.handler_id_2: str = "test-handler-02"

    @pytest.mark.skip(reason="ジョブ実行のみ（デバッグ用）")
    def test_exec(self, db, init, mocker):
        """ジョブ実行のみ（デバッグ用）
        通常はコメントアウト
        """

        data_dir = os.environ["data_dir"]
        dir_path = os.path.join(data_dir, self.machine_id + "-20211111110000")

        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.mkdir(dir_path)

        mocker.patch.object(DataRecorderService, "get_collect_status", return_value="setup")

        # DataRecorderService.record(db, self.machine_id, self.gateway_id, self.handler_id)
        DataRecorderService.record(db, self.machine_id, self.gateway_id, self.handler_id_2)

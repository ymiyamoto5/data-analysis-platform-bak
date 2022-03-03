"""
 ==================================
  test_data_recorder.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_detail import DataCollectHistorySensor
from backend.app.models.data_collect_history_event import DataCollectHistoryEvent
from backend.app.services.data_recorder_service import DataRecorderService
from backend.common import common
from backend.file_manager.file_manager import FileManager


class TestReadBinaryFiles:
    def test_normal(self, dat_files):
        """正常系：バイナリファイルが正常に読めること"""

        machine_id: str = "test-machine-01"

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
            data_collect_history_sensors=[
                DataCollectHistorySensor(
                    sensor_id="stroke_displacement",
                    sensor_name="ストローク変位",
                    sensor_type_id="stroke_displacement",
                    slope=1.0,
                    intercept=0.0,
                ),
                DataCollectHistorySensor(
                    sensor_id="load01",
                    sensor_name="load01",
                    sensor_type_id="load",
                    slope=1.0,
                    intercept=0.0,
                ),
                DataCollectHistorySensor(
                    sensor_id="load02",
                    sensor_name="load02",
                    sensor_type_id="load",
                    slope=1.0,
                    intercept=0.0,
                ),
                DataCollectHistorySensor(
                    sensor_id="load03",
                    sensor_name="load03",
                    sensor_type_id="load",
                    slope=1.0,
                    intercept=0.0,
                ),
                DataCollectHistorySensor(
                    sensor_id="load04",
                    sensor_name="load04",
                    sensor_type_id="load",
                    slope=1.0,
                    intercept=0.0,
                ),
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
        self.machine_id = "test-machine-01"

    # def test_exec(self, db, init):
    #     """ジョブ実行のみ（デバッグ用）
    #     通常はコメントアウト
    #     """
    #     DataRecorderService.record(db, self.machine_id)

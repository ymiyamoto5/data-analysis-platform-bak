"""
 ==================================
  test_data_recorder.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

from datetime import datetime, timedelta

import pytest
from backend.common.common import TIMESTAMP_MAX
from backend.data_recorder.data_recorder import DataRecorder
from backend.elastic_manager.elastic_manager import ElasticManager
from backend.file_manager.file_manager import FileManager


class TestGetTargetInterval:
    def test_setup_end_are_set(self):
        """start_timeとend_timeの設定が正しく行われること"""

        setup_time: datetime = datetime.now()
        setup_time_str: str = datetime.isoformat(setup_time)
        end_time: datetime = setup_time + timedelta(seconds=30)
        end_time_str: str = datetime.isoformat(end_time)

        events = [
            {"event_type": "setup", "occurred_time": setup_time_str},
            {"event_type": "stop", "occurred_time": end_time_str},
        ]

        dr = DataRecorder(machine_id="machine-01")
        actual = dr._get_target_interval(events)

        expected = (setup_time.timestamp(), end_time.timestamp() + 5.0)

        assert actual == expected

    def test_end_is_not_set(self):
        """setup_timeのみが設定されている場合、end_timeはmaxとして設定される"""

        setup_time: datetime = datetime.now()
        setup_time_str: str = datetime.isoformat(setup_time)

        events = [
            {"event_type": "setup", "occurred_time": setup_time_str},
        ]

        dr = DataRecorder(machine_id="machine-01")

        actual = dr._get_target_interval(events)

        expected = (setup_time.timestamp(), TIMESTAMP_MAX)

        assert actual == expected

    def test_is_not_setuped(self):
        """setup_time, end_timeが設定されていないときは、対象区間は (None, None) となる。"""

        dr = DataRecorder(machine_id="machine-01")

        events = []

        with pytest.raises(SystemExit):
            dr._get_target_interval(events)


class TestSetTimestamp:
    def test_first_process(self, mocker):
        """正常系：データ収集開始後、最初のプロセス"""

        machine_id: str = "machine-01"
        dr = DataRecorder(machine_id=machine_id)

        mocker.patch.object(ElasticManager, "get_docs", return_value=[])
        started_timestamp: float = datetime(2020, 12, 16, 8, 0, 58, 0).timestamp()

        actual: float = dr._set_timestamp(rawdata_index="tmp", started_timestamp=started_timestamp)
        expected: float = started_timestamp

        assert actual == expected

    def test_not_first_prcess(self, mocker):
        """正常系：データ収集開始後、2回目以降のプロセス"""

        machine_id: str = "machine-01"
        dr = DataRecorder(machine_id=machine_id)

        return_value = [{"timestamp": datetime(2020, 12, 16, 8, 1, 58, 0).timestamp()}]

        mocker.patch.object(ElasticManager, "get_docs", return_value=return_value)
        started_timestamp: float = datetime(2020, 12, 16, 8, 0, 58, 0).timestamp()

        actual: float = dr._set_timestamp(rawdata_index="tmp", started_timestamp=started_timestamp)
        # 前回プロセスで記録された最新生データのタイムスタンプに10マイクロ秒加算した値
        expected: float = datetime(2020, 12, 16, 8, 1, 58, 10).timestamp()

        assert actual == expected


class TestReadBinaryFiles:
    def test_normal(self, dat_files):
        """正常系：バイナリファイルが正常に読めること"""

        machine_id: str = "machine-01"
        dr = DataRecorder(machine_id=machine_id)

        file_infos = FileManager.create_files_info(dat_files.tmp_path._str, machine_id, "dat")
        file = file_infos[0]

        actual = dr._read_binary_files(file=file, sequential_number=0, timestamp=file.timestamp)

        expected = (
            [
                {
                    "sequential_number": 0,
                    "timestamp": file.timestamp,
                    "displacement": 10.0,
                    "load01": 1.1,
                    "load02": 2.2,
                    "load03": 3.3,
                    "load04": 4.4,
                },
                {
                    "sequential_number": 1,
                    "timestamp": file.timestamp + 0.000010,
                    "displacement": 9.0,
                    "load01": 1.2,
                    "load02": 2.3,
                    "load03": 3.4,
                    "load04": 4.5,
                },
            ],
            2,
            file.timestamp + 0.000010 + 0.000010,
        )

        assert actual == expected

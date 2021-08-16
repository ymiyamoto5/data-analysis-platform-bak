"""
 ==================================
  test_data_recorder.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import pytest
import pathlib
from datetime import datetime, timedelta
from backend.data_recorder.data_recorder import DataRecorder
from backend.elastic_manager.elastic_manager import ElasticManager
from backend.common.common import TIMESTAMP_MAX
from backend.common.dao import HandlerDAO
from backend.data_collect_manager.models.handler import Handler


class TestCreateFileTimestamp:
    def test_normal(self, mocker):
        """ファイル名からdatetime型のタイムスタンプを生成出来ること"""

        filepath = "tmp00/AD-00_20201216-080058.620753.dat"

        mocker.patch.object(
            HandlerDAO,
            "fetch_handler",
            return_value=Handler(
                sampling_ch_num=5,
                sampling_frequency=100_000,
            ),
        )

        dr = DataRecorder(machine_id="001")

        actual = dr._create_file_timestamp(filepath)
        expected = datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()

        assert actual == expected


class TestGetTargetInterval:
    def test_setup_end_are_set(self, mocker):
        """start_timeとend_timeの設定が正しく行われること"""

        setup_time: datetime = datetime.now()
        setup_time_str: str = datetime.isoformat(setup_time)
        end_time: datetime = setup_time + timedelta(seconds=30)
        end_time_str: str = datetime.isoformat(end_time)

        events = [
            {"event_type": "setup", "occurred_time": setup_time_str},
            {"event_type": "stop", "occurred_time": end_time_str},
        ]

        actual = data_recorder._get_target_interval(events)

        expected = (setup_time.timestamp(), end_time.timestamp() + 5.0)

        assert actual == expected

    def test_end_is_not_set(self):
        """setup_timeのみが設定されている場合、end_timeはmaxとして設定される"""

        setup_time: datetime = datetime.now()
        setup_time_str: str = datetime.isoformat(setup_time)

        events = [
            {"event_type": "setup", "occurred_time": setup_time_str},
        ]

        actual = data_recorder._get_target_interval(events)

        expected = (setup_time.timestamp(), TIMESTAMP_MAX)

        assert actual == expected

    def test_is_not_setuped(self):
        """setup_time, end_timeが設定されていないときは、対象区間は (None, None) となる。"""

        events = []

        with pytest.raises(SystemExit):
            data_recorder._get_target_interval(events)


class TestCreateFilesInfo:
    def test_normal_file_exists(self, dat_files):
        """正常系：ファイルが存在する"""

        actual = data_recorder._create_files_info(dat_files.tmp_path._str)

        expected = [
            data_recorder.FileInfo(dat_files.tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 59, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_3._str, datetime(2020, 12, 16, 8, 1, 0, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_4._str, datetime(2020, 12, 16, 8, 1, 1, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_5._str, datetime(2020, 12, 16, 8, 1, 2, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_file_exists_not_sorted(self, tmp_path):
        """正常系：ファイルが存在する。ファイルが名前の昇順にソートされること"""

        tmp_dat_1: pathlib.Path = tmp_path / "AD-00_20201216-080058.620753.dat"
        tmp_dat_2: pathlib.Path = tmp_path / "AD-00_20201216-080040.620753.dat"
        tmp_dat_3: pathlib.Path = tmp_path / "AD-00_20201210-080100.620753.dat"

        tmp_dat_1.write_text("")
        tmp_dat_2.write_text("")
        tmp_dat_3.write_text("")

        actual = data_recorder._create_files_info(tmp_path._str)

        expected = [
            data_recorder.FileInfo(tmp_dat_3._str, datetime(2020, 12, 10, 8, 1, 0, 620753).timestamp()),
            data_recorder.FileInfo(tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 40, 620753).timestamp()),
            data_recorder.FileInfo(tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_file_not_exists(self):
        """正常系：ファイルが存在しない。"""

        actual = data_recorder._create_files_info("dummy_path")

        expected = None

        assert actual == expected


class TestGetTargetFiles:
    def test_normal_target_file_exists(self, dat_files):
        """正常系：5ファイル中3ファイルが対象範囲。以下2ファイルが対象外。
        1ファイル目：20201216-080058.620753
        5ファイル目：20201216-080102.620753
        """

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        setup_time = datetime(2020, 12, 16, 8, 0, 59, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 2, 0).timestamp()
        actual = data_recorder._get_target_files(file_infos, setup_time, end_time)

        expected = [
            data_recorder.FileInfo(dat_files.tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 59, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_3._str, datetime(2020, 12, 16, 8, 1, 0, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_4._str, datetime(2020, 12, 16, 8, 1, 1, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_no_target_file(self, dat_files):
        """正常系：対象ファイルなし"""

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        setup_time = datetime(2020, 12, 16, 8, 1, 3, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 5, 0).timestamp()
        actual = data_recorder._get_target_files(file_infos, setup_time, end_time)

        expected = []

        assert actual == expected


class TestGetNotTargetFiles:
    def test_normal_not_target_file_exists(self, dat_files):
        """正常系：5ファイル中3ファイルが対象範囲外。以下2ファイルが対象外。
        1ファイル目：20201216-080058.620753
        5ファイル目：20201216-080102.620753
        """

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        setup_time = datetime(2020, 12, 16, 8, 0, 59, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 2, 0).timestamp()
        actual = data_recorder._get_not_target_files(file_infos, setup_time, end_time)

        expected = [
            data_recorder.FileInfo(dat_files.tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_5._str, datetime(2020, 12, 16, 8, 1, 2, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_all_files_are_target(self, dat_files):
        """正常系：すべて対象ファイル（対象外ファイルなし）"""

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        setup_time = datetime(2020, 12, 16, 8, 0, 58, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 10, 0).timestamp()
        actual = data_recorder._get_not_target_files(file_infos, setup_time, end_time)

        expected = []

        assert actual == expected


class TestSetTimestamp:
    def test_first_process(self, mocker):
        """正常系：データ収集開始後、最初のプロセス"""

        mocker.patch.object(ElasticManager, "get_docs", return_value=[])
        started_timestamp: float = datetime(2020, 12, 16, 8, 0, 58, 0).timestamp()

        actual: float = data_recorder._set_timestamp(rawdata_index="tmp", started_timestamp=started_timestamp)
        expected: float = started_timestamp

        assert actual == expected

    def test_not_first_prcess(self, mocker):
        """正常系：データ収集開始後、2回目以降のプロセス"""

        return_value = [{"timestamp": datetime(2020, 12, 16, 8, 1, 58, 0).timestamp()}]

        mocker.patch.object(ElasticManager, "get_docs", return_value=return_value)
        started_timestamp: float = datetime(2020, 12, 16, 8, 0, 58, 0).timestamp()

        actual: float = data_recorder._set_timestamp(rawdata_index="tmp", started_timestamp=started_timestamp)
        # 前回プロセスで記録された最新生データのタイムスタンプに10マイクロ秒加算した値
        expected: float = datetime(2020, 12, 16, 8, 1, 58, 10).timestamp()

        assert actual == expected


class TestReadBinaryFiles:
    def test_normal(self, dat_files):
        """正常系：バイナリファイルが正常に読めること"""

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)
        file = file_infos[0]

        actual = data_recorder._read_binary_files(file=file, sequential_number=0, timestamp=file.timestamp)

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

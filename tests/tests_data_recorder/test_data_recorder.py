import pytest
import pathlib
from datetime import datetime, timedelta

from data_recorder import data_recorder
import utils.common as common


class TestCreateFileTimestamp:
    def test_normal(self):
        """ ファイル名からdatetime型のタイムスタンプを生成出来ること """

        filepath = "tmp00/AD-00_20201216-080058.620753.dat"

        actual = data_recorder._create_file_timestamp(filepath)
        expected = datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()

        assert actual == expected


class TestGetTargetInterval:
    def test_start_end_are_set(self):
        """ start_timeとend_timeの設定が正しく行われること """

        start_time: datetime = datetime.now()
        start_time_str: str = datetime.isoformat(start_time)
        end_time: datetime = start_time + timedelta(seconds=30)
        end_time_str: str = datetime.isoformat(end_time)

        events = [
            {"event_type": "start", "occurred_time": start_time_str},
            {"event_type": "stop", "occurred_time": end_time_str},
        ]

        actual = data_recorder._get_target_interval(events)

        expected = (start_time.timestamp(), end_time.timestamp())

        assert actual == expected

    def test_end_is_not_set(self):
        """ start_timeのみが設定されている場合、end_timeはmaxとして設定される """

        start_time: datetime = datetime.now()
        start_time_str: str = datetime.isoformat(start_time)

        events = [
            {"event_type": "start", "occurred_time": start_time_str},
        ]

        actual = data_recorder._get_target_interval(events)

        expected = (start_time.timestamp(), datetime.max.timestamp())

        assert actual == expected

    def test_is_not_started(self):
        """ start_time, end_timeが設定されていないときは、対象区間は (None, None) となる。"""

        events = []

        with pytest.raises(SystemExit):
            data_recorder._get_target_interval(events)


class TestCreateFilesInfo:
    def test_normal_file_exists(self, dat_files):
        """ 正常系：ファイルが存在する """

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
        """ 正常系：ファイルが存在する。ファイルが名前の昇順にソートされること """

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
        """ 正常系：ファイルが存在しない。 """

        actual = data_recorder._create_files_info("dummy_path")

        expected = None

        assert actual == expected


class TestGetTargetFiles:
    def test_normal_target_file_exists(self, dat_files):
        """ 正常系：5ファイル中3ファイルが対象範囲。以下2ファイルが対象外。
            1ファイル目：20201216-080058.620753
            5ファイル目：20201216-080102.620753
        """

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        start_time = datetime(2020, 12, 16, 8, 0, 59, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 2, 0).timestamp()
        actual = data_recorder._get_target_files(file_infos, start_time, end_time)

        expected = [
            data_recorder.FileInfo(dat_files.tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 59, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_3._str, datetime(2020, 12, 16, 8, 1, 0, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_4._str, datetime(2020, 12, 16, 8, 1, 1, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_no_target_file(self, dat_files):
        """ 正常系：対象ファイルなし """

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        start_time = datetime(2020, 12, 16, 8, 1, 3, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 5, 0).timestamp()
        actual = data_recorder._get_target_files(file_infos, start_time, end_time)

        expected = []

        assert actual == expected


class TestGetNotTargetFiles:
    def test_normal_not_target_file_exists(self, dat_files):
        """ 正常系：5ファイル中3ファイルが対象範囲外。以下2ファイルが対象外。
            1ファイル目：20201216-080058.620753
            5ファイル目：20201216-080102.620753
        """

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        start_time = datetime(2020, 12, 16, 8, 0, 59, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 2, 0).timestamp()
        actual = data_recorder._get_not_target_files(file_infos, start_time, end_time)

        expected = [
            data_recorder.FileInfo(dat_files.tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_5._str, datetime(2020, 12, 16, 8, 1, 2, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_all_files_are_target(self, dat_files):
        """ 正常系：すべて対象ファイル（対象外ファイルなし） """

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        start_time = datetime(2020, 12, 16, 8, 0, 58, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 10, 0).timestamp()
        actual = data_recorder._get_not_target_files(file_infos, start_time, end_time)

        expected = []

        assert actual == expected

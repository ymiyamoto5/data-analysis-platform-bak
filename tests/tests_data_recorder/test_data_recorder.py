import pytest
import pathlib
from datetime import datetime, timedelta

from data_recorder import data_recorder


class TestCreateFileTimestamp:
    def test_normal(self):
        """ ファイル名からdatetime型のタイムスタンプを生成出来ること """

        filepath = "tmp00/AD-00_20201216-080058.620753.dat"

        actual = data_recorder._create_file_timestamp(filepath)
        expected = datetime(2020, 12, 16, 8, 0, 58, 620753)

        assert actual == expected


class TestGetTargetInterval:
    def test_start_end_are_set(self):
        """ start_timeとend_timeの設定が正しく行われること """

        start_time: datetime = datetime.now()
        start_time_str: str = datetime.strftime(start_time, "%Y%m%d%H%M%S%f")
        end_time: datetime = start_time + timedelta(seconds=30)
        end_time_str: str = datetime.strftime(end_time, "%Y%m%d%H%M%S%f")

        config = {"start_time": start_time_str, "end_time": end_time_str}

        actual = data_recorder._get_target_interval(config)

        expected = (start_time, end_time)

        assert actual == expected

    def test_end_is_not_set(self):
        """ start_timeのみが設定されている場合、end_timeはmaxとして設定される """

        start_time: datetime = datetime.now()
        start_time_str: str = datetime.strftime(start_time, "%Y%m%d%H%M%S%f")

        config = {"start_time": start_time_str}

        actual = data_recorder._get_target_interval(config)

        expected = (start_time, datetime.max)

        assert actual == expected

    def test_is_not_started(self):
        """ start_time, end_timeが設定されていないときは、対象区間は (None, None) となる。"""

        config = {}

        actual = data_recorder._get_target_interval(config)

        expected = (None, None)

        assert actual == expected

    def test_start_bigger_than_end(self):
        """ start_time > end_timeの場合、不正な値 """

        start_time: datetime = datetime.now()
        start_time_str: str = datetime.strftime(start_time, "%Y%m%d%H%M%S%f")
        end_time: datetime = start_time - timedelta(seconds=30)
        end_time_str: str = datetime.strftime(end_time, "%Y%m%d%H%M%S%f")

        config = {"start_time": start_time_str, "end_time": end_time_str}

        with pytest.raises(ValueError) as excinfo:
            data_recorder._get_target_interval(config)
            exception_message = excinfo.value.args[0]
            assert exception_message == "start_time({start_time}) > end_time({end_time}). This is abnormal condition."


class TestCreateFilesInfo:
    def test_normal_file_exists(self, dat_files):
        """ 正常系：ファイルが存在する """

        actual = data_recorder._create_files_info(dat_files.tmp_path._str)

        expected = [
            data_recorder.FileInfo(dat_files.tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753)),
            data_recorder.FileInfo(dat_files.tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 59, 620753)),
            data_recorder.FileInfo(dat_files.tmp_dat_3._str, datetime(2020, 12, 16, 8, 1, 0, 620753)),
            data_recorder.FileInfo(dat_files.tmp_dat_4._str, datetime(2020, 12, 16, 8, 1, 1, 620753)),
            data_recorder.FileInfo(dat_files.tmp_dat_5._str, datetime(2020, 12, 16, 8, 1, 2, 620753)),
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
            data_recorder.FileInfo(tmp_dat_3._str, datetime(2020, 12, 10, 8, 1, 0, 620753)),
            data_recorder.FileInfo(tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 40, 620753)),
            data_recorder.FileInfo(tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753)),
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

        start_time = datetime(2020, 12, 16, 8, 0, 59, 0)
        end_time = datetime(2020, 12, 16, 8, 1, 2, 0)
        actual = data_recorder._get_target_files(file_infos, start_time, end_time)

        expected = [
            data_recorder.FileInfo(dat_files.tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 59, 620753)),
            data_recorder.FileInfo(dat_files.tmp_dat_3._str, datetime(2020, 12, 16, 8, 1, 0, 620753)),
            data_recorder.FileInfo(dat_files.tmp_dat_4._str, datetime(2020, 12, 16, 8, 1, 1, 620753)),
        ]

        assert actual == expected

    def test_normal_no_target_file(self, dat_files):
        """ 正常系：対象ファイルなし """

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        start_time = datetime(2020, 12, 16, 8, 1, 3, 0)
        end_time = datetime(2020, 12, 16, 8, 1, 5, 0)
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

        start_time = datetime(2020, 12, 16, 8, 0, 59, 0)
        end_time = datetime(2020, 12, 16, 8, 1, 2, 0)
        actual = data_recorder._get_not_target_files(file_infos, start_time, end_time)

        expected = [
            data_recorder.FileInfo(dat_files.tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753)),
            data_recorder.FileInfo(dat_files.tmp_dat_5._str, datetime(2020, 12, 16, 8, 1, 2, 620753)),
        ]

        assert actual == expected

    def test_normal_all_files_are_target(self, dat_files):
        """ 正常系：すべて対象ファイル（対象外ファイルなし） """

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        start_time = datetime(2020, 12, 16, 8, 0, 58, 0)
        end_time = datetime(2020, 12, 16, 8, 1, 10, 0)
        actual = data_recorder._get_not_target_files(file_infos, start_time, end_time)

        expected = []

        assert actual == expected

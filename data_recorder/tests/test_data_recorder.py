import pytest
import json
from datetime import datetime, timedelta

from .. import data_recorder


class TestCreateFileTimestamp:
    def test_normal(self):
        """ ファイル名からdatetime型のタイムスタンプを生成出来ること """

        filepath = "tmp00/AD-00_20201216-080058.620753.dat"

        actual = data_recorder._create_file_timestamp(filepath)
        expected = datetime(2020, 12, 16, 8, 0, 58, 620753)

        assert actual == expected


class TestGetTargetInterval:
    @pytest.fixture(autouse=True)
    def app_config(self, tmp_path):
        """ app_configの生成Fixture。app_configにはconfigファイルのパスとdataディレクトリのパスを持つ。 """

        app_config = tmp_path / "app_config.json"
        config_params = {"config_file_path": str(tmp_path) + "/tmp.cnf", "data_dir": str(tmp_path) + "/data"}
        app_config.write_text(json.dumps(config_params))

        yield

    def test_start_end_are_set(self, tmp_path):
        """ start_timeとend_timeの設定が正しく行われること """

        start_time: datetime = datetime.now()
        start_time_str: str = datetime.strftime(start_time, "%Y%m%d%H%M%S%f")
        end_time: datetime = start_time + timedelta(seconds=30)
        end_time_str: str = datetime.strftime(end_time, "%Y%m%d%H%M%S%f")

        tmp_config_file = tmp_path / "tmp.cnf"
        config = {"start_time": start_time_str, "end_time": end_time_str}
        tmp_config_file.write_text(json.dumps(config))

        actual = data_recorder._get_target_interval(tmp_config_file)

        expected = (start_time, end_time)

        assert actual == expected

    def test_end_is_not_set(self, tmp_path):
        """ start_timeのみが設定されている場合、end_timeはmaxとして設定される """

        start_time: datetime = datetime.now()
        start_time_str: str = datetime.strftime(start_time, "%Y%m%d%H%M%S%f")

        tmp_config_file = tmp_path / "tmp.cnf"
        config = {"start_time": start_time_str}
        tmp_config_file.write_text(json.dumps(config))

        actual = data_recorder._get_target_interval(tmp_config_file)

        expected = (start_time, datetime.max)

        assert actual == expected

    def test_is_not_started(self, tmp_path):
        """ start_time, end_timeが設定されていないときは、対象区間は (None, None) となる。"""

        tmp_config_file = tmp_path / "tmp.cnf"
        config = {}
        tmp_config_file.write_text(json.dumps(config))

        actual = data_recorder._get_target_interval(tmp_config_file)

        expected = (None, None)

        assert actual == expected

    def test_start_bigger_than_end(self, tmp_path):
        """ start_time > end_timeの場合、不正な値 """

        start_time: datetime = datetime.now()
        start_time_str: str = datetime.strftime(start_time, "%Y%m%d%H%M%S%f")
        end_time: datetime = start_time - timedelta(seconds=30)
        end_time_str: str = datetime.strftime(end_time, "%Y%m%d%H%M%S%f")

        tmp_config_file = tmp_path / "tmp.cnf"
        config = {"start_time": start_time_str, "end_time": end_time_str}
        tmp_config_file.write_text(json.dumps(config))

        with pytest.raises(ValueError) as excinfo:
            data_recorder._get_target_interval(tmp_config_file)
            exception_message = excinfo.value.args[0]
            assert exception_message == "start_time({start_time}) > end_time({end_time}). This is abnormal condition."


class TestCreateFilesInfo:
    def test_file_exists(self, tmp_path):
        """ datファイル生成 """

        tmp_dat_1 = tmp_path / "AD-00_20201216-080058.620753.dat"
        tmp_dat_2 = tmp_path / "AD-00_20201216-080059.620753.dat"
        tmp_dat_3 = tmp_path / "AD-00_20201216-080100.620753.dat"

        tmp_dat_1.write_text("")
        tmp_dat_2.write_text("")
        tmp_dat_3.write_text("")

        actual = data_recorder._create_files_info(tmp_path._str)

        expected = [
            data_recorder.FileInfo(tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753)),
            data_recorder.FileInfo(tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 59, 620753)),
            data_recorder.FileInfo(tmp_dat_3._str, datetime(2020, 12, 16, 8, 1, 0, 620753)),
        ]

        assert actual == expected

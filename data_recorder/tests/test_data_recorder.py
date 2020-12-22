import pytest
import json
from datetime import datetime, timedelta

from .. import data_recorder


def test_create_file_timestamp():
    filename = "AD-00_20201216-080058.620753.dat"

    actual = data_recorder._create_file_timestamp(filename)
    expected = datetime(2020, 12, 16, 8, 0, 58, 620753)

    assert actual == expected


def test_get_target_interval_start_end_are_set(tmp_path):
    tmp_settings_file = tmp_path / "settings.json"
    settings = {"config_file_path": str(tmp_path) + "/tmp.cnf"}
    tmp_settings_file.write_text(json.dumps(settings))

    start_time: datetime = datetime.now()
    start_time_str: str = datetime.strftime(start_time, "%Y%m%d%H%M%S%f")
    end_time: datetime = start_time + timedelta(seconds=30)
    end_time_str: str = datetime.strftime(end_time, "%Y%m%d%H%M%S%f")

    tmp_config_file = tmp_path / "tmp.cnf"
    config = {"start_time": start_time_str, "end_time": end_time_str}
    tmp_config_file.write_text(json.dumps(config))

    actual = data_recorder._get_target_interval(tmp_settings_file)

    expected = (start_time, end_time)

    assert actual == expected


def test_get_target_interval_end_is_not_set(tmp_path):
    tmp_settings_file = tmp_path / "settings.json"
    settings = {"config_file_path": str(tmp_path) + "/tmp.cnf"}
    tmp_settings_file.write_text(json.dumps(settings))

    start_time: datetime = datetime.now()
    start_time_str: str = datetime.strftime(start_time, "%Y%m%d%H%M%S%f")

    tmp_config_file = tmp_path / "tmp.cnf"
    config = {"start_time": start_time_str}
    tmp_config_file.write_text(json.dumps(config))

    actual = data_recorder._get_target_interval(tmp_settings_file)

    expected = (start_time, datetime.max)

    assert actual == expected


def test_get_target_interval_is_not_started(tmp_path):
    tmp_settings_file = tmp_path / "settings.json"
    settings = {"config_file_path": str(tmp_path) + "/tmp.cnf"}
    tmp_settings_file.write_text(json.dumps(settings))

    tmp_config_file = tmp_path / "tmp.cnf"
    config = {}
    tmp_config_file.write_text(json.dumps(config))

    actual = data_recorder._get_target_interval(tmp_settings_file)

    expected = (None, None)

    assert actual == expected


def test_get_target_interval_start_bigger_than_end(tmp_path):
    tmp_settings_file = tmp_path / "settings.json"
    settings = {"config_file_path": str(tmp_path) + "/tmp.cnf"}
    tmp_settings_file.write_text(json.dumps(settings))

    start_time: datetime = datetime.now()
    start_time_str: str = datetime.strftime(start_time, "%Y%m%d%H%M%S%f")
    end_time: datetime = start_time - timedelta(seconds=30)
    end_time_str: str = datetime.strftime(end_time, "%Y%m%d%H%M%S%f")

    tmp_config_file = tmp_path / "tmp.cnf"
    config = {"start_time": start_time_str, "end_time": end_time_str}
    tmp_config_file.write_text(json.dumps(config))

    with pytest.raises(ValueError):
        data_recorder._get_target_interval(tmp_settings_file)


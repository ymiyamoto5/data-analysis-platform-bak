import json
from datetime import datetime

from .. import data_recorder


def test_create_file_timestamp():
    filename = "AD-00_20201216-080058.620753.dat"

    acutal = data_recorder._create_file_timestamp(filename)
    expected = datetime(2020, 12, 16, 8, 0, 58, 620753)

    assert expected == acutal


def test_get_target_interval(tmp_path):
    tmp_settings_file = tmp_path / "settings.json"
    settings = {"config_file_path": str(tmp_path) + "/tmp.cnf"}
    tmp_settings_file.write_text(json.dumps(settings))

    tmp_config_file = tmp_path / "tmp.cnf"
    config = {}
    tmp_config_file.write_text(json.dumps(config))

    actual = data_recorder._get_target_interval(tmp_settings_file)

    expected = (None, None)

    assert expected == actual

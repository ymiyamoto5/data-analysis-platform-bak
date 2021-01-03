import os
import pytest
import json
from ..models.config_file_manager import ConfigFileManager


@pytest.fixture()
def config_file(tmp_path):
    config_file = tmp_path / "conf_Gw-00.cnf"

    config: dict = {
        "sequence_number": 10,
        "gateway_result": 0,
        "status": "stop",
        "gateway_id": "Gw-00",
        "Log_Level": 5,
        "ADC_0": {
            "handler_id": "AD-00",
            "handler_type": "USB_1608HS",
            "ADC_SerialNum": "01234567",
            "sampling_frequency": 100000,
            "sampling_chnum": 5,
            "filewrite_time": 3600,
        },
    }

    config_file.write(json.dumps(config))

    yield


class TestDumpConfigFile:
    def test_normal(self, tmp_path):
        app_config = tmp_path / "app_config.json"
        cfm = ConfigFileManager(app_config)

        config: dict = {
            "sequence_number": 10,
            "gateway_result": 0,
            "status": "stop",
            "gateway_id": "Gw-00",
            "Log_Level": 5,
            "ADC_0": {
                "handler_id": "AD-00",
                "handler_type": "USB_1608HS",
                "ADC_SerialNum": "01234567",
                "sampling_frequency": 100000,
                "sampling_chnum": 5,
                "filewrite_time": 3600,
            },
            "start_time": "20201201010005000000",
            "end_time": "20201201013545000000",
        }

        actual: bool = cfm._dump_config_file(config)

        expected: bool = True

        assert actual == expected

        # config_file_path = tmp_path / "conf_Gw-00.cnf"
        # data_dir = tmp_path / "data"
        # data_dir.mkdir()

        # config: dict = {"config_file_path": config_file_path, "data_dir": data_dir._str}
        # json.dumps(config)


# def test_is_exists_config_file_not_exists():
#     """ config fileの存在確認。ない場合 """

#     cfm = ConfigFileManager("")
#     assert cfm.check_file_exists() is False


# def test_is_exists_config_file_already_exists(tmp_path):
#     """ config fileの存在確認。すでにある場合 """

#     tmp_file = tmp_path / "tmp.cnf"
#     tmp_file.write_text("temporary...")

#     cfm = ConfigFileManager(tmp_file._str)
#     assert cfm.check_file_exists() is True


# def test_create_config(tmp_path):
#     """ configの作成 """

#     tmp_file = tmp_path / "conf_GW-00.cnf"


# def test_create_running_file_already_exits():
#     """ すでにRunning Fileがある場合 """
#     pass

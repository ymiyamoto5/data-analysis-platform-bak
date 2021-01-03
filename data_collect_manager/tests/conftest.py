import pytest
import json


@pytest.fixture
def app_config_file(tmp_path):
    """ app_config.json の fixture """

    config_file_path = tmp_path / "conf_Gw-00.cnf"
    config_file_path.write_text("")

    data_dir = tmp_path / "data"
    data_dir.mkdir()

    app_config: dict = {"config_file_path": config_file_path._str, "data_dir": data_dir._str}
    app_config_str: str = json.dumps(app_config, indent=2, ensure_ascii=False)

    app_config_file = tmp_path / "app_config.json"
    app_config_file.write_text(app_config_str)

    yield app_config_file._str


@pytest.fixture
def config_file(tmp_path):
    """ .cnfファイルの fixture """

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

    config_file.write_text(json.dumps(config))

    yield config_file._str

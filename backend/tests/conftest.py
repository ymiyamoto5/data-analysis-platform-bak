"""
 ==================================
  conftest.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import json
import os
import pathlib
import sys

import pytest

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../backend/"))


@pytest.fixture
def app_config_file(tmp_path):
    """app_config.json の fixture"""

    data_dir: pathlib.PosixPath = tmp_path / "data"
    data_dir.mkdir()

    app_config: dict = {"data_dir": data_dir._str}
    app_config_str: str = json.dumps(app_config, indent=2, ensure_ascii=False)

    app_config_file: pathlib.PosixPath = tmp_path / "app_config.json"
    app_config_file.write_text(app_config_str)

    yield app_config_file


@pytest.fixture
def config_file(tmp_path):
    """.cnfファイルの fixture"""

    config_file: pathlib.PosixPath = tmp_path / "tmp.cnf"

    config: dict = {
        "sequence_number": 1,
        "gateway_result": 0,
        "status": "stop",
        "gateway_id": "Gw-00",
        "Log_Level": 5,
        "ADC_0": {
            "handler_id": "AD-00",
            "handler_type": "USB-1608HS",
            "ADC_SerialNum": "01234567",
            "sampling_frequency": 100000,
            "sampling_chnum": 5,
            "filewrite_time": 3600,
        },
    }

    config_file.write_text(json.dumps(config))

    yield config_file

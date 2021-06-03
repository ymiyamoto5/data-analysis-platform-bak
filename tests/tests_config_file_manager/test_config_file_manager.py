"""
 ==================================
  test_config_file_manager.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import builtins
import pytest
import json

from config_file_manager.config_file_manager import ConfigFileManager


class TestDumpConfigFile:
    def test_normal(self, app_config_file):
        """ configファイルが無い状態で新規作成できること。 """

        cfm = ConfigFileManager(app_config_file._str)

        config: dict = {"dummy_config": "dummy_config"}

        actual: bool = cfm._dump_config_file(config)
        expected: bool = True

        assert actual == expected

    def test_normal_file_already_exists(self, app_config_file, config_file):
        """ configファイルがすでに存在する状態で、上書きできること
            引数 config_file のfixtureでconfigファイルが生成される。
        """

        cfm = ConfigFileManager(app_config_file._str)

        config: dict = {"dummy_config": "dummy_config"}

        actual: bool = cfm._dump_config_file(config)
        expected: bool = True

        assert actual == expected

        with open(cfm.config_file_path, "r") as f:
            actual_config: dict = json.load(f)

        expected_config: dict = {"dummy_config": "dummy_config"}

        assert actual_config == expected_config

    def test_config_file_open_exception(self, mocker, app_config_file):
        """ 書き込みファイルのオープン失敗時、例外が発生しFalseが返ること。 """

        cfm = ConfigFileManager(app_config_file._str)

        config: dict = {"dummy_config": "dummy_config"}

        mocker.patch.object(builtins, "open", side_effect=Exception)
        with pytest.raises(Exception):
            cfm._dump_config_file(config)


class TestReadConfig:
    def test_normal(self, app_config_file, config_file):
        cfm = ConfigFileManager(app_config_file)

        actual: dict = cfm.read_config(config_file._str)

        expected: dict = {
            "sequence_number": 1,
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

        assert actual == expected


class TestCreate:
    def test_normal(self, app_config_file, config_file):
        cfm = ConfigFileManager(app_config_file)

        actual: bool = cfm.create(config_file._str)
        expected: bool = True

        assert actual == expected

    def test_initial_config_not_found_exception(self, app_config_file):
        """ 初期configファイルがない場合、Falseが返ること """

        cfm = ConfigFileManager(app_config_file._str)

        actual: bool = cfm.create("not_exists_file_path")
        expected: bool = False

        assert actual == expected

    def test_invalid_json_exception(self, app_config_file, config_file):
        """ 初期configファイルが不正なJSONだった場合、Falseが返ること """

        # 不正なJSONにする
        with open(config_file._str, "a") as f:
            f.write("{")

        cfm = ConfigFileManager(app_config_file._str)

        actual: bool = cfm.create(config_file._str)
        expected: bool = False

        assert actual == expected


class TestUpdate:
    def test_normal_change_status_to_running(self, app_config_file, config_file):
        """ configファイルを正常に更新できること。statusをrunningに変更。 """

        cfm = ConfigFileManager(app_config_file._str)

        params = {"status": "running"}

        actual: bool = cfm.update(params)
        expected: bool = True

        assert actual == expected

        with open(config_file._str, "r") as f:
            new_config: dict = json.load(f)

        assert new_config["sequence_number"] == 2  # initialが1のため、インクリメントされて2
        assert new_config["status"] == "running"

    def test_normal_change_status_to_stop(self, app_config_file, config_file):
        """ configファイルを正常に更新できること。statusをstopに変更。 """

        cfm = ConfigFileManager(app_config_file._str)

        params = {"status": "stop"}

        actual: bool = cfm.update(params)
        expected: bool = True

        assert actual == expected

        with open(config_file._str, "r") as f:
            new_config: dict = json.load(f)

        assert new_config["sequence_number"] == 2  # initialが1のため、インクリメントされて2
        assert new_config["status"] == "stop"

    def test_normal_sequence_number_overflow(self, app_config_file, config_file):
        """ sequence_numberが上限値に達した場合、ローリングされて1から開始されること """

        cfm = ConfigFileManager(app_config_file._str)

        # C言語でのint型上限値に書き換え
        with open(config_file._str, "r") as f:
            new_config: dict = json.load(f)
            new_config["sequence_number"] = 2_147_483_647
            json_str: str = json.dumps(new_config)
        with open(config_file._str, "w") as f:
            f.write(json_str)

        params = {"status": "running"}

        actual: bool = cfm.update(params)
        expected: bool = True

        assert actual == expected

        with open(config_file._str, "r") as f:
            new_config: dict = json.load(f)

        assert new_config["sequence_number"] == 1
        assert new_config["status"] == "running"


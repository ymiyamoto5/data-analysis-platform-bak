import pytest
import os
import json
from ..models.config_file_manager import ConfigFileManager


class TestDumpConfigFile:
    def test_normal(self, app_config_file):
        cfm = ConfigFileManager(app_config_file)

        config: dict = {"dummy_config": "dummy_config"}

        actual: bool = cfm._dump_config_file(config)
        expected: bool = True

        assert actual == expected

    def test_normal_file_already_exists(self, app_config_file, config_file):
        """ configファイルがすでに存在する状態で、上書きできること
            引数 config_file のfixtureでconfigファイルが生成される。
        """

        cfm = ConfigFileManager(app_config_file)

        config: dict = {"dummy_config": "dummy_config"}

        actual: bool = cfm._dump_config_file(config)
        expected: bool = True

        assert actual == expected

        with open(cfm.config_file_path, "r") as f:
            actual_config: dict = json.load(f)

        expected_config: dict = {"dummy_config": "dummy_config"}

        assert actual_config == expected_config

    def test_rename_exception(self, mocker, app_config_file):
        """ リネーム時の例外発生でFalseが返ること """

        mocker.patch.object(os, "rename", side_effect=OSError)

        cfm = ConfigFileManager(app_config_file)

        config: dict = {"dummy_config": "dummy_config"}

        actual: bool = cfm._dump_config_file(config)
        expected: bool = False

        assert actual == expected

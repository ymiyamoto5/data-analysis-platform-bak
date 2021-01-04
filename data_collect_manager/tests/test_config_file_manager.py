from _pytest.config import Config
from flask import app
import pytest
import os
import json
from datetime import datetime
from ..models.config_file_manager import ConfigFileManager


class TestDumpConfigFile:
    def test_normal(self, app_config_file):
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

    def test_rename_exception(self, mocker, app_config_file):
        """ リネーム時の例外発生でFalseが返ること """

        mocker.patch.object(os, "rename", side_effect=OSError)

        cfm = ConfigFileManager(app_config_file._str)

        config: dict = {"dummy_config": "dummy_config"}

        actual: bool = cfm._dump_config_file(config)
        expected: bool = False

        assert actual == expected


class TestCreate:
    def test_normal(self, config_file):
        cfm = ConfigFileManager()

        actual: bool = cfm.create(config_file._str)
        expected: bool = True

        assert actual == expected

    def test_initial_config_not_found_exception(self):
        """ 初期configファイルがない場合、Falseが返ること """

        cfm = ConfigFileManager()

        actual: bool = cfm.create("not_exists_file_path")
        expected: bool = False

        assert actual == expected

    def test_invalid_json_exception(self, config_file):
        """ 初期configファイルが不正なJSONだった場合、Falseが返ること """

        # 不正なJSONにする
        with open(config_file._str, "a") as f:
            f.write("{")

        cfm = ConfigFileManager()

        actual: bool = cfm.create(config_file._str)
        expected: bool = False

        assert actual == expected


class TestUpdate:
    def test_normal_change_sequence(self, app_config_file, config_file):
        """ configファイルを正常に更新できること。sequence_numberを書き換えるパターン。 """

        cfm = ConfigFileManager(app_config_file._str)

        start_time: str = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        params = {"status": "start", "start_time": start_time}

        actual: bool = cfm.update(params, should_change_sequence=True)
        expected: bool = True

        assert actual == expected

        with open(config_file._str, "r") as f:
            new_config: dict = json.load(f)

        assert new_config["status"] == "start"
        assert new_config["start_time"] == start_time


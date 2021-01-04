import pytest

from config_file_manager.config_file_manager import ConfigFileManager
from elastic_manager.elastic_manager import ElasticManager


class TestShowManager:
    def test_normal_config_file_not_exists(self, client, mocker):
        """ 正常系：configファイルが存在せず、作成するパターン。 """

        mocker.patch.object(ConfigFileManager, "config_exists", return_value=False)

        response = client.get("/")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"initial-view" in response.data

    def test_create_config_file_exception(self, client, mocker):
        """ 異常系：configファイルが存在せず、ファイル作成に失敗したパターン。"""

        mocker.patch.object(ConfigFileManager, "config_exists", return_value=False)
        mocker.patch.object(ConfigFileManager, "create", return_value=False)

        response = client.get("/")
        actual_code = response.status_code
        expected_code = 500

        assert actual_code == expected_code
        assert b'{"successful": false, "message": "config file create failed"}' in response.data

    def test_normal_latest_event_is_stop(self, client, mocker):
        """ 正常系：configファイルがすでに存在し、最新のevent_indexが存在するパターン。
            event_indexの最新ステータスはstopなので、前回の取得サイクルが正常に終了しており、初期画面に遷移。
        """

        mocker.patch.object(ConfigFileManager, "config_exists", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_event_index")
        mocker.patch.object(ElasticManager, "get_latest_events_index_doc", return_value={"event_type": "stop"})

        response = client.get("/")

        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"initial-view" in response.data

    def test_normal_latest_event_is_setup(self, client, mocker):
        """ 正常系：configファイルがすでに存在し、最新のevent_indexが存在するパターン。
            event_indexの最新ステータスはsetupなので、段取中画面に遷移。
        """

        mocker.patch.object(ConfigFileManager, "config_exists", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_event_index")
        mocker.patch.object(ElasticManager, "get_latest_events_index_doc", return_value={"event_type": "setup"})

        response = client.get("/")

        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"setup-view" in response.data


class TestSetup:
    def test_normal(self, client):

        response = client.post("/setup")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b'{"successful": true}' in response.data

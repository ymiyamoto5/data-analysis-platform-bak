import pytest
from typing import Tuple, Optional
from datetime import datetime, timedelta
import glob

from data_collect_manager import views
from config_file_manager.config_file_manager import ConfigFileManager
from elastic_manager.elastic_manager import ElasticManager


class TestInitializeConfigFile:
    def test_normal(self, mocker):
        """ 正常系 """

        mocker.patch.object(ConfigFileManager, "update", return_value=True)

        acutal: Tuple[bool, Optional[str]] = views._initialize_config_file()
        expected: Tuple[bool, Optional[str]] = True, None

        assert acutal == expected

        ConfigFileManager.update.assert_called_once()

    def test_config_file_update_fail_exception(self, mocker):
        """ 異常系：configファイルの更新失敗 """

        mocker.patch.object(ConfigFileManager, "update", return_value=False)

        acutal: Tuple[bool, Optional[str]] = views._initialize_config_file()
        expected: Tuple[bool, str] = False, "config file update failed."

        assert acutal == expected

        ConfigFileManager.update.assert_called_once()


class TestShowManager:
    def test_normal_config_file_not_exists(self, client, mocker):
        """ 正常系：configファイルが存在せず、作成するパターン。 """

        mocker.patch.object(ConfigFileManager, "config_exists", return_value=False)
        mocker.patch.object(ConfigFileManager, "create", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value=None)
        mocker.patch.object(ConfigFileManager, "update", return_value=True)

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

    def test_event_index_not_found_exception(self, client, mocker):
        """ 異常系：event_indexが存在しない場合、初期化処理をして初期画面に戻す。 """

        mocker.patch.object(ConfigFileManager, "config_exists", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value=None)
        mocker.patch.object(ConfigFileManager, "update", return_value=True)

        response = client.get("/")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"initial-view" in response.data

    def test_events_index_not_found_and_config_update_fail_exception(self, client, mocker):
        """ 異常系：最新のevents_indexが存在しない場合、初期化処理をして初期画面に戻す """

        mocker.patch.object(ConfigFileManager, "config_exists", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value=None)
        mocker.patch.object(ConfigFileManager, "update", return_value=True)

        response = client.get("/")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"initial-view" in response.data

    def test_events_index_dose_not_have_document_exception(self, client, mocker):
        """ 異常系：events_indexが存在するのに、documentがない場合 """

        mocker.patch.object(ConfigFileManager, "config_exists", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "get_latest_events_index_doc", return_value=None)
        mocker.patch.object(ConfigFileManager, "update", return_value=True)

        response = client.get("/")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"initial-view" in response.data

    def test_normal_latest_event_is_stop(self, client, mocker):
        """ 正常系：configファイルがすでに存在し、最新のevent_indexが存在するパターン。
            event_indexの最新ステータスはstopなので、前回の取得サイクルが正常に終了しており、初期画面に遷移。
        """

        mocker.patch.object(ConfigFileManager, "config_exists", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
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
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "get_latest_events_index_doc", return_value={"event_type": "setup"})

        response = client.get("/")

        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"setup-view" in response.data

    def test_normal_latest_event_is_start(self, client, mocker):
        """ 正常系：configファイルがすでに存在し、最新のevent_indexが存在するパターン。
            event_indexの最新ステータスがstartの場合、測定中画面に遷移。
        """

        mocker.patch.object(ConfigFileManager, "config_exists", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "get_latest_events_index_doc", return_value={"event_type": "start"})

        response = client.get("/")

        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"started-view" in response.data

    def test_normal_latest_event_is_tag(self, client, mocker):
        """ 正常系：configファイルがすでに存在し、最新のevent_indexが存在するパターン。
            event_indexの最新ステータスがtagの場合、測定中画面に遷移。
        """

        mocker.patch.object(ConfigFileManager, "config_exists", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "get_latest_events_index_doc", return_value={"event_type": "tag"})

        response = client.get("/")

        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"started-view" in response.data

    def test_normal_latest_event_is_pause_and_does_not_have_end_time(self, client, mocker):
        """ 正常系：configファイルがすでに存在し、最新のevent_indexが存在するパターン。
            event_indexの最新ステータスがpauseかつend_timeがない場合、中断中画面に遷移。
        """

        mocker.patch.object(ConfigFileManager, "config_exists", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        start_time: datetime = datetime.utcnow()
        mocker.patch.object(
            ElasticManager,
            "get_latest_events_index_doc",
            return_value={"event_type": "pause", "start_time": start_time},
        )

        response = client.get("/")

        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"paused-view" in response.data

    def test_normal_latest_event_is_pause_and_has_end_time(self, client, mocker):
        """ 正常系：configファイルがすでに存在し、最新のevent_indexが存在するパターン。
            event_indexの最新ステータスがpauseかつend_timeがある場合、測定中画面に遷移。
        """

        mocker.patch.object(ConfigFileManager, "config_exists", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        start_time: datetime = datetime.utcnow()
        end_time: datetime = start_time + timedelta(seconds=60)
        mocker.patch.object(
            ElasticManager,
            "get_latest_events_index_doc",
            return_value={"event_type": "pause", "start_time": start_time, "end_time": end_time},
        )

        response = client.get("/")

        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"started-view" in response.data


class TestSetup:
    def test_normal(self, client, mocker):
        """ 正常系：段取開始。events_indexを作成し、setupイベントを記録。
            また、configファイルにstart_timeを記録。
        """

        mocker.patch.object(ElasticManager, "create_index", return_value=True)
        mocker.patch.object(ElasticManager, "create_doc", return_value=True)
        mocker.patch.object(ConfigFileManager, "update", return_value=True)

        response = client.post("/setup")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b'{"successful": true}' in response.data

    def test_events_index_create_fail_exception(self, client, mocker):
        """ 異常系：events_index作成失敗 """

        mocker.patch.object(ElasticManager, "create_index", return_value=False)

        response = client.post("/setup")
        actual_code = response.status_code
        expected_code = 500

        assert actual_code == expected_code
        assert b'{"successful": false, "message": "create ES index failed."}' in response.data

    def test_events_index_create_doc_fail_exception(self, client, mocker):
        """ 異常系：events_indexのdocument作成失敗 """

        mocker.patch.object(ElasticManager, "create_index", return_value=True)
        mocker.patch.object(ElasticManager, "create_doc", return_value=False)

        response = client.post("/setup")
        actual_code = response.status_code
        expected_code = 500

        assert actual_code == expected_code
        assert b'{"successful": false, "message": "save to ES failed."}' in response.data

    def test_config_file_update_fail_exception(self, client, mocker):
        """ 異常系：configファイルの更新失敗 """

        mocker.patch.object(ElasticManager, "create_index", return_value=True)
        mocker.patch.object(ElasticManager, "create_doc", return_value=True)
        mocker.patch.object(ConfigFileManager, "update", return_value=False)

        response = client.post("/setup")
        actual_code = response.status_code
        expected_code = 500

        assert actual_code == expected_code
        assert b'{"successful": false, "message": "config file update failed."}' in response.data


class TestStart:
    def test_normal(self, client, mocker):
        """ 正常系 """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "count", return_value=1)
        mocker.patch.object(ElasticManager, "create_doc", return_value=True)

        response = client.post("/start")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b'{"successful": true}' in response.data

    def test_events_index_not_found_exception(self, client, mocker):
        """ 異常系：最新のevents_indexがない場合 """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value=None)
        mocker.patch.object(ConfigFileManager, "update", return_value=True)

        response = client.post("/start")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"initial-view" in response.data

    def test_events_index_create_doc_fail_exception(self, client, mocker):
        """ 異常系：events_index更新失敗 """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "count", return_value=1)
        mocker.patch.object(ElasticManager, "create_doc", return_value=False)

        response = client.post("/start")
        actual_code = response.status_code
        expected_code = 500

        assert actual_code == expected_code
        assert b'{"successful": false, "message": "save to ES failed."}' in response.data


class TestPause:
    def test_normal(self, client, mocker):
        """ 正常系 """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "count", return_value=1)
        mocker.patch.object(ElasticManager, "create_doc", return_value=True)

        response = client.post("/pause")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b'{"successful": true}' in response.data

    def test_events_index_not_found_exception(self, client, mocker):
        """ 異常系：最新のevents_indexがない場合 """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value=None)
        mocker.patch.object(ConfigFileManager, "update", return_value=True)

        response = client.post("/pause")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"initial-view" in response.data

    def test_events_index_create_doc_fail_exception(self, client, mocker):
        """ 異常系：events_index更新失敗 """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "count", return_value=1)
        mocker.patch.object(ElasticManager, "create_doc", return_value=False)

        response = client.post("/pause")
        actual_code = response.status_code
        expected_code = 500

        assert actual_code == expected_code
        assert b'{"successful": false, "message": "save to ES failed."}' in response.data


class TestResume:
    def test_normal(self, client, mocker):
        """ 正常系 """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "count", return_value=1)
        mocker.patch.object(ElasticManager, "update_doc", return_value=True)

        response = client.post("/resume")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b'{"successful": true}' in response.data

    def test_events_index_not_found_exception(self, client, mocker):
        """ 異常系：最新のevents_indexがない場合 """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value=None)
        mocker.patch.object(ConfigFileManager, "update", return_value=True)

        response = client.post("/resume")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"initial-view" in response.data

    def test_events_index_create_doc_fail_exception(self, client, mocker):
        """ 異常系：events_index更新失敗 """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "count", return_value=1)
        mocker.patch.object(ElasticManager, "update_doc", return_value=False)

        response = client.post("/resume")
        actual_code = response.status_code
        expected_code = 500

        assert actual_code == expected_code
        assert b'{"successful": false, "message": "save to ES failed."}' in response.data


class TestStop:
    def test_normal(self, client, mocker):
        """ 正常系 """

        mocker.patch.object(ConfigFileManager, "update", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "count", return_value=1)
        mocker.patch.object(ElasticManager, "create_doc", return_value=True)

        response = client.post("/stop")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b'{"successful": true}' in response.data

    def test_config_file_update_fail_exception(self, client, mocker):
        """ 異常系：configファイルの更新失敗 """

        mocker.patch.object(ConfigFileManager, "update", return_value=False)

        response = client.post("/stop")
        actual_code = response.status_code
        expected_code = 500

        assert actual_code == expected_code
        assert b'{"successful": false, "message": "config file update failed."}' in response.data

    def test_events_index_not_found_exception(self, client, mocker):
        """ 異常系：最新のevents_indexがない場合 """

        mocker.patch.object(ConfigFileManager, "update", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value=None)
        mocker.patch.object(ConfigFileManager, "update", return_value=True)

        response = client.post("/stop")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"initial-view" in response.data

    def test_events_index_create_doc_fail_exception(self, client, mocker):
        """ 異常系：events_index更新失敗 """

        mocker.patch.object(ConfigFileManager, "update", return_value=True)
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "count", return_value=1)
        mocker.patch.object(ElasticManager, "create_doc", return_value=False)

        response = client.post("/stop")
        actual_code = response.status_code
        expected_code = 500

        assert actual_code == expected_code
        assert b'{"successful": false, "message": "save to ES failed."}' in response.data


class TestRecordTag:
    def test_normal(self, client, mocker):
        """ 正常系 """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "count", return_value=1)
        mocker.patch.object(ElasticManager, "create_doc", return_value=True)

        response = client.post("/record_tag", data={"tag": "異常A"})
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b'{"successful": true}' in response.data

    def test_invalid_tag(self, client, mocker):
        """ 異常系：フォームから受け取ったTagが不正な場合 """

        response = client.post("/record_tag", data={"dummy": "dummy"})

        actual_code = response.status_code
        expected_code = 400

        assert actual_code == expected_code
        assert (
            b'{"successful": false, "message": "400 Bad Request: The browser (or proxy) sent a request that this server could not understand."'
            in response.data
        )

    def test_events_index_not_found_exception(self, client, mocker):
        """ 異常系：最新のevents_indexがない場合 """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value=None)
        mocker.patch.object(ConfigFileManager, "update", return_value=True)

        response = client.post("/record_tag", data={"tag": "異常A"})
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b"initial-view" in response.data

    def test_events_index_create_doc_fail_exception(self, client, mocker):
        """ 異常系：events_index更新失敗 """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "count", return_value=1)
        mocker.patch.object(ElasticManager, "create_doc", return_value=False)

        response = client.post("/record_tag", data={"tag": "異常A"})
        actual_code = response.status_code
        expected_code = 500

        assert actual_code == expected_code
        assert b'{"successful": false, "message": "save to ES failed."}' in response.data


class TestCheck:
    def test_normal(self, client, mocker):
        """ 正常系：datファイルがすべて処理済み。 """

        mocker.patch.object(glob, "glob", return_value=[])
        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "count", return_value=1)
        mocker.patch.object(ElasticManager, "create_doc", return_value=True)

        response = client.get("/check")
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code
        assert b'{"successful": true, "message": "data recording is finished."}' in response.data


"""
 ==================================
  test_controller.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import pytest
from backend.event_manager.event_manager import EventManager
from backend.app.models.machine import Machine
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.crud.crud_controller import CRUDController
from backend.common import common
from backend.app.api.endpoints import controller


class TestSetup:
    @pytest.fixture
    def init(self):
        self.machine_id = "test-machine-001"
        self.endpoint = f"/api/v1/controller/setup/{self.machine_id}"

    def test_normal(self, client, mocker, init):
        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "create_events_index", return_value=(True, "tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(CRUDController, "setup")

        response = client.post(self.endpoint)

        assert response.status_code == 200

    def test_validation_error(self, client, mocker, init):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(False, "Some error occurred.", 500))

        response = client.post(self.endpoint)

        assert response.status_code == 500

    def test_create_events_index_failed(self, client, mocker, init):
        """eventsインデックス作成失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager,
            "create_events_index",
            return_value=(False, "tmp_events_index"),
        )

        response = client.post(self.endpoint)

        assert response.status_code == 500

    def test_create_doc_events_index_failed(self, client, mocker, init):
        """eventsインデックスのdocument作成失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "create_events_index", return_value=(True, "tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=False)

        response = client.post(self.endpoint)

        assert response.status_code == 500

    def test_db_update_failed(self, client, mocker, init):
        """DBアップデート失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "create_events_index", return_value=(True, "tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(CRUDController, "setup", side_effect=Exception("some exception"))

        response = client.post(self.endpoint)

        assert response.status_code == 500


class TestStart:
    @pytest.fixture
    def init(self):
        self.machine_id = "test-machine-001"
        self.endpoint = f"/api/v1/controller/start/{self.machine_id}"

    def test_normal(self, client, mocker, init):
        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(CRUDMachine, "update")

        response = client.post(self.endpoint)

        assert response.status_code == 200

    def test_validation_error(self, client, mocker, init):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(False, "Some error occurred.", 500))

        response = client.post(self.endpoint)

        assert response.status_code == 500

    def test_get_latest_events_index_failed(self, client, mocker, init):
        """eventsインデックスの取得失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager,
            "get_latest_events_index",
            return_value=(None),
        )

        response = client.post(self.endpoint)

        assert response.status_code == 500

    def test_create_doc_events_index_failed(self, client, mocker, init):
        """eventsインデックスのdocument作成失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=False)

        response = client.post(self.endpoint)

        assert response.status_code == 500

    def test_db_update_failed(self, client, mocker, init):
        """DBアップデート失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(CRUDMachine, "update", side_effect=Exception("some exception"))

        response = client.post(self.endpoint)

        assert response.status_code == 500


class TestPause:
    @pytest.fixture
    def init(self):
        self.machine_id = "test-machine-001"
        self.endpoint = f"/api/v1/controller/pause/{self.machine_id}"

    def test_normal(self, client, mocker, init):
        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(CRUDMachine, "update")

        response = client.post(self.endpoint)

        assert response.status_code == 200

    def test_validation_error(self, client, mocker, init):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(False, "Some error occurred.", 500))

        response = client.post(self.endpoint)

        assert response.status_code == 500

    def test_get_latest_events_index_failed(self, client, mocker, init):
        """eventsインデックスの取得失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager,
            "get_latest_events_index",
            return_value=(None),
        )

        response = client.post(self.endpoint)

        assert response.status_code == 500

    def test_create_doc_events_index_failed(self, client, mocker, init):
        """eventsインデックスのdocument作成失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=False)

        response = client.post(self.endpoint)

        assert response.status_code == 500

    def test_db_update_failed(self, client, mocker, init):
        """DBアップデート失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(CRUDMachine, "update", side_effect=Exception("some exception"))

        response = client.post(self.endpoint)

        assert response.status_code == 500


class TestResume:
    @pytest.fixture
    def init(self):
        self.machine_id = "test-machine-001"
        self.endpoint = f"/api/v1/controller/resume/{self.machine_id}"

    def test_normal(self, client, mocker, init):
        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "update_pause_event", return_value=True)
        mocker.patch.object(CRUDMachine, "update")

        response = client.post(self.endpoint)

        assert response.status_code == 200

    def test_validation_error(self, client, mocker, init):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(False, "Some error occurred.", 500))

        response = client.post(self.endpoint)

        assert response.status_code == 500

    def test_get_latest_events_index_failed(self, client, mocker, init):
        """eventsインデックスの取得失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager,
            "get_latest_events_index",
            return_value=(None),
        )

        response = client.post(self.endpoint)

        assert response.status_code == 500

    def test_update_pause_events_index_failed(self, client, mocker, init):
        """eventsインデックスのデータ更新失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "update_pause_event", return_value=False)

        response = client.post(self.endpoint)

        assert response.status_code == 500

    def test_db_update_failed(self, client, mocker, init):
        """DBアップデート失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "update_pause_event", return_value=True)
        mocker.patch.object(CRUDMachine, "update", side_effect=Exception("some exception"))

        response = client.post(self.endpoint)

        assert response.status_code == 500


class TestStop:
    @pytest.fixture
    def init(self):
        self.machine_id = "test-machine-001"
        self.endpoint = f"/api/v1/controller/stop/{self.machine_id}"

    def test_normal(self, client, mocker, init):
        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(CRUDController, "stop")

        response = client.post(self.endpoint)

        assert response.status_code == 200

    def test_validation_error(self, client, mocker, init):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(False, "Some error occurred.", 500))

        response = client.post(self.endpoint)

        assert response.status_code == 500
        assert response.json() == {"detail": "Some error occurred."}

    def test_get_latest_events_index_failed(self, client, mocker, init):
        """eventsインデックスの取得失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager,
            "get_latest_events_index",
            return_value=(None),
        )

        response = client.post(self.endpoint)

        assert response.status_code == 500
        assert response.json() == {"detail": "対象のevents_indexがありません。"}

    def test_create_doc_events_index_failed(self, client, mocker, init):
        """eventsインデックスのdocument作成失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=False)

        response = client.post(self.endpoint)

        assert response.status_code == 500
        assert response.json() == {"detail": "events_indexのデータ投入に失敗しました。"}

    def test_db_update_failed(self, client, mocker, init):
        """DBアップデート失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(CRUDController, "stop", side_effect=Exception("some exception"))

        response = client.post(self.endpoint)

        assert response.status_code == 500
        assert response.json() == {"detail": "DB update error."}


class TestCheck:
    @pytest.fixture
    def init(self):
        self.machine_id = "test-machine-001"
        self.endpoint = f"/api/v1/controller/check/{self.machine_id}"

    def test_normal(self, client, mocker, init):
        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(common, "get_config_value", return_value=("/mnt/datadrive/data/"))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(CRUDController, "record")

        response = client.post(self.endpoint)

        assert response.status_code == 200

    def test_validation_error(self, client, mocker, init):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(False, "Some error occurred.", 500))

        response = client.post(self.endpoint)

        assert response.status_code == 500
        assert response.json() == {"detail": "Some error occurred."}

    def test_get_latest_events_index_failed(self, client, mocker, init):
        """eventsインデックスの取得失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager,
            "get_latest_events_index",
            return_value=(None),
        )

        response = client.post(self.endpoint)

        assert response.status_code == 500
        assert response.json() == {"detail": "対象のevents_indexがありません。"}

    def test_create_doc_events_index_failed(self, client, mocker, init):
        """eventsインデックスのdocument作成失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=False)

        response = client.post(self.endpoint)

        assert response.status_code == 500

    def test_db_update_failed(self, client, mocker, init):
        """DBアップデート失敗"""

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id="test-machine-001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "get_latest_events_index", return_value=("tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(CRUDController, "record", side_effect=Exception("some exception"))

        response = client.post(self.endpoint)

        assert response.status_code == 500

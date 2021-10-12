"""
 ==================================
  test_controller.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import pytest
from backend.app.api.endpoints import controller
from backend.app.crud.crud_controller import CRUDController
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.models.machine import Machine
from backend.common import common
from backend.event_manager.event_manager import EventManager


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
        mocker.patch.object(CRUDController, "start")

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
        mocker.patch.object(CRUDController, "start", side_effect=Exception("some exception"))

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
        mocker.patch.object(CRUDController, "pause")

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
        mocker.patch.object(CRUDController, "pause", side_effect=Exception("some exception"))

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
        mocker.patch.object(CRUDController, "resume")

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
        mocker.patch.object(CRUDController, "resume", side_effect=Exception("some exception"))

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
        mocker.patch.object(CRUDController, "record", side_effect=Exception("some exception"))

        response = client.post(self.endpoint)

        assert response.status_code == 500

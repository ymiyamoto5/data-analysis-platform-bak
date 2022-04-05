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
from backend.app.worker.celery import celery_app
from backend.common import common


class TestData:
    machine_id_data = ["test-machine-01", "test-machine-02"]


class TestSetup:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/controller/setup"

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_normal(self, client, mocker, init, machine_id):
        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(True, None, 200))

        response = client.post(endpoint)

        assert response.status_code == 200

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_validation_error(self, client, mocker, init, machine_id):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""
        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(False, "Some error occurred.", 500))

        response = client.post(endpoint)

        assert response.status_code == 500

    def test_multi_handler_validation_error(self, client, mocker, init):
        """multi_handler_validation関数で何らかのエラーが発生した場合を想定"""
        endpoint = f"{self.endpoint}/test-machine-01"

        mocker.patch.object(controller, "multi_handler_validation", return_value=(False, "Some error occurred.", 400))

        response = client.post(endpoint)

        assert response.status_code == 400

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_db_update_failed(self, client, mocker, init, machine_id):
        """DBアップデート失敗"""
        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(CRUDController, "setup", side_effect=Exception("some exception"))

        response = client.post(endpoint)

        assert response.status_code == 500


class TestRunAutoDataRecorder:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/controller/run-data-recorder"
        self.task = type("Dummy", (object,), {"id": "test-task-id", "info": "test-task-info"})

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_normal(self, client, mocker, init, machine_id):
        # TODO: task_idやステータスの確認を追加し、インテグレーションテストにする
        # https://testdriven.io/blog/fastapi-and-celery/#tests

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(celery_app, "send_task", return_value=self.task)

        response = client.post(endpoint)

        assert response.status_code == 200

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_validation_error(self, client, mocker, init, machine_id):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(False, "Some error occurred.", 500))

        response = client.post(endpoint)

        assert response.status_code == 500


class TestStart:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/controller/start"

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_normal(self, client, mocker, init, machine_id):
        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(True, None, 200))

        response = client.post(endpoint)

        assert response.status_code == 200

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_validation_error(self, client, mocker, init, machine_id):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(False, "Some error occurred.", 500))

        response = client.post(endpoint)

        assert response.status_code == 500

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_db_update_failed(self, client, mocker, init, machine_id):
        """DBアップデート失敗"""

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(CRUDController, "start", side_effect=Exception("some exception"))

        response = client.post(endpoint)

        assert response.status_code == 500


class TestPause:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/controller/pause"

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_normal(self, client, mocker, init, machine_id):

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(True, None, 200))

        response = client.post(endpoint)

        assert response.status_code == 200

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_validation_error(self, client, mocker, init, machine_id):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(False, "Some error occurred.", 500))

        response = client.post(endpoint)

        assert response.status_code == 500

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_db_update_failed(self, client, mocker, init, machine_id):
        """DBアップデート失敗"""

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(CRUDController, "pause", side_effect=Exception("some exception"))

        response = client.post(endpoint)

        assert response.status_code == 500


class TestResume:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/controller/resume"

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_normal(self, client, mocker, init, machine_id):
        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(True, None, 200))

        response = client.post(endpoint)

        assert response.status_code == 200

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_validation_error(self, client, mocker, init, machine_id):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(False, "Some error occurred.", 500))

        response = client.post(endpoint)

        assert response.status_code == 500

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_db_update_failed(self, client, mocker, init, machine_id):
        """DBアップデート失敗"""

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(CRUDController, "resume", side_effect=Exception("some exception"))

        response = client.post(endpoint)

        assert response.status_code == 500


class TestStop:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/controller/stop"

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_normal(self, client, mocker, init, machine_id):
        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(True, None, 200))

        response = client.post(endpoint)

        assert response.status_code == 200

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_validation_error(self, client, mocker, init, machine_id):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(False, "Some error occurred.", 500))

        response = client.post(endpoint)

        assert response.status_code == 500
        assert response.json() == {"detail": "Some error occurred."}

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_db_update_failed(self, client, mocker, init, machine_id):
        """DBアップデート失敗"""

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(CRUDController, "stop", side_effect=Exception("some exception"))

        response = client.post(endpoint)

        assert response.status_code == 500
        assert response.json() == {"detail": "DB update error."}


class TestCheck:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/controller/check"

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_normal(self, client, mocker, init, machine_id):
        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(common, "get_config_value", return_value=("/mnt/datadrive/data/"))

        response = client.post(endpoint)

        assert response.status_code == 200

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_validation_error(self, client, mocker, init, machine_id):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(False, "Some error occurred.", 500))

        response = client.post(endpoint)

        assert response.status_code == 500
        assert response.json() == {"detail": "Some error occurred."}

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_db_update_failed(self, client, mocker, init, machine_id):
        """DBアップデート失敗"""

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(CRUDController, "record", side_effect=Exception("some exception"))

        response = client.post(endpoint)

        assert response.status_code == 500


class TestReset:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/controller/reset"

    test_reset_data = []

    test_collect_status_data = [
        common.COLLECT_STATUS.SETUP.value,
        common.COLLECT_STATUS.START.value,
        common.COLLECT_STATUS.PAUSE.value,
        common.COLLECT_STATUS.RESUME.value,
        common.COLLECT_STATUS.STOP.value,
        common.COLLECT_STATUS.RECORDED.value,
    ]

    for machine_id in TestData.machine_id_data:
        for collect_status in test_collect_status_data:
            test_reset_data.append((machine_id, collect_status))

    @pytest.mark.parametrize("machine_id, collect_status", test_reset_data)
    def test_normal(self, client, mocker, init, machine_id, collect_status):
        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id=machine_id,
                collect_status=collect_status,
            ),
        )

        mocker.patch.object(celery_app, "control")

        response = client.post(endpoint)

        assert response.status_code == 200

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_db_update_failed(self, client, mocker, init, machine_id):
        """DBアップデート失敗"""

        endpoint = f"{self.endpoint}/{machine_id}"

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=Machine(
                machine_id=machine_id,
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(CRUDController, "reset", side_effect=Exception("some exception"))

        response = client.post(endpoint)

        assert response.status_code == 500
        assert response.json() == {"detail": "DB update error."}

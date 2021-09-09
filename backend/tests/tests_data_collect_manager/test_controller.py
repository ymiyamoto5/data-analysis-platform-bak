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
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.dao.machine_dao import MachineDAO
from backend.data_collect_manager.dao.controller_dao import ControllerDAO
from backend.common import common
from backend.data_collect_manager.apis import controller


class TestSetup:
    @pytest.fixture
    def init(self):
        self.machine_id = "test_machine_001"
        self.endpoint = f"/api/v1/controller/setup/{self.machine_id}"

    def test_normal(self, client, mocker, init):
        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager, "create_events_index", return_value=(True, "tmp_events_index")
        )
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(ControllerDAO, "setup")

        response = client.post(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_validation_error(self, client, mocker, init):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(
            controller, "validation", return_value=(False, "Some error occurred.", 500)
        )

        response = client.post(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert b'{"message":"Some error occurred."}\n' in response.data

    def test_create_events_index_failed(self, client, mocker, init):
        """eventsインデックス作成失敗"""

        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
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
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"events_indexの作成に失敗しました。"}\n' in response.data.decode()

    def test_create_doc_events_index_failed(self, client, mocker, init):
        """eventsインデックスのdocument作成失敗"""

        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager, "create_events_index", return_value=(True, "tmp_events_index")
        )
        mocker.patch.object(EventManager, "record_event", return_value=False)

        response = client.post(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"events_indexのデータ投入に失敗しました。"}\n' in response.data.decode()

    def test_db_update_failed(self, client, mocker, init):
        """DBアップデート失敗"""

        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager, "create_events_index", return_value=(True, "tmp_events_index")
        )
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(
            ControllerDAO, "setup", side_effect=Exception("some exception")
        )

        response = client.post(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"更新に失敗しました: some exception"}\n' in response.data.decode()


class TestStart:
    @pytest.fixture
    def init(self):
        self.machine_id = "test_machine_001"
        self.endpoint = f"/api/v1/controller/start/{self.machine_id}"

    def test_normal(self, client, mocker, init):
        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager, "get_latest_events_index", return_value=("tmp_events_index")
        )
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(MachineDAO, "update")

        response = client.post(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_validation_error(self, client, mocker, init):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(
            controller, "validation", return_value=(False, "Some error occurred.", 500)
        )

        response = client.post(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert b'{"message":"Some error occurred."}\n' in response.data

    def test_get_latest_events_index_failed(self, client, mocker, init):
        """eventsインデックスの取得失敗"""

        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
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
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"対象のevents_indexがありません。"}\n' in response.data.decode()

    def test_create_doc_events_index_failed(self, client, mocker, init):
        """eventsインデックスのdocument作成失敗"""

        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager, "get_latest_events_index", return_value=("tmp_events_index")
        )
        mocker.patch.object(EventManager, "record_event", return_value=False)

        response = client.post(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"events_indexのデータ投入に失敗しました。"}\n' in response.data.decode()

    def test_db_update_failed(self, client, mocker, init):
        """DBアップデート失敗"""

        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager, "get_latest_events_index", return_value=("tmp_events_index")
        )
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(
            MachineDAO, "update", side_effect=Exception("some exception")
        )

        response = client.post(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"更新に失敗しました: some exception"}\n' in response.data.decode()


class TestPause:
    @pytest.fixture
    def init(self):
        self.machine_id = "test_machine_001"
        self.endpoint = f"/api/v1/controller/pause/{self.machine_id}"

    def test_normal(self, client, mocker, init):
        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager, "get_latest_events_index", return_value=("tmp_events_index")
        )
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(MachineDAO, "update")

        response = client.post(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_validation_error(self, client, mocker, init):
        """validation関数で何らかのエラーが発生した場合を想定。
        validation関数自体は別テストケースとする。"""

        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(
            controller, "validation", return_value=(False, "Some error occurred.", 500)
        )

        response = client.post(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert b'{"message":"Some error occurred."}\n' in response.data

    def test_get_latest_events_index_failed(self, client, mocker, init):
        """eventsインデックスの取得失敗"""

        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
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
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"対象のevents_indexがありません。"}\n' in response.data.decode()

    def test_create_doc_events_index_failed(self, client, mocker, init):
        """eventsインデックスのdocument作成失敗"""

        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager, "get_latest_events_index", return_value=("tmp_events_index")
        )
        mocker.patch.object(EventManager, "record_event", return_value=False)

        response = client.post(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"events_indexのデータ投入に失敗しました。"}\n' in response.data.decode()

    def test_db_update_failed(self, client, mocker, init):
        """DBアップデート失敗"""

        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(
                machine_id="test_machine_001",
                collect_status=common.COLLECT_STATUS.RECORDED.value,
            ),
        )
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(
            EventManager, "get_latest_events_index", return_value=("tmp_events_index")
        )
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(
            MachineDAO, "update", side_effect=Exception("some exception")
        )

        response = client.post(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"更新に失敗しました: some exception"}\n' in response.data.decode()

"""
 ==================================
  test_controller.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

from backend.event_manager.event_manager import EventManager
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.dao.machine_dao import MachineDAO
from backend.data_collect_manager.dao.controller_dao import ControlerDAO
from backend.common import common
from backend.data_collect_manager.apis import controller


class TestSetup:
    def test_normal(self, client, mocker):
        mocker.patch.object(controller, "validation", return_value=(True, None, 200))
        mocker.patch.object(EventManager, "create_events_index", return_value=(True, "tmp_events_index"))
        mocker.patch.object(EventManager, "record_event", return_value=True)
        mocker.patch.object(
            MachineDAO,
            "select_by_id",
            return_value=Machine(machine_id="test_machine_001", collect_status=common.COLLECT_STATUS.RECORDED.value),
        )
        mocker.patch.object(ControlerDAO, "setup")

        machine_id = "test_machine_001"
        endpoint = f"/api/v1/controller/setup/{machine_id}"

        response = client.post(endpoint)
        actual_code = response.status_code
        expected_code = 200

        assert actual_code == expected_code

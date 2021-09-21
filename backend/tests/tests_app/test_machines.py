import pytest
import json
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.models.machine import Machine
from backend.app.models.machine_type import MachineType


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/machines"
        self.machine_id = "test-machine-001"

    def test_normal_db_select_all(self, client, mocker, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        mocker.patch.object(CRUDMachine, "select_all")

        assert actual_code == 200

    def test_normal_db_select_by_id(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.machine_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        mocker.patch.object(CRUDMachine, "select_by_id")

        assert actual_code == 200


class TestCreate:
    @pytest.fixture
    def init(self):
        # NOTE: 末尾スラッシュがないと307 redirectになってしまう。
        self.endpoint = "/api/v1/machines/"
        self.machine_type = MachineType(machine_type_id=1, machine_type_name="荷重")
        self.machine = Machine(
            machine_id="Test-Machine-001",
            machine_name="Test-Press",
            machine_type_id=1,
            collect_status="recorded",
            machine_type=self.machine_type,
        )

    def test_normal(self, client, mocker, init):
        data = {
            "machine_id": "Test-Machine-001",
            "machine_name": "Test-Press",
            "machine_type_id": 1,
        }

        mocker.patch.object(CRUDMachine, "select_by_id", return_value=None)
        mocker.patch.object(CRUDMachine, "insert", return_value=self.machine)

        response = client.post(self.endpoint, json=data)

        assert response.status_code == 200

    test_invalid_machine_id_data = [
        (
            {
                "machine_id": "Machine_001",
                "machine_name": "Test-Press",
                "machine_type_id": 1,
            },
            422,
        ),
        (
            {
                "machine_id": "Machine@001",
                "machine_name": "Test-Press",
                "machine_type_id": 1,
            },
            422,
        ),
        (
            {
                "machine_id": "Machine001'",
                "machine_name": "Test-Press",
                "machine_type_id": 1,
            },
            422,
        ),
        (
            {"machine_id": "機器001", "machine_name": "Test-Press", "machine_type_id": 1},
            422,
        ),
        ({"machine_id": "", "machine_name": "Test-Press", "machine_type_id": 1}, 422),
    ]

    @pytest.mark.parametrize("data, expected_code", test_invalid_machine_id_data)
    def test_invalid_machine_id(self, client, init, data, expected_code):
        """利用不可文字が含まれるmachine_id"""

        response = client.post(self.endpoint, json=data)
        actual_code = response.status_code

        assert actual_code == expected_code

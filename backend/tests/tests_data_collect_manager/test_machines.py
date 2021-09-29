import pytest
import json
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.dao.machine_dao import MachineDAO
from backend.common import common


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/machines"
        self.machine_id = "test_machine_001"

    def test_normal_db_select_all(self, client, mocker, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        mocker.patch.object(MachineDAO, "select_all")

        assert actual_code == 200

    def test_normal_db_select_by_id(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.machine_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        mocker.patch.object(MachineDAO, "select_by_id")

        assert actual_code == 200

    def test_db_select_all_failed(self, client, mocker, init):
        """Machineを起点に関連エンティティを全結合したデータ取得失敗"""

        mocker.patch.object(
            MachineDAO, "select_all", side_effect=Exception("some exception")
        )

        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"読み取りに失敗しました: some exception"}\n' in response.data.decode()

    def test_db_select_by_id_failed(self, client, mocker, init):
        """指定machineのデータ取得失敗"""

        endpoint = f"{self.endpoint}/{self.machine_id}"
        mocker.patch.object(
            MachineDAO, "select_by_id", side_effect=Exception("some exception")
        )

        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"読み取りに失敗しました: some exception"}\n' in response.data.decode()


class TestCreate:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/machines"

    def test_normal(self, client, mocker, init):
        data = {
            "machine_id": "Test-Machine-001",
            "machine_name": "Test-Press",
            "machine_type_id": 1,
        }

        mocker.patch.object(MachineDAO, "insert")

        response = client.post(
            self.endpoint, data=json.dumps(data), content_type="application/json"
        )
        actual_code = response.status_code

        assert actual_code == 200

    def test_no_post_data(self, client, init):
        response = client.post(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 400
        assert '{"message":"入力データがありません"}\n' in response.data.decode()

    test_invalid_machine_id_data = [
        (
            {
                "machine_id": "Machine_001",
                "machine_name": "Test-Press",
                "machine_type_id": 1,
            },
            400,
        ),
        (
            {
                "machine_id": "Machine@001",
                "machine_name": "Test-Press",
                "machine_type_id": 1,
            },
            400,
        ),
        (
            {
                "machine_id": "Machine001'",
                "machine_name": "Test-Press",
                "machine_type_id": 1,
            },
            400,
        ),
        (
            {"machine_id": "機器001", "machine_name": "Test-Press", "machine_type_id": 1},
            400,
        ),
    ]

    @pytest.mark.parametrize("data, expected_code", test_invalid_machine_id_data)
    def test_invalid_machine_id(self, client, init, data, expected_code):
        """利用不可文字が含まれるmachine_id"""

        response = client.post(
            self.endpoint, data=json.dumps(data), content_type="application/json"
        )
        actual_code = response.status_code

        assert actual_code == expected_code
        assert (
            "{\"message\":\"検証に失敗しました: {'machine_id': ['Invalid character used.']}\"}\n"
            in response.data.decode()
        )

    def test_null_machine_id(self, client, init):
        """machine_idが空文字"""
        data = {"machine_id": "", "machine_name": "Test-Press", "machine_type_id": 1}

        response = client.post(
            self.endpoint, data=json.dumps(data), content_type="application/json"
        )
        actual_code = response.status_code

        assert actual_code == 400
        assert (
            "{\"message\":\"検証に失敗しました: {'machine_id': ['Invalid character used.', 'Length must be between 1 and 255.']}\"}\n"
            in response.data.decode()
        )

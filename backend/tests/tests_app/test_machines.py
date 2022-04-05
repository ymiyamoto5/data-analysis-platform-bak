import pytest
from backend.app.crud.crud_machine import CRUDMachine


class TestData:
    machine_id_data = ["test-machine-01", "test-machine-02"]


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/machines"

    def test_normal_db_select_all(self, client, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_all_failed(self, client, mocker, init):
        mocker.patch.object(CRUDMachine, "select_all", side_effect=Exception("some exception"))
        response = client.get(self.endpoint)

        assert response.status_code == 500

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_normal_db_select_by_id(self, client, init, machine_id):
        endpoint = f"{self.endpoint}/{machine_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_db_select_by_id_failed(self, client, mocker, init, machine_id):
        endpoint = f"{self.endpoint}/{machine_id}"
        mocker.patch.object(CRUDMachine, "select_by_id", side_effect=Exception("some exception"))
        response = client.get(endpoint)

        assert response.status_code == 500


class TestCreate:
    @pytest.fixture
    def init(self):
        # NOTE: 末尾スラッシュがないと307 redirectになってしまう。
        self.endpoint = "/api/v1/machines/"
        self.data = {
            "machine_id": "new-test-machine",
            "machine_name": "Test-Press",
            "machine_type_id": 1,
        }

    def test_normal(self, client, init):

        response = client.post(self.endpoint, json=self.data)

        assert response.status_code == 200

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_not_unique_machine_id(self, client, init, machine_id):
        """重複しているmachine_id"""
        data = {
            "machine_id": f"{machine_id}",
            "machine_name": "Test-Press",
            "machine_type_id": 1,
        }

        response = client.post(self.endpoint, json=data)

        assert response.status_code == 400

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
            {
                "machine_id": "機器001",
                "machine_name": "Test-Press",
                "machine_type_id": 1,
            },
            422,
        ),
        (
            {
                "machine_id": "",
                "machine_name": "Test-Press",
                "machine_type_id": 1,
            },
            422,
        ),
    ]

    @pytest.mark.parametrize("data, expected_code", test_invalid_machine_id_data)
    def test_invalid_machine_id(self, client, init, data, expected_code):
        """利用不可文字が含まれるmachine_id"""

        response = client.post(self.endpoint, json=data)
        actual_code = response.status_code

        assert actual_code == expected_code

    def test_insert_failed(self, client, mocker, init):
        mocker.patch.object(CRUDMachine, "insert", side_effect=Exception("some exception"))
        response = client.post(self.endpoint, json=self.data)

        assert response.status_code == 500


class TestUpdate:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/machines"
        self.data = {
            "machine_name": "test-update",
            "machine_type_id": 2,
        }

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_normal(self, client, init, machine_id):
        endpoint = f"{self.endpoint}/{machine_id}"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 200

    def test_not_exist_machine_id(self, client, init):
        """存在しないmachine_id"""
        endpoint = f"{self.endpoint}/not-exist-machine-id"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 404

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_update_failed(self, client, mocker, init, machine_id):
        endpoint = f"{self.endpoint}/{machine_id}"
        mocker.patch.object(CRUDMachine, "update", side_effect=Exception("some exception"))
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 500


class TestDelete:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/machines"

    def test_normal(self, client, init):
        endpoint = f"{self.endpoint}/test-machine-04"
        response = client.delete(endpoint)

        assert response.status_code == 200

    def test_not_exist_machine_id(self, client, init):
        """存在しないmachine_id"""
        endpoint = f"{self.endpoint}/not-exist-machine-id"
        response = client.delete(endpoint)

        assert response.status_code == 404

    @pytest.mark.parametrize("machine_id", TestData.machine_id_data)
    def test_foreign_key_error(self, client, init, machine_id):
        """子が存在するmachine_id"""
        endpoint = f"{self.endpoint}/{machine_id}"
        response = client.delete(endpoint)

        assert response.status_code == 500

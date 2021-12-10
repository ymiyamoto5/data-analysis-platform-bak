import pytest
from backend.app.crud.crud_machine import CRUDMachine


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/machines"
        self.machine_id = "test-machine-01"

    def test_normal_db_select_all(self, client, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_all_failed(self, client, mocker, init):
        mocker.patch.object(CRUDMachine, "select_all", side_effect=Exception("some exception"))
        response = client.get(self.endpoint)

        assert response.status_code == 500

    def test_normal_db_select_by_id(self, client, init):
        endpoint = f"{self.endpoint}/{self.machine_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_by_id_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.machine_id}"
        mocker.patch.object(CRUDMachine, "select_by_id", side_effect=Exception("some exception"))
        response = client.get(endpoint)

        assert response.status_code == 500

    def test_normal_db_select_machines_has_handler(self, client, init):
        endpoint = f"{self.endpoint}/machines/has_handler"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_machines_has_handler_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/machines/has_handler"
        mocker.patch.object(CRUDMachine, "select_machines_has_handler", side_effect=Exception("some exception"))
        response = client.get(endpoint)

        assert response.status_code == 500

    def test_normal_db_select_handler_from_machine_id(self, client, init):
        endpoint = f"{self.endpoint}/{self.machine_id}/handler"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_handler_from_machine_id_failed(self, client, init):
        """handlerを持たないmachine_id"""
        endpoint = f"{self.endpoint}/test-machine-04/handler"
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

    def test_not_unique_machine_id(self, client, init):
        """重複しているmachine_id"""
        data = {
            "machine_id": "test-machine-01",
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
        self.machine_id = "test-machine-01"
        self.endpoint = "/api/v1/machines"
        self.data = {
            "machine_name": "test-update",
            "machine_type_id": 2,
        }

    def test_normal(self, client, init):
        endpoint = f"{self.endpoint}/{self.machine_id}"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 200

    def test_not_exist_machine_id(self, client, init):
        """存在しないmachine_id"""
        endpoint = f"{self.endpoint}/not-exist-machine-id"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 404

    def test_update_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.machine_id}"
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

    def test_foreign_key_error(self, client, init):
        """子が存在するmachine_id"""
        endpoint = f"{self.endpoint}/test-machine-01"
        response = client.delete(endpoint)

        assert response.status_code == 500

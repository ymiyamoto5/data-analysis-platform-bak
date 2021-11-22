import pytest
from backend.app.crud.crud_gateway import CRUDGateway
from backend.common import common


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/gateways"
        self.gateway_id = "test-gw-01"

    def test_normal_db_select_all(self, client, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_all_failed(self, client, mocker, init):
        mocker.patch.object(CRUDGateway, "select_all", side_effect=Exception("some exception"))
        response = client.get(self.endpoint)

        assert response.status_code == 500

    def test_normal_db_select_by_id(self, client, init):
        endpoint = f"{self.endpoint}/{self.gateway_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_by_id_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.gateway_id}"
        mocker.patch.object(CRUDGateway, "select_by_id", side_effect=Exception("some exception"))
        response = client.get(endpoint)

        assert response.status_code == 500


class TestCreate:
    @pytest.fixture
    def init(self):
        # NOTE: 末尾スラッシュがないと307 redirectになってしまう。
        self.endpoint = "/api/v1/gateways/"
        self.data = {
            "gateway_id": "Test-Gateway-001",
            "log_level": 5,
            "machine_id": "test-machine-01",
        }

    def test_normal(self, client, init):

        response = client.post(self.endpoint, json=self.data)

        assert response.status_code == 200

    def test_not_unique_gateway_id(self, client, init):
        """重複しているgateway_id"""
        data = {
            "gateway_id": "test-gw-01",
            "log_level": 5,
            "machine_id": "test-machine-01",
        }

        response = client.post(self.endpoint, json=data)

        assert response.status_code == 400

    test_invalid_data = [
        # invalid gateway_id
        (
            {
                "gateway_id": "GW_001",
                "log_level": 5,
                "machine_id": "test-machine-01",
            },
            422,
        ),
        (
            {
                "gateway_id": "GW@001",
                "log_level": 5,
                "machine_id": "test-machine-01",
            },
            422,
        ),
        (
            {
                "gateway_id": "GW001'",
                "log_level": 5,
                "machine_id": "test-machine-01",
            },
            422,
        ),
        (
            {
                "gateway_id": "ゲートウェイ001",
                "log_level": 5,
                "machine_id": "test-machine-01",
            },
            422,
        ),
        (
            {
                "gateway_id": "",
                "log_level": 5,
                "machine_id": "test-machine-01",
            },
            422,
        ),
        # out of range log_level
        (
            {
                "gateway_id": "Test-Gateway-001",
                "log_level": 0,
                "machine_id": "test-machine-01",
            },
            422,
        ),
        (
            {
                "gateway_id": "Test-Gateway-001",
                "log_level": 6,
                "machine_id": "test-machine-01",
            },
            422,
        ),
    ]

    @pytest.mark.parametrize("data, expected_code", test_invalid_data)
    def test_invalid_someting_data(self, client, init, data, expected_code):
        """無効なデータが含まれる"""

        response = client.post(self.endpoint, json=data)
        actual_code = response.status_code

        assert actual_code == expected_code

    def test_insert_failed(self, client, mocker, init):
        mocker.patch.object(CRUDGateway, "insert", side_effect=Exception("some exception"))
        response = client.post(self.endpoint, json=self.data)

        assert response.status_code == 500


class TestUpdate:
    @pytest.fixture
    def init(self):
        self.gateway_id = "test-gw-01"
        self.endpoint = "/api/v1/gateways"
        self.data = {
            "log_level": 1,
        }

    def test_normal(self, client, init):
        endpoint = f"{self.endpoint}/{self.gateway_id}"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 200

    def test_not_exist_gateway_id(self, client, init):
        """存在しないgateway_id"""
        endpoint = f"{self.endpoint}/not-exist-gw-id"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 404

    test_out_of_range_log_level_data = [
        (
            {
                "log_level": 0,
            },
            422,
        ),
        (
            {
                "log_level": 6,
            },
            422,
        ),
    ]

    @pytest.mark.parametrize("data, expected_code", test_out_of_range_log_level_data)
    def test_out_of_range_log_level(self, client, init, data, expected_code):
        """範囲外のlog_level"""

        endpoint = f"{self.endpoint}/{self.gateway_id}"
        response = client.put(endpoint, json=data)
        actual_code = response.status_code

        assert actual_code == expected_code

    def test_update_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.gateway_id}"
        mocker.patch.object(CRUDGateway, "update", side_effect=Exception("some exception"))
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 500

    def test_normal_update_from_gateway(self, client, init):
        endpoint = f"{self.endpoint}/{self.gateway_id}/update"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 200

    def test_update_from_not_exist_gateway_id(self, client, init):
        """存在しないgateway_id"""
        endpoint = f"{self.endpoint}/not-exist-gw-id/update"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 404

    @pytest.mark.parametrize("data, expected_code", test_out_of_range_log_level_data)
    def test_update_from_gateway_out_of_range_log_level(self, client, init, data, expected_code):
        """範囲外のlog_level"""

        endpoint = f"{self.endpoint}/{self.gateway_id}/update"
        response = client.put(endpoint, json=data)
        actual_code = response.status_code

        assert actual_code == expected_code

    def test_update_from_gateway_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.gateway_id}/update"
        mocker.patch.object(CRUDGateway, "update_from_gateway", side_effect=Exception("some exception"))
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 500


class TestUpdateFromGateway:
    @pytest.fixture
    def init(self):
        self.gateway_id = "test-gw-01"
        self.endpoint = "/api/v1/gateways"
        self.data = {"sequence_number": 1, "gateway_result": 1, "status": common.STATUS.RUNNING.value, "log_level": 5}

    def test_normal(self, client, init):
        endpoint = f"{self.endpoint}/{self.gateway_id}/update"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 200


class TestDelete:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/gateways"

    def test_normal(self, client, init):
        endpoint = f"{self.endpoint}/test-gw-05"
        response = client.delete(endpoint)

        assert response.status_code == 200

    def test_not_exist_gateway_id(self, client, init):
        """存在しないgateway_id"""
        endpoint = f"{self.endpoint}/not-exist-gw-id"
        response = client.delete(endpoint)

        assert response.status_code == 404

    def test_foreign_key_error(self, client, init):
        """子が存在するgateway_id"""
        endpoint = f"{self.endpoint}/test-gw-01"
        response = client.delete(endpoint)

        assert response.status_code == 500

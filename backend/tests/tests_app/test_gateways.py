import pytest


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/gateways"
        self.gateway_id = "test-gw-01"

    def test_normal_db_select_all(self, client, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_normal_db_select_by_id(self, client, init):
        endpoint = f"{self.endpoint}/{self.gateway_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200


class TestCreate:
    @pytest.fixture
    def init(self):
        # NOTE: 末尾スラッシュがないと307 redirectになってしまう。
        self.endpoint = "/api/v1/gateways/"

    def test_normal(self, client, init):
        data = {
            "gateway_id": "Test-Gateway-001",
            "log_level": 5,
            "machine_id": "test-machine-01",
        }

        response = client.post(self.endpoint, json=data)

        assert response.status_code == 200


class TestUpdate:
    @pytest.fixture
    def init(self):
        self.gateway_id = "test-gw-01"
        self.endpoint = "/api/v1/gateways/" + self.gateway_id

    def test_normal(self, client, init):
        data = {
            "log_level": 1,
        }
        response = client.put(self.endpoint, json=data)

        assert response.status_code == 200


class TestDelete:
    @pytest.fixture
    def init(self):
        self.gateway_id = "test-gw-05"
        self.endpoint = "/api/v1/gateways/" + self.gateway_id

    def test_normal(self, client, init):

        response = client.delete(self.endpoint)

        assert response.status_code == 200

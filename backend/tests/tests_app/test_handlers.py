import pytest


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/handlers"
        self.handler_id = "test-handler-01"

    def test_normal_db_select_all(self, client, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_normal_db_select_by_id(self, client, init):
        endpoint = f"{self.endpoint}/{self.handler_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200


class TestCreate:
    @pytest.fixture
    def init(self):
        # NOTE: 末尾スラッシュがないと307 redirectになってしまう。
        self.endpoint = "/api/v1/handlers/"

    def test_normal(self, client, init):
        data = {
            "handler_id": "Test-Handler-001",
            "handler_type": "test-create",
            "adc_serial_num": "12345678",
            "sampling_frequency": 1,
            "filewrite_time": 1,
            "gateway_id": "test-gw-01",
        }

        response = client.post(self.endpoint, json=data)

        assert response.status_code == 200


class TestUpdate:
    @pytest.fixture
    def init(self):
        self.handler_id = "test-handler-01"
        self.endpoint = "/api/v1/handlers/" + self.handler_id

    def test_normal(self, client, init):
        data = {
            "handler_type": "test-update",
            "adc_serial_num": "12345678",
            "sampling_frequency": 1,
            "filewrite_time": 1,
        }
        response = client.put(self.endpoint, json=data)

        assert response.status_code == 200


class TestDelete:
    @pytest.fixture
    def init(self):
        self.handler_id = "test-handler-06"
        self.endpoint = "/api/v1/handlers/" + self.handler_id

    def test_normal(self, client, init):

        response = client.delete(self.endpoint)

        assert response.status_code == 200

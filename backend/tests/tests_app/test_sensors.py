import pytest


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/sensors"
        self.sensor_id = "load01"
        self.machine_id = "test-machine-01"

    def test_normal_db_select_all(self, client, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_normal_db_select_by_id(self, client, init):
        endpoint = f"{self.endpoint}/{self.sensor_id}?machine_id={self.machine_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200


class TestCreate:
    @pytest.fixture
    def init(self):
        # NOTE: 末尾スラッシュがないと307 redirectになってしまう。
        self.endpoint = "/api/v1/sensors/"

    def test_normal(self, client, init):
        data = {
            "sensor_name": "test-create",
            "sensor_type_id": "load",
            "handler_id": "test-handler-01",
            "slope": 1.0,
            "intercept": 0.0,
        }

        response = client.post(self.endpoint, json=data)

        assert response.status_code == 200


class TestUpdate:
    @pytest.fixture
    def init(self):
        self.machine_id = "test-machine-01"
        self.sensor_id = "load01"
        self.endpoint = "/api/v1/sensors/" + self.sensor_id

    def test_normal(self, client, init):
        data = {
            "machine_id": self.machine_id,
            "sensor_name": "test-update",
            "sensor_type_id": "load",
            "handler_id": "test-handler-01",
            "slope": 10,
            "intercept": 10,
        }
        response = client.put(self.endpoint, json=data)

        assert response.status_code == 200

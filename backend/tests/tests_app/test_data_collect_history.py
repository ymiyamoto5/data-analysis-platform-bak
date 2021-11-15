import pytest


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/data_collect_histories"
        self.machine_id = "machine-test-01"

    def test_normal_db_select_all(self, client, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_normal_db_select_by_id(self, client, init):
        endpoint = f"{self.endpoint}/1"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_normal_db_select_by_machine_id(self, client, init):
        endpoint = f"{self.endpoint}/{self.machine_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_normal_db_select_latest_by_machine_id(self, client, init):
        endpoint = f"{self.endpoint}/{self.machine_id}/latest"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200


class TestUpdate:
    @pytest.fixture
    def init(self):
        self.id = 1
        self.endpoint = f"/api/v1/data_collect_histories/{self.id}"

    def test_normal(self, client, init):
        data = {
            "sampling_frequency": 777,
            "data_collect_history_details": [
                {
                    "data_collect_history_id": self.id,
                    "sensor_id": "stroke_displacement",
                    "sensor_name": "ストローク変位",
                    "sensor_type_id": "stroke_displacement",
                    "slope": 7.0,
                    "intercept": 7.0,
                },
                {
                    "data_collect_history_id": self.id,
                    "sensor_id": "load01",
                    "sensor_name": "荷重",
                    "sensor_type_id": "load01",
                    "slope": 7.0,
                    "intercept": 7.0,
                },
            ],
        }
        response = client.put(self.endpoint, json=data)

        assert response.status_code == 200


class TestDelete:
    @pytest.fixture
    def init(self):
        self.id = 1
        self.endpoint = f"/api/v1/data_collect_histories/{self.id}"

    def test_normal(self, client, init):

        response = client.delete(self.endpoint)

        assert response.status_code == 200

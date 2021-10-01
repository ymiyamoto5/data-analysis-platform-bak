import pytest
from backend.app.crud.crud_sensor import CRUDSensor


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/sensors"
        self.sensor_id = "load01"
        self.machine_id = "test-machine-001"

    def test_normal_db_select_all(self, client, mocker, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        mocker.patch.object(CRUDSensor, "select_all")

        assert actual_code == 200

    def test_normal_db_select_by_id(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.sensor_id}?machine_id={self.machine_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        mocker.patch.object(CRUDSensor, "select_by_id")

        assert actual_code == 200

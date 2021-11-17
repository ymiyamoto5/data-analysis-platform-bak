import pytest
from backend.app.crud.crud_sensor import CRUDSensor


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

    def test_db_select_all_failed(self, client, mocker, init):
        mocker.patch.object(CRUDSensor, "select_all", side_effect=Exception("some exception"))
        response = client.get(self.endpoint)

        assert response.status_code == 500

    def test_normal_db_select_by_id(self, client, init):
        endpoint = f"{self.endpoint}/{self.sensor_id}?machine_id={self.machine_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_by_id_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.sensor_id}?machine_id={self.machine_id}"
        mocker.patch.object(CRUDSensor, "select_by_id", side_effect=Exception("some exception"))
        response = client.get(endpoint)

        assert response.status_code == 500


class TestCreate:
    @pytest.fixture
    def init(self):
        # NOTE: 末尾スラッシュがないと307 redirectになってしまう。
        self.endpoint = "/api/v1/sensors/"
        self.data = {
            "sensor_name": "test-create",
            "sensor_type_id": "load",
            "handler_id": "test-handler-01",
            "slope": 1.0,
            "intercept": 0.0,
        }

    def test_normal(self, client, init):

        response = client.post(self.endpoint, json=self.data)

        assert response.status_code == 200

    # TODO: 例外処理が未実装
    # def test_not_unique_sensor_id(self, client, init):
    #     """重複しているsensor_id"""
    #     data = {
    #         "sensor_name": "test-create",
    #         "sensor_type_id": "load",
    #         "handler_id": "test-handler-01",
    #         "slope": 1.0,
    #         "intercept": 0.0,
    #     }

    #     response = client.post(self.endpoint, json=data)

    #     assert response.status_code == 400

    def test_insert_failed(self, client, mocker, init):
        mocker.patch.object(CRUDSensor, "insert", side_effect=Exception("some exception"))
        response = client.post(self.endpoint, json=self.data)

        assert response.status_code == 500


class TestUpdate:
    @pytest.fixture
    def init(self):
        self.sensor_id = "load01"
        self.endpoint = "/api/v1/sensors"
        self.data = {
            "machine_id": "test-machine-01",
            "sensor_name": "test-update",
            "sensor_type_id": "load",
            "handler_id": "test-handler-01",
            "slope": 10,
            "intercept": 10,
        }

    def test_normal(self, client, init):
        endpoint = f"{self.endpoint}/{self.sensor_id}"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 200

    def test_not_exist_machine_id(self, client, init):
        """存在しないsensor_id"""
        endpoint = f"{self.endpoint}/not-exist-sensor-id"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 404

    def test_update_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.sensor_id}"
        mocker.patch.object(CRUDSensor, "update", side_effect=Exception("some exception"))
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 500


class TestDelete:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/sensors"
        self.sensor_id = "load01"
        self.data = {
            "machine_id": "test-machine-01",
        }

    def test_normal(self, client, init):
        endpoint = f"{self.endpoint}/{self.sensor_id}"
        response = client.delete(endpoint, json=self.data)

        assert response.status_code == 200

    def test_not_exist_sensor_id(self, client, init):
        """存在しないsensor_id"""
        endpoint = f"{self.endpoint}/not-exist-sensor-id"
        response = client.delete(endpoint, json=self.data)

        assert response.status_code == 404

    def test_delete_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.sensor_id}"
        mocker.patch.object(CRUDSensor, "delete", side_effect=Exception("some exception"))
        response = client.delete(endpoint, json=self.data)

        assert response.status_code == 500

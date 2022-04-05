import pytest
from backend.app.crud.crud_sensor import CRUDSensor


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/sensors"
        self.sensor_id = "load01"

    machine_id_data = ["test-machine-01", "test-machine-02"]

    def test_normal_db_select_all(self, client, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_all_failed(self, client, mocker, init):
        mocker.patch.object(CRUDSensor, "select_all", side_effect=Exception("some exception"))
        response = client.get(self.endpoint)

        assert response.status_code == 500

    @pytest.mark.parametrize("machine_id", machine_id_data)
    def test_normal_db_select_by_id(self, client, init, machine_id):
        endpoint = f"{self.endpoint}/{self.sensor_id}?machine_id={machine_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    @pytest.mark.parametrize("machine_id", machine_id_data)
    def test_db_select_by_id_failed(self, client, mocker, init, machine_id):
        endpoint = f"{self.endpoint}/{self.sensor_id}?machine_id={machine_id}"
        mocker.patch.object(CRUDSensor, "select_by_id", side_effect=Exception("some exception"))
        response = client.get(endpoint)

        assert response.status_code == 500


class TestCreate:
    @pytest.fixture
    def init(self):
        # NOTE: 末尾スラッシュがないと307 redirectになってしまう。
        self.endpoint = "/api/v1/sensors/"

    test_create_data = [
        {
            "sensor_name": "test-create",
            "sensor_type_id": "load",
            "handler_id": "test-handler-01-1",
            "slope": 1.0,
            "intercept": 0.0,
        },
        {
            "sensor_name": "test-create",
            "sensor_type_id": "load",
            "handler_id": "test-handler-02",
            "slope": 1.0,
            "intercept": 0.0,
        },
    ]

    @pytest.mark.parametrize("data", test_create_data)
    def test_normal(self, client, init, data):

        response = client.post(self.endpoint, json=data)

        assert response.status_code == 200

    test_not_unique_data = [
        (
            {
                "sensor_name": "test-create",
                "sensor_type_id": "stroke_displacement",
                "handler_id": "test-handler-01-1",
                "slope": 1.0,
                "intercept": 0.0,
            },
            500,
        ),
        (
            {
                "sensor_name": "test-create",
                "sensor_type_id": "pulse",
                "handler_id": "test-handler-02",
                "slope": 1.0,
                "intercept": 0.0,
            },
            500,
        ),
    ]

    @pytest.mark.parametrize("data, expected_code", test_not_unique_data)
    def test_not_unique_sensor_id(self, client, init, data, expected_code):
        """stroke_displacementを重複して登録
        NOTE: load等のセンサーはサフィックスをつけるため、基本的に重複しない。
        """

        response = client.post(self.endpoint, json=data)

        assert response.status_code == expected_code

    @pytest.mark.parametrize("data", test_create_data)
    def test_insert_failed(self, client, mocker, init, data):
        mocker.patch.object(CRUDSensor, "insert", side_effect=Exception("some exception"))
        response = client.post(self.endpoint, json=data)

        assert response.status_code == 500


class TestUpdate:
    @pytest.fixture
    def init(self):
        self.sensor_id = "load01"
        self.endpoint = "/api/v1/sensors"

    test_update_data = [
        {
            "machine_id": "test-machine-01",
            "sensor_name": "test-update",
            "sensor_type_id": "load",
            "handler_id": "test-handler-01-1",
            "slope": 10,
            "intercept": 10,
        },
        {
            "machine_id": "test-machine-02",
            "sensor_name": "test-update",
            "sensor_type_id": "load",
            "handler_id": "test-handler-02",
            "slope": 10,
            "intercept": 10,
        },
    ]

    @pytest.mark.parametrize("data", test_update_data)
    def test_normal(self, client, init, data):
        endpoint = f"{self.endpoint}/{self.sensor_id}"
        response = client.put(endpoint, json=data)

        assert response.status_code == 200

    @pytest.mark.parametrize("data", test_update_data)
    def test_not_exist_machine_id(self, client, init, data):
        """存在しないsensor_id"""
        endpoint = f"{self.endpoint}/not-exist-sensor-id"
        response = client.put(endpoint, json=data)

        assert response.status_code == 404

    @pytest.mark.parametrize("data", test_update_data)
    def test_update_failed(self, client, mocker, init, data):
        endpoint = f"{self.endpoint}/{self.sensor_id}"
        mocker.patch.object(CRUDSensor, "update", side_effect=Exception("some exception"))
        response = client.put(endpoint, json=data)

        assert response.status_code == 500


class TestDelete:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/sensors"
        self.sensor_id = "load01"

    test_delete_data = [
        {
            "machine_id": "test-machine-01",
        },
        {
            "machine_id": "test-machine-02",
        },
    ]

    @pytest.mark.parametrize("data", test_delete_data)
    def test_normal(self, client, init, data):
        endpoint = f"{self.endpoint}/{self.sensor_id}"
        response = client.delete(endpoint, json=data)

        assert response.status_code == 200

    @pytest.mark.parametrize("data", test_delete_data)
    def test_not_exist_sensor_id(self, client, init, data):
        """存在しないsensor_id"""
        endpoint = f"{self.endpoint}/not-exist-sensor-id"
        response = client.delete(endpoint, json=data)

        assert response.status_code == 404

    @pytest.mark.parametrize("data", test_delete_data)
    def test_delete_failed(self, client, mocker, init, data):
        endpoint = f"{self.endpoint}/{self.sensor_id}"
        mocker.patch.object(CRUDSensor, "delete", side_effect=Exception("some exception"))
        response = client.delete(endpoint, json=data)

        assert response.status_code == 500

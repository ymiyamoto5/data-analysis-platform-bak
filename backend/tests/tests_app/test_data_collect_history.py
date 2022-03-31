import pytest
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.services.data_collect_history_service import \
    DataCollectHistoryService


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/data_collect_histories"
        self.machine_id = "test-machine-01"
        self.data_collect_history_id = 1

    def test_normal_db_select_all(self, client, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_all_failed(self, client, mocker, init):
        mocker.patch.object(CRUDDataCollectHistory, "select_all", side_effect=Exception("some exception"))
        response = client.get(self.endpoint)

        assert response.status_code == 500

    def test_normal_db_select_by_machine_id(self, client, init):
        endpoint = f"{self.endpoint}/{self.machine_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_by_machine_id_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.machine_id}"
        mocker.patch.object(CRUDDataCollectHistory, "select_by_machine_id", side_effect=Exception("some exception"))
        response = client.get(endpoint)

        assert response.status_code == 500

    def test_normal_db_select_latest_by_machine_id(self, client, init):
        endpoint = f"{self.endpoint}/{self.machine_id}/latest"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_latest_by_machine_id_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.machine_id}/latest"
        mocker.patch.object(CRUDDataCollectHistory, "select_latest_by_machine_id", side_effect=Exception("some exception"))
        response = client.get(endpoint)

        assert response.status_code == 500


class TestUpdate:
    @pytest.fixture
    def init(self):
        self.data_collect_history_id = 1
        self.endpoint = "/api/v1/data_collect_histories"
        self.data = {
            "sampling_frequency": 777,
            "data_collect_history_sensors": [
                {
                    "data_collect_history_id": self.data_collect_history_id,
                    "sensor_id": "stroke_displacement",
                    "sensor_name": "ストローク変位",
                    "sensor_type_id": "stroke_displacement",
                    "slope": 7.0,
                    "intercept": 7.0,
                },
                {
                    "data_collect_history_id": self.data_collect_history_id,
                    "sensor_id": "load01",
                    "sensor_name": "荷重",
                    "sensor_type_id": "load01",
                    "slope": 7.0,
                    "intercept": 7.0,
                },
            ],
        }

    def test_normal(self, client, init):
        endpoint = f"{self.endpoint}/{self.data_collect_history_id}"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 200

    def test_not_exist_data_collect_history_id(self, client, init):
        """存在しないdata_collect_history_id"""
        endpoint = f"{self.endpoint}/100"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 404

    def test_update_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.data_collect_history_id}"
        mocker.patch.object(CRUDDataCollectHistory, "update", side_effect=Exception("some exception"))
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 500


class TestDelete:
    @pytest.fixture
    def init(self):
        self.data_collect_history_id = 1
        self.endpoint = "/api/v1/data_collect_histories"

    def test_normal(self, client, mocker, init):
        """子が存在するdata_collect_history_id"""
        mocker.patch.object(DataCollectHistoryService, "delete_elastic_index")

        endpoint = f"{self.endpoint}/{self.data_collect_history_id}"
        response = client.delete(endpoint)

        assert response.status_code == 200

    def test_not_exist_data_collect_history_id(self, client, init):
        """存在しないdata_collect_history_id"""
        endpoint = f"{self.endpoint}/100"
        response = client.delete(endpoint)

        assert response.status_code == 404

    def test_delete_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.data_collect_history_id}"
        mocker.patch.object(CRUDDataCollectHistory, "delete", side_effect=Exception("some exception"))
        response = client.delete(endpoint)

        assert response.status_code == 500

import pytest
import json
from backend.data_collect_manager.models.sensor import Sensor
from backend.data_collect_manager.dao.sensor_dao import SensorDAO
from backend.common import common


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/sensors"
        self.sensor_id = "test_load"

    def test_normal_db_select_all(self, client, mocker, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        mocker.patch.object(SensorDAO, "select_all")

        assert actual_code == 200

    def test_normal_db_select_by_id(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.sensor_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        mocker.patch.object(SensorDAO, "select_by_id")

        assert actual_code == 200

    def test_db_select_all_failed(self, client, mocker, init):
        """Sensorを起点に関連エンティティを全結合したデータ取得失敗"""

        mocker.patch.object(
            SensorDAO, "select_all", side_effect=Exception("some exception")
        )

        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"読み取りに失敗しました: some exception"}\n' in response.data.decode()

    def test_db_select_by_id_failed(self, client, mocker, init):
        """指定Sensorのデータ取得失敗"""

        endpoint = f"{self.endpoint}/{self.sensor_id}"
        mocker.patch.object(
            SensorDAO, "select_by_id", side_effect=Exception("some exception")
        )

        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"読み取りに失敗しました: some exception"}\n' in response.data.decode()

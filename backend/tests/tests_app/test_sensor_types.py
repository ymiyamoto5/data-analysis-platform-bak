import pytest


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/sensor_types"

    def test_normal_db_select_all(self, client, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

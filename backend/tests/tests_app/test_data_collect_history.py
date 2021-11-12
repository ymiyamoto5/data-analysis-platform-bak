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

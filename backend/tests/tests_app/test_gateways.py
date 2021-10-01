import pytest
from backend.app.crud.crud_gateway import CRUDGateway


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/gateways"
        self.gateway_id = "test-GW-001"

    def test_normal_db_select_all(self, client, mocker, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        mocker.patch.object(CRUDGateway, "select_all")

        assert actual_code == 200

    def test_normal_db_select_by_id(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.gateway_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        mocker.patch.object(CRUDGateway, "select_by_id")

        assert actual_code == 200

import pytest
from backend.app.crud.crud_handler import CRUDHandler


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/handlers"
        self.handler_id = "test-handler-001"

    def test_normal_db_select_all(self, client, mocker, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        mocker.patch.object(CRUDHandler, "select_all")

        assert actual_code == 200

    def test_normal_db_select_by_id(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.handler_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        mocker.patch.object(CRUDHandler, "select_by_id")

        assert actual_code == 200

import pytest
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/data_collect_history"

    def test_normal_db_select_all(self, client, mocker, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        mocker.patch.object(CRUDDataCollectHistory, "select_all")

        assert actual_code == 200

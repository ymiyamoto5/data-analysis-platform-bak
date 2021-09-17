import pytest
from backend.app.crud.crud_handler import CRUDHandler


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/handlers"
        self.handler_id = "test_handler_001"

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

    def test_db_select_all_failed(self, client, mocker, init):
        """Handlerを起点に関連エンティティを全結合したデータ取得失敗"""

        mocker.patch.object(CRUDHandler, "select_all", side_effect=Exception("some exception"))

        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"読み取りに失敗しました: some exception"}\n' in response.data.decode()

    def test_db_select_by_id_failed(self, client, mocker, init):
        """指定Handlerのデータ取得失敗"""

        endpoint = f"{self.endpoint}/{self.handler_id}"
        mocker.patch.object(CRUDHandler, "select_by_id", side_effect=Exception("some exception"))

        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"読み取りに失敗しました: some exception"}\n' in response.data.decode()

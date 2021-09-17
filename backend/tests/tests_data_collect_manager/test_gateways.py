import pytest
from backend.app.crud.crud_gateway import CRUDGateway


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/gateways"
        self.gateway_id = "test_GW_001"

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

    def test_db_select_all_failed(self, client, mocker, init):
        """Gatewayを起点に関連エンティティを全結合したデータ取得失敗"""

        mocker.patch.object(CRUDGateway, "select_all", side_effect=Exception("some exception"))

        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"読み取りに失敗しました: some exception"}\n' in response.data.decode()

    def test_db_select_by_id_failed(self, client, mocker, init):
        """指定Gatewayのデータ取得失敗"""

        endpoint = f"{self.endpoint}/{self.gateway_id}"
        mocker.patch.object(CRUDGateway, "select_by_id", side_effect=Exception("some exception"))

        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"読み取りに失敗しました: some exception"}\n' in response.data.decode()

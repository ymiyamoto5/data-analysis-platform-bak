import pytest
from backend.app.crud.crud_machine_type import CRUDMachineType


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/machine_types"

    def test_normal_db_select_all(self, client, mocker, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        mocker.patch.object(CRUDMachineType, "select_all")

        assert actual_code == 200

    def test_db_select_all_failed(self, client, mocker, init):
        """MachineTypeの全データ取得失敗"""

        mocker.patch.object(CRUDMachineType, "select_all", side_effect=Exception("some exception"))

        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"読み取りに失敗しました: some exception"}\n' in response.data.decode()

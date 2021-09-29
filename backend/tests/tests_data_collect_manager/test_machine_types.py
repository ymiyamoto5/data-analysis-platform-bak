import pytest
import json
from backend.data_collect_manager.models.machine_type import MachineType
from backend.data_collect_manager.dao.machine_type_dao import MachineTypeDAO
from backend.common import common


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/machine_types"

    def test_normal_db_select_all(self, client, mocker, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        mocker.patch.object(MachineTypeDAO, "select_all")

        assert actual_code == 200

    def test_db_select_all_failed(self, client, mocker, init):
        """MachineTypeの全データ取得失敗"""

        mocker.patch.object(
            MachineTypeDAO, "select_all", side_effect=Exception("some exception")
        )

        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"読み取りに失敗しました: some exception"}\n' in response.data.decode()

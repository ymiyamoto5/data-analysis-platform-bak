import pytest
import json
from backend.data_collect_manager.models.data_collect_history import DataCollectHistory
from backend.data_collect_manager.dao.data_collect_history_dao import (
    DataCollectHistoryDAO,
)
from backend.common import common


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/data_collect_history"

    def test_normal_db_select_all(self, client, mocker, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        mocker.patch.object(DataCollectHistoryDAO, "select_all")

        assert actual_code == 200

    def test_db_select_all_failed(self, client, mocker, init):
        """データ収集履歴取得失敗"""

        mocker.patch.object(
            DataCollectHistoryDAO, "select_all", side_effect=Exception("some exception")
        )

        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 500
        assert '{"message":"読み取りに失敗しました: some exception"}\n' in response.data.decode()

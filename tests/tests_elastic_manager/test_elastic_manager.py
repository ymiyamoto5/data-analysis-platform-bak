import elasticsearch
from elastic_manager.elastic_manager import ElasticManager


class TestGetLatestEventsIndex:
    def test_normal(self, mocker):
        """ 正常系：events_indexの最新が取得できる """

        mocker.patch.object(
            elasticsearch.client.CatClient,
            "indices",
            return_value="events-20201201123456\nevents-20201201133456\nevents-20201201143456",
        )

        actual: str = ElasticManager.get_latest_events_index()
        expected: str = "events-20201201143456"

        assert actual == expected

    def test_index_not_exists_exception(self, mocker):
        """ 異常系：events_indexが存在しない """

        mocker.patch.object(
            elasticsearch.client.CatClient, "indices", return_value="",
        )

        actual = ElasticManager.get_latest_events_index()
        expected = None

        assert actual == expected


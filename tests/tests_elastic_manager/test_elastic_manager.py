"""
 ==================================
  test_elastic_manager.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import elasticsearch
from elastic_manager.elastic_manager import ElasticManager


class TestGetLatestIndex:
    def test_normal(self, mocker):
        """ 正常系：events_indexの最新が取得できる """

        mocker.patch.object(
            elasticsearch.client.CatClient,
            "indices",
            return_value="events-20201201123456\nevents-20201201133456\nevents-20201201143456",
        )

        actual: str = ElasticManager.get_latest_index("events-*")
        expected: str = "events-20201201143456"

        assert actual == expected

    def test_index_not_exists_exception(self, mocker):
        """ 異常系：events_indexが存在しない """

        mocker.patch.object(
            elasticsearch.client.CatClient, "indices", return_value="",
        )

        actual = ElasticManager.get_latest_index("events-*")
        expected = None

        assert actual == expected


class TestDeleteDataBySeqNum:
    def test_normal(self, mocker):
        """ 正常系：delete_by_queryが一度のみ呼び出されること """

        mocker.patch.object(ElasticManager, "_check_index", return_value=(True, ""))
        mock_delete_by_query = mocker.patch.object(
            elasticsearch.Elasticsearch, "delete_by_query", return_value={"deleted": 10, "failures": []}
        )

        ElasticManager.delete_data_by_seq_num("tmp_index", 1, 10)

        mock_delete_by_query.assert_called_once()

    def test_exception_1(self, mocker):
        """ 異常系：startがマイナス """

        mocker.patch.object(ElasticManager, "_check_index", return_value=(True, ""))
        mock_delete_by_query = mocker.patch.object(
            elasticsearch.Elasticsearch, "delete_by_query", return_value={"deleted": 10, "failures": []}
        )

        ElasticManager.delete_data_by_seq_num("tmp_index", -1, 10)

        mock_delete_by_query.assert_not_called()

    def test_exception_2(self, mocker):
        """ 異常系：endがマイナス """

        mocker.patch.object(ElasticManager, "_check_index", return_value=(True, ""))
        mock_delete_by_query = mocker.patch.object(
            elasticsearch.Elasticsearch, "delete_by_query", return_value={"deleted": 10, "failures": []}
        )

        ElasticManager.delete_data_by_seq_num("tmp_index", 1, -1)

        mock_delete_by_query.assert_not_called()

    def test_exception_3(self, mocker):
        """ 異常系：indexが不正 """

        mocker.patch.object(ElasticManager, "_check_index", return_value=(False, "インデックスを指定してください。"))
        mock_delete_by_query = mocker.patch.object(
            elasticsearch.Elasticsearch, "delete_by_query", return_value={"deleted": 10, "failures": []}
        )

        ElasticManager.delete_data_by_seq_num("tmp_index", 1, 10)

        mock_delete_by_query.assert_not_called()

    def test_delete_fail_exception(self, mocker):
        """ 異常系: 削除失敗 """

        mocker.patch.object(ElasticManager, "_check_index", return_value=(True, ""))
        mock_delete_by_query = mocker.patch.object(
            elasticsearch.Elasticsearch, "delete_by_query", return_value={"deleted": 10, "failures": ["xxx", "yyy"]}
        )

        ElasticManager.delete_data_by_seq_num("tmp_index", 1, 10)

        mock_delete_by_query.assert_called_once()


class TestDeleteDataByShotNum:
    def test_normal(self, mocker):
        """ 正常系：delete_by_queryが一度のみ呼び出されること """

        mocker.patch.object(ElasticManager, "_check_index", return_value=(True, ""))
        mock_delete_by_query = mocker.patch.object(
            elasticsearch.Elasticsearch, "delete_by_query", return_value={"deleted": 10, "failures": []}
        )

        ElasticManager.delete_data_by_shot_num("tmp_index", 1)

        mock_delete_by_query.assert_called_once()

    def test_exception_1(self, mocker):
        """ 異常系：shot_numberがマイナス """

        mocker.patch.object(ElasticManager, "_check_index", return_value=(True, ""))
        mock_delete_by_query = mocker.patch.object(
            elasticsearch.Elasticsearch, "delete_by_query", return_value={"deleted": 10, "failures": []}
        )

        ElasticManager.delete_data_by_shot_num("tmp_index", -1)

        mock_delete_by_query.assert_not_called()

    def test_exception_2(self, mocker):
        """ 異常系：indexが不正 """

        mocker.patch.object(ElasticManager, "_check_index", return_value=(False, "インデックスを指定してください。"))
        mock_delete_by_query = mocker.patch.object(
            elasticsearch.Elasticsearch, "delete_by_query", return_value={"deleted": 10, "failures": []}
        )

        ElasticManager.delete_data_by_shot_num("tmp_index", 1)

        mock_delete_by_query.assert_not_called()

    def test_delete_fail_exception(self, mocker):
        """ 異常系: 削除失敗 """

        mocker.patch.object(ElasticManager, "_check_index", return_value=(True, ""))
        mock_delete_by_query = mocker.patch.object(
            elasticsearch.Elasticsearch, "delete_by_query", return_value={"deleted": 10, "failures": ["xxx", "yyy"]}
        )

        ElasticManager.delete_data_by_shot_num("tmp_index", 1)

        mock_delete_by_query.assert_called_once()

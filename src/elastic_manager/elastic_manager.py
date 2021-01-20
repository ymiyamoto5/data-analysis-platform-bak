""" Elasticsearchへの各種処理を行うwrapperモジュール """

from elasticsearch import Elasticsearch
from elasticsearch import exceptions
from elasticsearch import helpers
import os
import sys
import pandas as pd
import json
from typing import Iterable, Iterator, Tuple, List, Optional, Final
import multiprocessing
from datetime import datetime
import logging

es_logger = logging.getLogger("elasticsearch")
es_logger.setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import common

ELASTIC_URL: Final[str] = common.get_config_value(common.APP_CONFIG_PATH, "elastic_url")
ELASTIC_USER: Final[str] = common.get_config_value(common.APP_CONFIG_PATH, "elastic_user")
ELASTIC_PASSWORD: Final[str] = common.get_config_value(common.APP_CONFIG_PATH, "elastic_password")


class ElasticManager:
    """ Elasticsearchへの各種処理を行うwrapperクラス """

    es = Elasticsearch(hosts=ELASTIC_URL, http_auth=(ELASTIC_USER, ELASTIC_PASSWORD), timeout=50000)

    @classmethod
    def show_indices(cls, index: str = "*") -> pd.DataFrame:
        """ インデックス一覧のDataFrameを返す """

        _indices = cls.es.cat.indices(
            index=index, v=True, h=["index", "docs.count", "store.size"], bytes="kb"
        ).splitlines()

        indices_list = [x.split() for x in _indices]

        df = pd.DataFrame(indices_list[1:], columns=indices_list[0]).sort_values("index").reset_index(drop=True)
        return df

    @classmethod
    def get_latest_events_index(cls) -> Optional[str]:
        """ 最新のevents_indexの名前を返す """

        _indices = cls.es.cat.indices(index="events-*", s="index", h="index").splitlines()
        if len(_indices) == 0:
            logger.error("events index not found.")
            return None
        return _indices[-1]

    @classmethod
    def get_latest_events_index_doc(cls, latest_events_index: str) -> Optional[dict]:
        """ 最新のevents_indexの一番最後に記録されたdocumentを返す。
            events_indexにdocumentが無い場合はNoneを返す。
        """

        if cls.count(latest_events_index) == 0:
            return None

        body = {"sort": {"event_id": {"order": "desc"}}}

        result = cls.es.search(index=latest_events_index, body=body, size=1)
        return result["hits"]["hits"][0]["_source"]

    @classmethod
    def get_docs(cls, index: str, query: dict) -> List[dict]:
        """ 対象インデックスのdocumentを返す """

        body = query
        result = cls.es.search(index=index, body=body, size=10_000)

        return [x["_source"] for x in result["hits"]["hits"]]

    @classmethod
    def delete_index(cls, index: str) -> None:
        """ インデックスを削除する """

        is_valid_index: bool
        message: str
        is_valid_index, message = ElasticManager.__check_index(index)

        if not is_valid_index:
            logger.error(message)
            return

        result: dict = cls.es.indices.delete(index=index)

        if result["acknowledged"]:
            logger.info(f"{index} deleted.")
        else:
            logger.error(f"{index} cannot deleted")

    @classmethod
    def delete_data_by_seq_num(cls, index: str, start: int, end: int) -> None:
        """ documentを削除する（連番指定） """

        is_valid_index: bool
        message: str
        is_valid_index, message = ElasticManager.__check_index(index)

        if not is_valid_index:
            logger.error(message)
            return

        if start > end:
            logger.error(f"end({end})はstart({start})より大きい値を設定してください。")
            return

        if start < 0 or end < 0:
            logger.error("Invalid value.")
            return

        body: dict = {"query": {"range": {"sequential_number": {"gte": start, "lte": end}}}}

        result: dict = cls.es.delete_by_query(index=index, body=body, refresh=True)

        if len(result["failures"]) != 0:
            logger.error("Failed to delete data.")
            for failure in result["failures"]:
                logger.error(failure)
            return

        logger.info(f"Delete was successful. {result['deleted']} docs deleted.")

    @classmethod
    def delete_data_by_shot_num(cls, index: str, shot_number: int) -> None:
        """ documentを削除する（shot番号指定） """

        is_valid_index: bool
        message: str
        is_valid_index, message = ElasticManager.__check_index(index)

        if not is_valid_index:
            logger.error(message)
            return

        if shot_number < 0:
            print("ショット番号が不正です。")

        query: dict = {"term": {"shot_number": shot_number}}

        result: dict = cls.es.delete_by_query(index=index, body=query, refresh=True)

        if len(result["failures"]) != 0:
            logger.error("Failed to delete data.")
            for failure in result["failures"]:
                logger.error(failure)
            return

        logger.info(f"Delete was successful. {result['deleted']} docs deleted.")

    @classmethod
    def __check_index(cls, index: str) -> Tuple[bool, str]:
        """ インデックスが指定されているかチェックする """

        if index == "":
            message = "インデックスを指定してください。"
            return False, message

        if not cls.exists_index(index):
            message = f"{index}が存在しません。"
            return False, message

        return True, ""

    @classmethod
    def delete_exists_index(cls, index: str) -> None:
        """ 既存のインデックスを削除する """

        if cls.exists_index(index):
            result: dict = cls.es.indices.delete(index=index)
            logger.info(f"delete index '{index}' finished. result: {result}")

    @classmethod
    def exists_index(cls, index: str) -> bool:
        """ インデックスの存在確認 """
        return cls.es.indices.exists(index=index)

    @classmethod
    def create_index(cls, index: str, mapping_file: str = None, setting_file: str = None) -> bool:
        """ インデックスを作成する。 """

        # body = {"settings": {"index": {"max_result_window": 30000}}}
        body = {}

        if setting_file:
            with open(setting_file) as f:
                d = json.load(f)
                body["settings"] = d

        if mapping_file:
            with open(mapping_file) as f:
                d = json.load(f)
                body["mappings"] = d

        result: dict = cls.es.indices.create(index=index, body=body)

        if not result["acknowledged"]:
            logger.error(f"create index '{index}' failed. result: {result}")
            return False

        logger.info(f"create index '{index}' finished. result: {result}")
        return True

    @classmethod
    def create_doc(cls, index: str, doc_id: str, query: dict) -> bool:
        """ documentの作成 """

        if not cls.exists_index(index):
            logger.error(f"'{index} is not exists.")
            return False

        try:
            cls.es.create(index=index, id=doc_id, body=query, refresh=True)
            return True

        except exceptions.RequestError as e:
            logger.error(str(e))
            return False

    @classmethod
    def update_doc(cls, index: str, doc_id: str, query: dict) -> bool:
        """ documentの更新 """

        if not cls.exists_index(index):
            logger.error(f"'{index} is not exists.")
            return False

        body: dict = {"doc": query}

        try:
            cls.es.update(index=index, id=doc_id, body=body, refresh=True)
            return True

        except exceptions.RequestError as e:
            logger.error(str(e))
            return False

    @classmethod
    def multi_process_bulk_lazy_join(
        cls, data: List[dict], index_to_import: str, num_of_process: int = 8, chunk_size: int = 5000
    ) -> List[multiprocessing.context.Process]:
        """ マルチプロセスでbulk insertする。processリストを返却し、呼び出し元でjoinする。 """

        num_of_data: int = len(data)

        # データをプロセッサの数に均等分配
        data_num_by_proc: List[int] = [(num_of_data + i) // num_of_process for i in range(num_of_process)]

        procs: List[multiprocessing.context.Process] = []
        start_index: int = 0
        for proc_number, data_num in enumerate(data_num_by_proc):
            end_index: int = start_index + data_num
            target_data: list = data[start_index:end_index]
            start_index += data_num

            logger.debug(f"process {proc_number} will execute {len(target_data)} data.")

            proc: multiprocessing.context.Process = multiprocessing.Process(
                target=cls.bulk_insert, args=(target_data, index_to_import, chunk_size)
            )
            proc.start()
            procs.append(proc)

        return procs

    @classmethod
    def bulk_insert(cls, data_list: List[dict], index_to_import: str, chunk_size: int = 500) -> None:
        """
         マルチプロセスで実行する処理。渡されたデータをもとにElasticsearchにデータ投入する。
        """

        # プロセスごとにコネクションが必要
        # https://github.com/elastic/elasticsearch-py/issues/638
        # TODO: 接続先定義が複数個所に分かれてしまっている。接続先はクラス変数を辞める？
        es = Elasticsearch(hosts=ELASTIC_URL, http_auth=(ELASTIC_USER, ELASTIC_PASSWORD), timeout=50000)

        actions: Tuple[dict] = ({"_index": index_to_import, "_source": x} for x in data_list)
        helpers.bulk(es, actions, chunk_size=chunk_size, stats_only=True, raise_on_error=False)

    @classmethod
    def count(cls, index: str) -> int:
        result: dict = cls.es.count(index=index)
        return result["count"]

    @classmethod
    def multi_process_range_scan(cls, index: str, num_of_data: int, num_of_process: int = 12) -> List[dict]:
        """ マルチプロセスでrange scanする。 """

        logger.info(f"Data read start. data_count: {num_of_data}.")

        # データをプロセッサの数に均等分配
        data_num_by_proc: List[int] = [(num_of_data + i) // num_of_process for i in range(num_of_process)]

        # マルチプロセスの結果格納用
        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        procs: List[multiprocessing.context.Process] = []
        start_index: int = 0
        for proc_number, data_num in enumerate(data_num_by_proc):
            end_index: int = start_index + data_num

            proc: multiprocessing.context.Process = multiprocessing.Process(
                target=cls.range_scan, args=(index, proc_number, start_index, end_index, return_dict)
            )
            proc.start()
            procs.append(proc)

            start_index: int = end_index

        for proc in procs:
            proc.join()

        # マルチプロセスの結果をマージする
        result = []
        for proc in range(num_of_process):
            for data in return_dict[proc]:
                result.append(data)

        return result

    @classmethod
    def range_scan(cls, index: str, proc_num: int, start: int, end: int, return_dict: list) -> Iterator:
        """ データをレンジスキャンした結果を返す。
            Pythonのrange関数に合わせ、endはひとつ前までを返す仕様とする。
        """

        # プロセスごとにコネクションが必要
        # https://github.com/elastic/elasticsearch-py/issues/638
        es = Elasticsearch(hosts=ELASTIC_URL, http_auth=(ELASTIC_USER, ELASTIC_PASSWORD), timeout=50000)

        body: dict = {
            "query": {"range": {"sequential_number": {"gte": start, "lte": end - 1}}},
        }

        data_gen: Iterable = helpers.scan(client=es, index=index, query=body)
        data = [x["_source"] for x in data_gen]

        return_dict[proc_num] = data


if __name__ == "__main__":
    pass

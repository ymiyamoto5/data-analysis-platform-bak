"""
 ==================================
  elastic_manager.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import json
import multiprocessing
import os
from typing import Any, Collection, Dict, Final, Generator, Iterable, List, Optional, Tuple

import pandas as pd
from backend.common import common
from backend.common.common_logger import logger
from elasticsearch import Elasticsearch, exceptions, helpers

ELASTIC_URL: Final[str] = os.environ["ElasticUrl"]
ELASTIC_USER: Final[str] = os.environ["ElasticUser"]
ELASTIC_PASSWORD: Final[str] = os.environ["ElasticPassword"]


class ElasticManager:
    """Elasticsearchへの各種処理を行うwrapperクラス"""

    es = Elasticsearch(hosts=ELASTIC_URL, http_auth=(ELASTIC_USER, ELASTIC_PASSWORD), timeout=50000)

    @classmethod
    def show_indices(cls, index: str = "*") -> pd.DataFrame:
        """インデックス一覧のDataFrameを返す"""

        _indices = cls.es.cat.indices(index=index, v=True, h=["index", "docs.count", "store.size"], bytes="kb").splitlines()

        indices_list = [x.split() for x in _indices]

        df = pd.DataFrame(indices_list[1:], columns=indices_list[0]).sort_values("index").reset_index(drop=True)
        return df

    @classmethod
    def get_latest_index(cls, index) -> Optional[str]:
        """引数で指定したindexに一致する最新のインデックス名を返す"""

        _indices: List[str] = cls.es.cat.indices(index=index, s="index", h="index").splitlines()
        if len(_indices) == 0:
            logger.error("Index not found.")
            return None

        return _indices[-1]

    @classmethod
    def get_docs(cls, index: str, query: dict, size: int = common.ELASTIC_MAX_DOC_SIZE) -> List[dict]:
        """対象インデックスのdocumentを返す。documentがない場合は空のリストを返す。
        取得件数はデフォルトで10,000件。
        """

        result = cls.es.search(index=index, body=query, size=size)
        return [x["_source"] for x in result["hits"]["hits"]]

    @classmethod
    def get_docs_with_id(cls, index: str, query: dict, size: int = common.ELASTIC_MAX_DOC_SIZE) -> List[dict]:
        """対象インデックスのdocumentをdocument_id付きで返す。documentがない場合は空のリストを返す。
        取得件数はデフォルトで10,000件。
        """

        result = cls.es.search(index=index, body=query, size=size)

        ret_list = []
        for x in result["hits"]["hits"]:
            d = x["_source"]
            d["id"] = x["_id"]
            ret_list.append(d)

        return ret_list

    @classmethod
    def delete_index(cls, index: str) -> None:
        """インデックスを削除する"""

        is_valid_index: bool
        message: str
        is_valid_index, message = ElasticManager._check_index(index)

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
        """documentを削除する（連番指定）"""

        is_valid_index: bool
        message: str
        is_valid_index, message = ElasticManager._check_index(index)

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

        logger.info(f"Delete successful. {result['deleted']} docs deleted.")

    @classmethod
    def delete_data_by_shot_num(cls, index: str, shot_number: int) -> None:
        """documentを削除する（shot番号指定）"""

        is_valid_index: bool
        message: str
        is_valid_index, message = ElasticManager._check_index(index)

        if not is_valid_index:
            logger.error(message)
            return

        if shot_number < 0:
            logger.error("ショット番号が不正です。")
            return

        body: dict = {"query": {"term": {"shot_number": shot_number}}}

        result: dict = cls.es.delete_by_query(index=index, body=body, refresh=True)

        if len(result["failures"]) != 0:
            logger.error("Failed to delete data.")
            for failure in result["failures"]:
                logger.error(failure)
            return

        logger.info(f"Delete was successful. {result['deleted']} docs deleted.")

    @classmethod
    def _check_index(cls, index: str) -> Tuple[bool, str]:
        """インデックスが指定されているかチェックする"""

        if index == "":
            message = "インデックスを指定してください。"
            return False, message

        if not cls.exists_index(index):
            message = f"{index}が存在しません。"
            return False, message

        return True, ""

    @classmethod
    def delete_exists_index(cls, index: str) -> None:
        """既存のインデックスを削除する"""

        if cls.exists_index(index):
            result: dict = cls.es.indices.delete(index=index)
            logger.info(f"delete index '{index}' finished. result: {result}")

    @classmethod
    def exists_index(cls, index: str) -> bool:
        """インデックスの存在確認"""
        return cls.es.indices.exists(index=index)

    @classmethod
    def create_index(cls, index: str, mapping_file: str = None, setting_file: str = None) -> bool:
        """インデックスを作成する。"""

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
    def create_doc(cls, index: str, query: dict, doc_id: Optional[str] = None) -> bool:
        """documentの作成"""

        if not cls.exists_index(index):
            logger.error(f"'{index} is not exists.")
            return False

        try:
            cls.es.index(index=index, body=query, refresh=True)
            return True

        except exceptions.RequestError as e:
            logger.error(str(e))
            return False

    @classmethod
    def update_doc(cls, index: str, doc_id: str, query: dict) -> bool:
        """documentの更新"""

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
    def delete_doc(cls, index: str, doc_id: str) -> bool:
        """documentの削除"""

        if not cls.exists_index(index):
            logger.error(f"'{index} is not exists.")
            return False

        try:
            cls.es.delete(index=index, id=doc_id, refresh=True)
            return True

        except exceptions.RequestError as e:
            logger.error(str(e))
            return False

    @classmethod
    def multi_process_bulk_lazy_join(
        cls,
        data: List[dict],
        index_to_import: str,
        num_of_process: int = common.NUM_OF_PROCESS,
        chunk_size: int = 5000,
    ) -> List[multiprocessing.context.Process]:
        """マルチプロセスでbulk insertする。processリストを返却し、呼び出し元でjoinする。"""

        num_of_data: int = len(data)

        # NOTE: データをプロセッサの数に均等分配
        # ex) 13個のデータを4プロセスに分割すると[3, 3, 3, 4]
        #     [0:3]の3個, [3:6]の3個, [6:9]の3個, [9:13]の4個をプロセスごとに処理する。
        data_num_by_proc: List[int] = [(num_of_data + i) // num_of_process for i in range(num_of_process)]

        procs: List[multiprocessing.context.Process] = []
        start_index: int = 0
        for proc_number, data_num in enumerate(data_num_by_proc):
            end_index: int = start_index + data_num
            target_data: list = data[start_index:end_index]
            start_index = end_index

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
        es = Elasticsearch(hosts=ELASTIC_URL, http_auth=(ELASTIC_USER, ELASTIC_PASSWORD), timeout=50000)

        actions: Generator[Dict[str, Collection[Any]], None, None] = ({"_index": index_to_import, "_source": x} for x in data_list)
        helpers.bulk(es, actions, chunk_size=chunk_size, stats_only=True, raise_on_error=False)

    @classmethod
    def count(cls, index: str) -> int:
        result: Dict[str, int] = cls.es.count(index=index)
        return result["count"]

    @classmethod
    def multi_process_range_scan(
        cls,
        index: str,
        start_index: int,
        num_of_data: int,
        num_of_process: int = common.NUM_OF_PROCESS,
    ) -> List[dict]:
        """マルチプロセスでrange scanする。"""

        logger.info(f"Data read start. data_count: {num_of_data}.")

        # データをプロセッサの数に均等分配
        data_num_by_proc: List[int] = [(num_of_data + i) // num_of_process for i in range(num_of_process)]

        # マルチプロセスの結果格納用
        manager = multiprocessing.Manager()
        return_dict: Dict[int, List[dict]] = manager.dict()

        procs: List[multiprocessing.context.Process] = []

        for proc_number, data_num in enumerate(data_num_by_proc):
            end_index: int = start_index + data_num

            proc: multiprocessing.context.Process = multiprocessing.Process(
                target=cls.range_scan,
                args=(index, proc_number, start_index, end_index, return_dict),
            )
            proc.start()
            procs.append(proc)

            start_index = end_index

        for proc in procs:
            proc.join()

        # マルチプロセスの結果をマージする
        result = []
        for proc_number in range(num_of_process):
            for data in return_dict[proc_number]:
                result.append(data)

        return result

    @classmethod
    def range_scan(cls, index: str, proc_num: int, start: int, end: int, return_dict: list) -> None:
        """データをレンジスキャンした結果を返す。
        Pythonのrange関数に合わせ、endはひとつ前までを返す仕様とする。
        """

        # プロセスごとにコネクションが必要
        # https://github.com/elastic/elasticsearch-py/issues/638
        es = Elasticsearch(hosts=ELASTIC_URL, http_auth=(ELASTIC_USER, ELASTIC_PASSWORD), timeout=50000)

        body: dict = {
            "query": {"range": {"sequential_number": {"gte": start, "lte": end - 1}}},
        }

        data_gen: Iterable = helpers.scan(client=es, index=index, query=body)
        data: List[dict] = [x["_source"] for x in data_gen]

        return_dict[proc_num] = data

    @classmethod
    def scan_docs(cls, index: str, query: dict, preserve_order: bool = False) -> List[dict]:
        """ドキュメントの範囲スキャン"""

        es = Elasticsearch(hosts=ELASTIC_URL, http_auth=(ELASTIC_USER, ELASTIC_PASSWORD), timeout=50000)

        data_gen: Iterable = helpers.scan(client=es, index=index, query=query, preserve_order=preserve_order)
        data: List[dict] = [x["_source"] for x in data_gen]

        return data


if __name__ == "__main__":
    pass

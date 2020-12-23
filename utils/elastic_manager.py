""" Elasticsearchへの各種処理を行うwrapperモジュール """

from elasticsearch import Elasticsearch
from elasticsearch import exceptions
from elasticsearch import helpers
from elasticsearch import AsyncElasticsearch
import pandas as pd
import json
from typing import Iterable, Iterator
import multiprocessing
from datetime import datetime
import logging
from itertools import repeat
from functools import partial

es_logger = logging.getLogger("elasticsearch")
es_logger.setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class ElasticManager:
    """ Elasticsearchへの各種処理を行うwrapperクラス """

    es = Elasticsearch(hosts="localhost:9200", http_auth=("elastic", "P@ssw0rd12345"), timeout=50000)
    async_es = AsyncElasticsearch(hosts="localhost:9200", http_auth=("elastic", "P@ssw0rd12345"), timeout=50000)

    @classmethod
    def show_indices(cls, show_all_index: bool = False) -> pd.DataFrame:
        """
         インデックス一覧のDataFrameを返す。

        Args:
            show_all_index: Trueの場合、すべてのインデックスを表示する。
                            デフォルトはFalseで、本プロジェクトに関係するインデックスのみ表示する。
        """

        if show_all_index:
            _indices = cls.es.cat.indices(
                index="*", v=True, h=["index", "docs.count", "store.size"], bytes="kb"
            ).splitlines()
        else:
            _indices = cls.es.cat.indices(
                index=["rawdata-*", "shots-*", "events-*", "analyzed-*"],
                v=True,
                h=["index", "docs.count", "store.size"],
                bytes="kb",
            ).splitlines()

        indices_list = [x.split() for x in _indices]

        df = pd.DataFrame(indices_list[1:], columns=indices_list[0])

        return df

    @classmethod
    def get_latest_events_index(cls) -> str:
        """ 最新のevents_indexの名前を返す """

        _indices = cls.es.cat.indices(index="events-*", s="index", h="index").splitlines()
        if len(_indices) == 0:
            logger.error("events index not found.")
            return None
        return _indices[-1]

    @classmethod
    def get_latest_events_index_doc(cls, latest_events_index: str) -> dict:
        """ 最新のevents_indexの一番最後に記録されたdocumentを返す。
            events_indexにdocumentが無い場合はNoneを返す。
        """

        if cls.count(latest_events_index) == 0:
            return None

        body = {"sort": {"event_id": {"order": "desc"}}}

        result = cls.es.search(index=latest_events_index, body=body, size=1)
        return result["hits"]["hits"][0]["_source"]

    @classmethod
    def get_all_doc(cls, index: str, query: dict) -> list:
        """ 対象インデックスの全documentを返す """

        body = query
        result = cls.es.search(index=index, body=body, size=10_000)

        return [x["_source"] for x in result["hits"]["hits"]]

    @classmethod
    def delete_index(cls, index: str) -> None:
        """ インデックスを削除する """

        is_valid_index, message = ElasticManager.__check_index(index)

        if not is_valid_index:
            print(message)
            return

        result = cls.es.indices.delete(index=index)

        if result["acknowledged"]:
            print(f"{index}を削除しました。")
        else:
            print(f"エラー：{index}を削除できませんでした。")

    @classmethod
    def delete_data_by_seq_num(cls, index: str, start: int, end: int) -> None:
        """ documentを削除する（連番指定） """

        is_valid_index, message = ElasticManager.__check_index(index)

        if not is_valid_index:
            print(message)
            return

        if start > end:
            print(f"end({end})はstart({start})より大きい値を設定してください。")
            return

        if start < 0 or end < 0:
            print("連番の値が不正です。")
            return

        body = {"query": {"range": {"sequential_number": {"gte": start, "lte": end}}}}

        result = cls.es.delete_by_query(index=index, body=body, refresh=True)

        if len(result["failures"]) != 0:
            print("エラー：データ削除に失敗しました。")
            for failure in result["failures"]:
                print(failure)
            return

        print(f"データを{result['deleted']}件削除しました。")

    @classmethod
    def delete_data_by_shot_num(cls, index: str, shot_number: int) -> None:
        """ documentを削除する（shot番号指定） """

        is_valid_index, message = ElasticManager.__check_index(index)

        if not is_valid_index:
            print(message)
            return

        if shot_number < 0:
            print("ショット番号が不正です。")

        query = {"term": {"shot_number": shot_number}}

        result = cls.es.delete_by_query(index=index, body=query, refresh=True)

        if len(result["failures"]) != 0:
            print("エラー：データ削除に失敗しました。")
            for failure in result["failures"]:
                print(failure)
            return

        print(f"データを{result['deleted']}件削除しました。")

    @classmethod
    def __check_index(cls, index: str):
        """ インデックスが指定されているかチェックする """

        if index == "":
            message = "エラー：インデックスを指定してください。"
            return False, message

        if not cls.exists_index(index):
            message = f"エラー：{index}が存在しません。"
            return False, message

        return True, ""

    @classmethod
    def delete_exists_index(cls, index: str) -> None:
        """ 既存のインデックスを削除する """

        if cls.exists_index(index):
            result = cls.es.indices.delete(index=index)
            logger.info(f"delete index '{index}' finished. result: {result}")

    @classmethod
    def exists_index(cls, index: str):
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
            # logger.info("create document finished.")
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
            # logger.info("update document finished.")
            return True

        except exceptions.RequestError as e:
            logger.error(str(e))
            return False

    @classmethod
    async def async_bulk(cls, data: list):
        await helpers.async_bulk(cls.async_es, data, chunk_size=10000)

    @classmethod
    async def async_multi_process_bulk(cls, data: list):
        # args = list(zip(repeat(cls.async_es), data))
        # with multiprocessing.Pool(8) as p:
        #     # p.map_async(cls.async_bulk, data)
        #     # async_es = AsyncElasticsearch(
        #     #     hosts="localhost:9200", http_auth=("elastic", "P@ssw0rd12345"), timeout=50000
        #     # )
        #     p.starmap_async(helpers.async_bulk, args)
        pass

    @classmethod
    def parallel_bulk(cls, doc_generator: Iterable, thread_count: int = 4, chunk_size: int = 500) -> None:
        """ 指定したスレッド数でbulk insertする。 """

        for success, info in helpers.parallel_bulk(
            cls.es, doc_generator, chunk_size=chunk_size, thread_count=thread_count
        ):
            if not success:
                print("A document failed:", info)

    @classmethod
    def multi_process_bulk_lazy_join(
        cls, data: list, index_to_import: str, num_of_process=4, chunk_size: int = 500
    ) -> list:
        """ マルチプロセスでbulk insertする。map版試作 """
        num_of_data = len(data)
        # logger.info(f"Start writing to Elasticsearch. data_count:{num_of_data}, process_count:{num_of_process}")

        batch_size, mod = divmod(num_of_data, num_of_process)

        procs: list = []
        for i in range(num_of_process):
            start_index: int = i * batch_size
            end_index: int = start_index + batch_size
            target_data = data[start_index:end_index]
            # 最後のプロセスには余り分を含めたデータを処理させる
            if i == num_of_process - 1:
                target_data = data[start_index:]

            proc = multiprocessing.Process(target=cls.bulk_insert, args=(target_data, index_to_import, chunk_size,))
            proc.start()
            procs.append(proc)

        return procs

    @classmethod
    def multi_process_bulk(cls, data: list, index_to_import: str, num_of_process=4, chunk_size: int = 500) -> None:
        """ マルチプロセスでbulk insertする。 """

        num_of_data = len(data)
        # logger.info(f"Start writing to Elasticsearch. data_count:{num_of_data}, process_count:{num_of_process}")

        batch_size, mod = divmod(num_of_data, num_of_process)

        procs: list = []
        for i in range(num_of_process):
            start_index: int = i * batch_size
            end_index: int = start_index + batch_size
            target_data = data[start_index:end_index]
            # 最後のプロセスには余り分を含めたデータを処理させる
            if i == num_of_process - 1:
                target_data = data[start_index:]

            proc = multiprocessing.Process(target=cls.bulk_insert, args=(target_data, index_to_import, chunk_size,))
            proc.start()
            procs.append(proc)

        for proc in procs:
            proc.join()

        # logger.info(f"Finished. {num_of_data} have been written.")

    @classmethod
    def bulk_insert(cls, data_list: list, index_to_import: str, chunk_size: int = 500) -> None:
        """
         マルチプロセスで実行する処理。渡されたデータをもとにElasticsearchにデータ投入する。
        """

        # プロセスごとにコネクションが必要
        # https://github.com/elastic/elasticsearch-py/issues/638
        # TODO: 接続先定義が複数個所に分かれてしまっている。接続先はクラス変数を辞める？
        es = Elasticsearch(hosts="localhost:9200", http_auth=("elastic", "P@ssw0rd12345"), timeout=50000,)

        inserted_count: int = 0
        actions: list = []

        for data in data_list:
            actions.append({"_index": index_to_import, "_source": data})

            if len(actions) >= chunk_size:
                helpers.bulk(es, actions)
                inserted_count += len(actions)
                actions = []

        # 残っているデータを登録
        if len(actions) > 0:
            helpers.bulk(es, actions)
            inserted_count += len(actions)

    @classmethod
    def single_process_range_scan(cls, index: str, start: int, end: int) -> Iterable:

        body = {"query": {"range": {"sequential_number": {"gte": start, "lte": end - 1}}}}

        data_gen: Iterable = helpers.scan(client=cls.es, index=index, query=body)
        data = [x["_source"] for x in data_gen]
        data.sort(key=lambda x: x["sequential_number"])

        return data

    @classmethod
    def count(cls, index: str) -> int:
        result = cls.es.count(index=index)
        return result["count"]

    @classmethod
    def multi_process_range_scan(
        cls, index: list, num_of_data: int, start: int, end: int, num_of_process: int = 4,
    ) -> list:
        """ マルチプロセスでrange scanする。 """

        dt_now = datetime.now()
        print(f"{dt_now} data read start. data_count:{num_of_data}, process_count:{num_of_process}")

        batch_size, mod = divmod(num_of_data, num_of_process)

        # マルチプロセスの結果格納用
        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        procs: list = []
        for i in range(num_of_process):
            start_index: int = i * batch_size + start
            end_index: int = start_index + batch_size
            # 最後のプロセスには余り分を含めたデータを処理させる
            if (i == num_of_process - 1) and (mod != 0):
                end_index = end + 1

            proc = multiprocessing.Process(
                target=cls.range_scan, args=(index, i, start_index, end_index, return_dict),
            )
            proc.start()
            procs.append(proc)

        for proc in procs:
            proc.join()

        # マルチプロセスの結果をマージする
        result = []
        for proc in range(num_of_process):
            for data in return_dict[proc]:
                result.append(data)

        dt_now = datetime.now()
        print(f"{dt_now} Got {len(result)} documents.")

        return result

    @classmethod
    def range_scan(cls, index: str, proc_num: int, start: int, end: int, return_dict: list) -> Iterator:
        """ データをレンジスキャンした結果を返す
         Pythonのrange関数に合わせ、endはひとつ前までを返す仕様とする。
        """

        # プロセスごとにコネクションが必要
        # https://github.com/elastic/elasticsearch-py/issues/638
        es = Elasticsearch(hosts="localhost:9200", http_auth=("elastic", "P@ssw0rd12345"), timeout=50000,)

        body = {
            "query": {"range": {"sequential_number": {"gte": start, "lte": end - 1}}},
            # "sort": {
            #     "sequential_number": "asc"
            # }
        }

        data_gen: Iterable = helpers.scan(client=es, index=index, query=body)
        data = [x["_source"] for x in data_gen]
        data.sort(key=lambda x: x["sequential_number"])

        # 読み込んだデータの順番がsequential_number通りになっていることの確認
        # TODO: DEBUG_MODEのときだけ実行
        # data_sequential_numbers = [x['sequential_number'] for x in data]
        # expected = [x['sequential_number'] for x in sorted(data, key=lambda x: x['sequential_number'])]
        # if data_sequential_numbers != expected:
        #     file_name1 = "out_result_" + str(proc_num) + ".txt"
        #     file_name2 = "out_expected_" + str(proc_num) + ".txt"
        #     with open(file_name1, "w") as f:
        #         for x in data_sequential_numbers:
        #             f.write(str(x) + '\n')
        #     with open(file_name2, "w") as f:
        #         for x in expected:
        #             f.write(str(x) + '\n')

        return_dict[proc_num] = data


if __name__ == "__main__":
    pass

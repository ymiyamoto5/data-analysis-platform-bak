""" Elasticsearchへの各種処理を行うwrapperモジュール """

import os
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import pandas as pd
import json
from typing import Iterable, Iterator
import multiprocessing
from datetime import datetime, timezone, timedelta
import logging

# logger = logging.getLogger(__name__)
# handler = logging.FileHandler("log/elastic_manager.log")
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)

# datetime取得時に日本時間を指定する
JST = timezone(timedelta(hours=+9), 'JST')


class ElasticManager:
    """ Elasticsearchへの各種処理を行うwrapperクラス """

    es = Elasticsearch(hosts="localhost:9200", http_auth=('elastic', 'P@ssw0rd12345'), timeout=50000)

    @classmethod
    def show_indices(cls, show_all_index: bool = False) -> pd.DataFrame:
        """
         インデックス一覧のDataFrameを返す。

        Args:
            show_all_index: Trueの場合、すべてのインデックスを表示する。
                            デフォルトはFalseで、本プロジェクトに関係するインデックスのみ表示する。
        """

        if show_all_index:
            indices = cls.es.cat.indices(
                index='*', v=True, h=['index', 'docs.count', 'store.size'], bytes='kb').splitlines()
        else:
            indices = cls.es.cat.indices(
                index=['rawdata-*', 'shots-*', 'meta-*'], v=True, h=['index', 'docs.count', 'store.size'], bytes='kb'
            ).splitlines()

        indices_list = [x.split() for x in indices]

        df = pd.DataFrame(indices_list[1:], columns=indices_list[0])

        return df

    @classmethod
    def delete_index(cls, index: str) -> None:
        """ インデックスを削除する """

        is_valid_index, message = ElasticManager.__check_index(index)

        if not is_valid_index:
            print(message)
            return

        result = cls.es.indices.delete(index=index)

        if result['acknowledged']:
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

        body = {
            "query": {
                "range": {
                    "sequential_number": {
                        "gte": start,
                        "lte": end
                    }
                }
            }
        }

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

        query = {
            "term": {
                "shot_number": shot_number
            }
        }

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

        if index == '':
            message = "エラー：インデックスを指定してください。"
            return False, message

        if not cls.es.indices.exists(index=index):
            message = f"エラー：{index}が存在しません。"
            return False, message

        return True, ""

    @classmethod
    def delete_exists_index(cls, index: str) -> None:
        """ 既存のインデックスを削除する """

        if cls.es.indices.exists(index=index):
            result = cls.es.indices.delete(index=index)
            print(result)

    @classmethod
    def create_index(cls, index: str, mapping_file: str = None, setting_file: str = None) -> None:
        """ インデックスを作成する。documentは1度に30,000件まで読める設定とする。 """

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

        result = cls.es.indices.create(index=index, body=body)
        print(result)

    @classmethod
    def parallel_bulk(
        cls, doc_generator: Iterable, thread_count: int = 4, chunk_size: int = 500) -> None:
        """ 指定したスレッド数でbulk insertする。 """

        for success, info in helpers.parallel_bulk(
            cls.es, doc_generator, chunk_size=chunk_size, thread_count=thread_count):
            if not success:
                print('A document failed:', info)

    @classmethod
    def multi_process_bulk(
        cls, data: list, index_to_import: str, num_of_process=4, chunk_size: int = 500) -> None:
        """ マルチプロセスでbulk insertする。 """

        dt_now = datetime.now(JST)
        num_of_data = len(data)
        print(f"{dt_now} data import start. data_count:{num_of_data}, process_count:{num_of_process}")

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

    @classmethod
    def bulk_insert(cls, data_list: list, index_to_import: str, chunk_size: int = 500) -> None:
        """
         マルチプロセスで実行する処理。渡されたデータをもとにElasticsearchにデータ投入する。
        """

        # プロセスごとにコネクションが必要
        # https://github.com/elastic/elasticsearch-py/issues/638
        # TODO: 接続先定義が複数個所に分かれてしまっている。接続先はクラス変数を辞める？
        es = Elasticsearch(hosts="localhost:9200", http_auth=('elastic', 'P@ssw0rd12345'), timeout=50000)

        inserted_count: int = 0
        dt_now = datetime.now(JST)

        actions: list = []

        for data in data_list:
            actions.append({'_index': index_to_import, '_source': data})

            if len(actions) >= chunk_size:
                helpers.bulk(es, actions)
                inserted_count += len(actions)
                # TODO: 標準出力がプロセス間で取り合いになるせいか、改行がされない場合がある。
                throughput_counter(inserted_count, dt_now)
                actions = []

        # 残っているデータを登録
        if len(actions) > 0:
            helpers.bulk(es, actions)
            inserted_count += len(actions)

        print(f"pid:{os.getpid()}, inserted {inserted_count} docs")

    @classmethod
    def scan(cls, index: str) -> Iterable:
        """ データを全件取得し、連番の昇順ソート結果を返すジェネレータを生成する """

        query = {
            "sort": {
                "sequential_number": {
                    "order": "asc"
                }
            }
        }

        raw_data_gen: Iterable = helpers.scan(client=cls.es, index=index, query=query, preserve_order=True)

        return raw_data_gen

    @classmethod
    def scan2(cls, index: str) -> Iterable:
        """ データを全件取得し、連番の昇順ソート結果を返すジェネレータを生成する """

        query = {
            "match_all": {}
        }

        raw_data_gen: Iterable = helpers.scan(client=cls.es, index=index, query=query)

        return raw_data_gen

    @classmethod
    def count(cls, index: str) -> int:
        result = cls.es.count(index=index)
        return result['count']

    @classmethod
    def range_scan(cls, index: str, start: int, end: int) -> list:
        """ データをレンジスキャンした結果を返す
         Pythonのrange関数に合わせ、endはひとつ前までを返す仕様とする。
        """

        body = {
            "query": {
                "range": {
                    "sequential_number": {
                        "gte": start,
                        "lte": end - 1
                    }
                }
            }
        }

        # print(f'read start...{datetime.now(JST)}')
        data_gen: Iterable = helpers.scan(client=cls.es, index=index, query=body)
        data = [x['_source'] for x in data_gen]
        data.sort(key=lambda x: x['sequential_number'])
        # print(f'{len(data)} documents read...{datetime.now(JST)}')

        return data

    @classmethod
    def multi_process_range_scan(cls, index: list, num_of_data: int, start: int, end: int, num_of_process: int = 4) -> list:
        """ マルチプロセスでbulk insertする。 """

        dt_now = datetime.now(JST)
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

            proc = multiprocessing.Process(target=cls.range_scan_2,
                                           args=(index, i, start_index, end_index, return_dict))
            proc.start()
            procs.append(proc)

        for proc in procs:
            proc.join()

        result = []
        for i in range(num_of_process):
            for j in return_dict[i]:
                result.append(j)

        dt_now = datetime.now(JST)
        print(f"{dt_now} Got {len(result)} documents.")

        return result

    @classmethod
    def range_scan_2(cls, index: str, proc_num: int, start: int, end: int, return_dict: list) -> None:
        """ データをレンジスキャンした結果を返す
         Pythonのrange関数に合わせ、endはひとつ前までを返す仕様とする。
        """

        es = Elasticsearch(hosts="localhost:9200", http_auth=('elastic', 'P@ssw0rd12345'), timeout=50000)

        body = {
            "query": {
                "range": {
                    "sequential_number": {
                        "gte": start,
                        "lte": end - 1
                    }
                }
            }
        }
        # body = {
        #     "query": {
        #         "bool": {
        #             "must": {"match_all": {}},
        #             "filter": {
        #                 "range": {
        #                     "sequential_number": {
        #                         "gte": start,
        #                         "lte": end - 1
        #                     }
        #                 }
        #             }
        #         }
        #     }
        # }

        data_gen: Iterable = helpers.scan(client=es, index=index, query=body)
        data = [x['_source'] for x in data_gen]
        data.sort(key=lambda x: x['sequential_number'])

        # es_res = es.search(index=index, body=body)
        # hits = es_res['hits']['hits']
        # data = [x['_source'] for x in hits]
        # data.sort(key=lambda x: x['sequential_number'])

        return_dict[proc_num] = data


def throughput_counter(processed_count: int, dt_old: datetime) -> None:
    """ スループットの表示
     TODO: 外部モジュール化検討
    """

    dt_now = datetime.now(JST)
    dt_delta = dt_now - dt_old
    total_sec = dt_delta.total_seconds()
    throughput = processed_count / total_sec

    print(f"{dt_now}, processed_count: {processed_count}, throughput: {throughput}")


if __name__ == '__main__':
    pass

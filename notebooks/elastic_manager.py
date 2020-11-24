""" Elasticsearchへの各種処理を行うwrapperモジュール """

from elasticsearch import Elasticsearch
from elasticsearch import helpers
import pandas as pd
import json
from typing import Iterable


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
    def create_index(cls, index: str, mapping_file: str = None) -> None:
        """ インデックスを作成する。documentは1度に30,000件まで読める設定とする。 """

        body = {"settings": {"index": {"max_result_window": 30000}}}

        if mapping_file:
            with open(mapping_file) as f:
                d = json.load(f)
                body["mappings"] = d

        result = cls.es.indices.create(index=index, body=body)
        print(result)

    @classmethod
    def parallel_bulk(
        cls, doc_generator: Iterable, data_to_import: str, index_to_import: str,
        thread_count: int = 4, chunk_size: int = 500) -> None:
        """
         並列処理でbulk insertする。
         TODO: data_to_importはいらなくなる
        """

        for success, info in helpers.parallel_bulk(
            cls.es, doc_generator, chunk_size=chunk_size, thread_count=thread_count):
            if not success:
                print('A document failed:', info)

    @classmethod
    def scan(cls, index: str) -> Iterable:
        """ 生データを全件取得し、連番の昇順ソート結果を返すジェネレータを生成する """

        query = {
            "sort": {
                "sequential_number": {
                    "order": "asc"
                }
            }
        }

        raw_data_gen: Iterable = helpers.scan(client=cls.es, index=index, query=query, preserve_order=True)
        # raw_data: list = [x['_source'] for x in raw_data_gen]
        # print(f"取得データ数：{len(raw_data)}")

        return raw_data_gen


if __name__ == '__main__':
    pass

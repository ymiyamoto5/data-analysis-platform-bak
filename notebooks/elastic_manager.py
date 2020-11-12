from elasticsearch import Elasticsearch
import pandas as pd


class ElasticManager:
    es = Elasticsearch(hosts="localhost:9200", http_auth=('elastic', 'P@ssw0rd12345'), timeout=50000)

    @classmethod
    def show_indices(cls, show_all_index: bool = False) -> pd.DataFrame:
        '''
         インデックス一覧を表示する。
            Args:
                show_all_index: Trueの場合、すべてのインデックスを表示する。デフォルトはFalseで、本プロジェクトに関係するインデックスのみ表示する。
        '''

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
    def __check_index(cls, index):
        if index == '':
            message = "エラー：インデックスを指定してください。"
            return False, message

        if not cls.es.indices.exists(index=index):
            message = f"エラー：{index}が存在しません。"
            return False, message

        return True, ""

if __name__ == '__main__':
    pass
    # ElasticManager.show_indices()
    # ElasticManager.delete_index('rawdata-20201112-*')
    ElasticManager.delete_data_by_seq_num('rawdata-20201112-1', 0, 10)

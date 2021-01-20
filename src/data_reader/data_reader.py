from typing import Final, List
from datetime import datetime
from pandas.core.frame import DataFrame
import os
import sys
import logging
import logging.handlers
import pandas as pd


sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
from time_logger import time_log
import common


class DataReader:
    def read_shot(self, index: str, shot_number: int) -> DataFrame:
        """ 特定ショットのデータを取得し、連番の昇順にソートして返却する """

        query: dict = {"query": {"term": {"shot_number": {"value": shot_number}}}}

        result: List[dict] = ElasticManager.get_docs(index=index, query=query)
        result.sort(key=lambda x: x["sequential_number"])

        df: DataFrame = pd.DataFrame(result)
        return df

    @time_log
    def read_all(self, index: str) -> DataFrame:
        """ 全件取得し、連番の昇順ソート結果を返す """

        print("データを全件取得します。データ件数が多い場合、長時間かかる場合があります。")

        num_of_data: int = ElasticManager.count(index=index)

        result: List[dict] = ElasticManager.multi_process_range_scan(index=index, num_of_data=num_of_data)
        result.sort(key=lambda x: x["sequential_number"])

        df: DataFrame = pd.DataFrame(result)
        return df

    def read_shots_meta(self, index: str) -> DataFrame:
        """ メタデータを取得する """

        query: dict = {"sort": {"shot_number": {"order": "asc"}}}
        result: List[dict] = ElasticManager.get_docs(index=index, query=query)

        df: DataFrame = pd.DataFrame(result)
        return df


def main():
    data_reader = DataReader()
    data_reader.read_all("shots-20201201010000")


if __name__ == "__main__":
    main()


from typing import Final
from datetime import datetime
from pandas.core.frame import DataFrame
import os
import sys
import logging
import logging.handlers
import pandas as pd

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elastic_manager import ElasticManager
from time_logger import time_log
from throughput_counter import throughput_counter


sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import common

ELASTIC_URL: Final[str] = common.get_config_value(common.APP_CONFIG_PATH, "elastic_url")
ELASTIC_USER: Final[str] = common.get_config_value(common.APP_CONFIG_PATH, "elastic_user")
ELASTIC_PASSWORD: Final[str] = common.get_config_value(common.APP_CONFIG_PATH, "elastic_password")


class DataReader:
    def __init__(self):
        self.es = Elasticsearch(hosts=ELASTIC_URL, http_auth=(ELASTIC_USER, ELASTIC_PASSWORD), timeout=50000)

    def read(self, src_index: str, shot_number: int = 1) -> list:
        """ 特定ショットのデータを取得し、連番の昇順にソートして返却する """
        query = {"query": {"term": {"shot_number": {"value": shot_number}}}}

        result = helpers.scan(client=self.es, index=src_index, query=query)
        shot_data = [x["_source"] for x in result]
        shot_data.sort(key=lambda x: x["sequential_number"])

        print(f"取得データ数：{len(shot_data)}")

        return shot_data

    def read_raw_data(self, src_index: str) -> list:
        """ 生データを全件取得し、連番の昇順ソート結果を返すジェネレータを生成する """
        query = {}

        result = helpers.scan(client=self.es, index=src_index, query=query)
        raw_data = [x["_source"] for x in result]
        raw_data.sort(key=lambda x: x["sequential_number"])

        print(f"取得データ数：{len(raw_data)}")

        return raw_data

    @time_log
    def read_shots_data(self, src_index: str, num_of_process: int = 8) -> list:

        num_of_data: int = ElasticManager.count(src_index)

        shots_data = ElasticManager.multi_process_range_scan(src_index, num_of_data, 0, num_of_data, num_of_process)

        print(f"取得データ数: {len(shots_data)}")


def main():
    data_reader = DataReader()
    # data_reader.read("shots", 1)
    # data_reader.read_raw_data("raw_data")
    data_reader.read_shots_data("shots-no13-3000")


if __name__ == "__main__":
    main()

# #scroll版(scanがscrollのwrapperになっているので、特に使わなくてよいと思われる。)
# snapshot_time = "1m"
# export_result = self.es.search(
#     index=src_index, body=body, size=10000, scroll=snapshot_time)

# scroll_id = export_result['_scroll_id']
# scroll_size = len(export_result['hits']['total'])

# # 配列内のキー'_source'に実データがあるため、そこだけ抽出
# tmp_result = export_result['hits']['hits']
# shot_data = [x['_source'] for x in tmp_result]

# while scroll_size > 0:
#     scroll_result = self.es.scroll(
#         scroll_id=scroll_id, scroll=snapshot_time)
#     scroll_id = scroll_result['_scroll_id']
#     scroll_size = len(scroll_result['hits']['hits'])

#     tmp_result = scroll_result['hits']['hits']
#     scrolled_data = [x['_source'] for x in tmp_result]
#     shot_data.extend(scrolled_data)

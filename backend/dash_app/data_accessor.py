"""
 ==================================
  data_accessor.py
 ==================================

  Copyright(c) 2022 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

from pathlib import Path

import pandas as pd
from backend.elastic_manager.elastic_manager import ElasticManager


class ElasticDataAccessor:
    """DashアプリからElasticsearchにアクセスするwrapper
    NOTE: CSVとは扱いが異なるため、CsvDataAccessorとは共通化しない。
    """

    @staticmethod
    def get_shot_df(index, shot_number, size=10_000):
        """elasticsearch indexからショットデータを取得し、DataFrameとして返す"""

        query: dict = {"query": {"term": {"shot_number": {"value": shot_number}}}, "sort": {"sequential_number": {"order": "asc"}}}

        result = ElasticManager.get_docs(index=index, query=query, size=size)
        shot_df = pd.DataFrame(result)
        return shot_df

    @staticmethod
    def get_shot_list(index):
        query: dict = {
            "collapse": {"field": "shot_number"},
            "query": {"match_all": {}},
            "_source": ["shot_number"],
            "sort": {"shot_number": {"order": "asc"}},
        }

        docs = ElasticManager.get_docs(index=index, query=query, size=10_000)
        shot_numbers = [d["shot_number"] for d in docs]
        return shot_numbers

    @staticmethod
    def get_indices():
        return ElasticManager.show_indices(index="shots-*-data")["index"]

    @staticmethod
    def insert(data_list, index_name: str):
        """data_listをElasticsearchに保存する。既存のindexは削除する。"""

        if ElasticManager.exists_index(index=index_name):
            ElasticManager.delete_index(index=index_name)
        ElasticManager.create_index(index=index_name)

        ElasticManager.bulk_insert(data_list, index_name)


class CsvDataAccessor:
    def __init__(self, dir: str):
        p = Path(dir)
        self.__flist = list(sorted(p.glob("*.CSV")))

    def get_shot_df(self, csv_file: str):
        df = pd.read_csv(csv_file)
        return df

    def get_flist(self):
        return self.__flist


class AidaCsvDataAccessor(CsvDataAccessor):
    def get_shot_df(self, csv_file: str):
        df = pd.read_csv(
            csv_file,
            encoding="cp932",
            skiprows=[0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],
        ).rename({"CH名称": "time"}, axis=1)
        try:
            df["プレス荷重shift"] = df["プレス荷重"].shift(-640)
            df["dF/dt"] = df["プレス荷重shift"].diff()
            df["F*dF/dt"] = df["プレス荷重shift"] * df["dF/dt"]
            if "加速度左右_X_左+" in df.columns:
                df = df.rename({"加速度左右_X_左+": "加速度左右_X_左+500G"}, axis=1)
            if "加速度上下_Y_下+" in df.columns:
                df = df.rename({"加速度上下_Y_下+": "加速度上下_Y_下+500G"}, axis=1)
            if "加速度前後_Z_前+" in df.columns:
                df = df.rename({"加速度前後_Z_前+": "加速度前後_Z_前+500G"}, axis=1)
        except KeyError:
            print("プレス荷重　無し")
            return

        return df

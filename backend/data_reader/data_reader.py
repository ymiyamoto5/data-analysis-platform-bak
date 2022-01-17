"""
 ==================================
  data_reader.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import glob
from typing import List, Optional

import pandas as pd
from backend.common import common
from backend.common.common_logger import logger
from backend.elastic_manager.elastic_manager import ElasticManager
from pandas.core.frame import DataFrame


class DataReader:
    def read_shot(self, index: str, shot_number: int) -> DataFrame:
        """特定ショットのデータを取得し、連番の昇順にソートして返却する"""

        query: dict = {"query": {"term": {"shot_number": {"value": shot_number}}}}

        result: List[dict] = ElasticManager.scan_docs(index=index, query=query)

        if len(result) == 0:
            logger.error("No data.")
            return

        result.sort(key=lambda x: x["sequential_number"])  # type: ignore

        df: DataFrame = pd.DataFrame(result)
        return df

    def read_shots(self, index: str, start_shot_number: int, end_shot_number: int) -> DataFrame:
        """複数ショット分のデータを取得し、連番の昇順にソートして返却する。
        Pythonのrange関数に合わせ、endはひとつ前までを返す仕様とする。
        """

        query: dict = {"query": {"range": {"shot_number": {"gte": start_shot_number, "lte": end_shot_number - 1}}}}

        result: List[dict] = ElasticManager.scan_docs(index=index, query=query)

        if len(result) == 0:
            logger.error("No data.")
            return

        result.sort(key=lambda x: x["sequential_number"])  # type: ignore

        df: DataFrame = pd.DataFrame(result)
        return df

    def multi_process_read_all(self, index: str) -> DataFrame:
        """マルチプロセスで全件取得し、連番の昇順ソート結果を返す。
        本関数が利用可能なインデックスは連番(sequential_number)フィールドを持つインデックスだけであることに注意。
        """

        logger.info("データを全件取得します。データ件数が多い場合、長時間かかる場合があります。")

        num_of_data: int = ElasticManager.count(index=index)

        # 100万件毎のバッチに分割
        # ex) 2_500_000 -> [1_000_000, 1_000_000, 500_000]
        batch_size: int = 1_000_000
        remain_num_of_data = num_of_data
        num_of_data_by_batch: List[int] = []
        while True:
            if remain_num_of_data >= batch_size:
                num_of_data_by_batch.append(batch_size)
            else:
                num_of_data_by_batch.append(remain_num_of_data)
                break
            remain_num_of_data -= batch_size

        results: DataFrame = pd.DataFrame([])
        start_index: int = 0
        for num_of_data in num_of_data_by_batch:
            result: List[dict] = ElasticManager.multi_process_range_scan(
                index=index,
                start_index=start_index,
                num_of_data=num_of_data,
                num_of_process=common.NUM_OF_PROCESS,
            )

            result.sort(key=lambda x: x["sequential_number"])  # type: ignore
            df: DataFrame = pd.DataFrame(result)
            results = pd.concat([results, df], axis=0, ignore_index=True)

            start_index += num_of_data

        if len(results) == 0:
            logger.error("No data.")
            return

        return results

    def read_all(self, index: str) -> DataFrame:
        """シングルプロセスで全件取得し、連番の昇順ソート結果を返す"""

        logger.info("データを全件取得します。データ件数が多い場合、長時間かかる場合があります。")

        num_of_data: int = ElasticManager.count(index=index)

        logger.info(f"データ件数: {num_of_data}")

        result: List[dict] = ElasticManager.scan_docs(index=index, query={})

        if len(result) == 0:
            logger.error("No data.")
            return

        result.sort(key=lambda x: x["sequential_number"])  # type: ignore

        logger.info("Data reading has finished.")

        df: DataFrame = pd.DataFrame(result)
        return df

    def read_shots_meta(self, index: str) -> DataFrame:
        """メタデータを取得する"""

        query: dict = {"sort": {"shot_number": {"order": "asc"}}}
        result: List[dict] = ElasticManager.get_docs(index=index, query=query)

        if len(result) == 0:
            logger.error("No data.")
            return

        df: DataFrame = pd.DataFrame(result)
        return df

    def read_csv_files(
        self, path: str, header: Optional[int] = None, names: Optional[List[str]] = None, encoding: str = "utf-8"
    ) -> DataFrame:
        """指定ディレクトリの全csvファイルをDataFrameにて取得"""
        files = sorted(glob.glob(path + "/*.csv"))
        df: DataFrame = pd.DataFrame()
        df_lists = []

        for f in files:
            # 列数とnamesの要素数が一致しない場合はエラーとする
            if names is not None:
                csv_columns = len(pd.read_csv(f, header=header, names=None, encoding=encoding).columns)
                if csv_columns != len(names):
                    logger.error("Length of names list is not equal columns.")
                    return

            csv_df = pd.read_csv(f, header=header, names=names, encoding=encoding)

            # 異なる列数の行が存在し、DataFrameに欠損値(NaN)が入った場合はエラーとする
            if csv_df.isnull().values.sum() != 0:
                logger.error("NaN exists in DataFrame.")
                return

            df_lists.append(csv_df)
        df = pd.concat(df_lists, axis=0, ignore_index=True)
        return df


if __name__ == "__main__":
    data_reader = DataReader()
    machine_id = "machine-01"
    target_date = "20210327141514"
    target = "shots-" + machine_id + "-" + target_date + "-data"
    df = data_reader.multi_process_read_all(target)
    # logger.info(df.info())

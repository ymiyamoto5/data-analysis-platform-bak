"""
 ==================================
  data_reader.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import glob
import re
from typing import List, Optional

import pandas as pd
from backend.common import common
from backend.common.common_logger import logger
from backend.elastic_manager.elastic_manager import ElasticManager
from backend.file_manager.file_manager import FileInfo, FileManager
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
            df_lists.append(csv_df)

        df = pd.concat(df_lists, axis=0, ignore_index=True)
        return df

    def read_loadstroke_files(self, path: str, file_info: FileInfo):
        """指定ディレクトリの全loadstroke-*.csvファイルを読み込み・加工する"""

        df: DataFrame = pd.read_csv(file_info.file_path, header=None, names=None, encoding="shift-jis")

        # csvのheader情報を取得
        begin_header: int = int(df[df[0] == "#BeginHeader"].reset_index().loc[0, 1]) - 1
        data_num: int = int(df[df[0] == "データ数"].reset_index().loc[0, 1]) - 1

        # 取込範囲のDataFrameを取得
        loadstroke_df: DataFrame = pd.read_csv(
            file_info.file_path, header=0, names=None, encoding="shift-jis", skiprows=begin_header, nrows=data_num
        ).dropna(how="all", axis=1)

        # TODO: 必要な加工を施す（時刻処理や物理変換等が必要な想定。後ほど仕様検討）

        # pickleファイルに出力
        data_list: List[dict] = loadstroke_df.to_dict(orient="records")
        FileManager.export_to_pickle(data_list, file_info, path)

        # Elasticsearchに出力
        index_name = re.split(r"/|\.", file_info.file_path)[-2]
        ElasticManager.df_to_els(df=loadstroke_df, index=index_name)


if __name__ == "__main__":
    data_reader = DataReader()
    machine_id = "machine-01"
    target_date = "20210327141514"
    target = "shots-" + machine_id + "-" + target_date + "-data"
    df = data_reader.multi_process_read_all(target)
    # logger.info(df.info())

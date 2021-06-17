"""
 ==================================
  data_importer.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

from typing import Final, List, Tuple, Optional
from pandas.core.frame import DataFrame
import os
import sys
import logging
import logging.handlers
import pandas as pd
import glob
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import common


class DataImporter:
    """ 指定ディレクトリの全csvファイルを加工し、pklファイルとして出力するモジュール """

    def __init__(self, dir, start_time):
        self.dir = dir
        self.start_time = start_time

    def process(self, exists_timestamp: bool, use_cols, cols_name) -> None:
        """ """

        files: List[str] = glob.glob(os.path.join(self.dir, "*.csv"))

        if len(files) == 0:
            print("File not found.")
            sys.exit(1)

        files.sort()

        seq_num = 0  # ファイル跨ぎの連番
        for file in files:
            # FIXME: ヘッダーありの場合等の考慮
            df = pd.read_csv(file, header=None, skiprows=1, usecols=use_cols)
            # 列名変換
            # df = self.rename(df, use_cols, cols_name)
            df = df.set_axis(cols_name, axis="columns")

            # timestampと連番付与
            if not exists_timestamp:
                df, seq_num = self.add_timestamp(df, seq_num)

            # 並べ替え
            cols = ["sequential_number", "timestamp"] + cols_name
            df = df.reindex(columns=cols)

            self.to_pickle(df, file)

    def add_timestamp(self, df: DataFrame, seq_num):
        """ timestamp列追加
            FIXME: ついでに連番も付けているが、本来は別メソッドにすべき。
        """

        seq_nums = []
        datetime_list = []
        for _ in df.itertuples():
            time = self.start_time + timedelta(microseconds=10) * seq_num
            datetime_list.append(time.timestamp() - 9 * 60 * 60)
            seq_nums.append(seq_num)
            seq_num += 1

        df["sequential_number"] = seq_nums
        df["timestamp"] = datetime_list

        return df, seq_num

    def to_pickle(self, df: DataFrame, file: str):
        pickle_filename: str = os.path.splitext(os.path.basename(file))[0]
        pickle_filepath: str = os.path.join(self.dir, pickle_filename) + ".pkl"
        df.to_pickle(pickle_filepath)


if __name__ == "__main__":
    dir = "/home/ymiyamoto5/h-one-experimental-system/shared/data/20210617130000"
    start_time = datetime(2021, 6, 17, 13, 0, 0)
    # 何列目を使うか。
    use_cols: List[int] = [0, 6, 7, 8, 9]
    cols_name: List[str] = ["displacement", "load01", "load02", "load03", "load04"]
    di = DataImporter(dir, start_time)
    di.process(exists_timestamp=False, use_cols=use_cols, cols_name=cols_name)

"""
 ==================================
  data_importer.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

from typing import List
from pandas.core.frame import DataFrame
import os
import sys
import numpy as np
import pandas as pd
import glob
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import common


class DataImporter:
    """ DataFrameで提供されるデータをElasticsearchに格納するためのクラス """

    def __init__(self):
        pass

    # TODO: 共通化
    def _get_files(self, file_dir, pattern: str):
        """ pattern に一致するファイルをdirから取得する """

        files: List[str] = glob.glob(os.path.join(file_dir, pattern))

        if len(files) == 0:
            print("File not found.")
            sys.exit(1)

        files.sort()

        return files

    def split_np_array_by_shot(self, target_file_path: str, target_date: str):
        """ numpy arrayのデータファイルをloadし、ショット毎に1csvファイルとして分割する。
            numpy arrayは3次元データとし、0次元がショット軸であることが前提である。
        """

        arr = np.load(target_file_path)
        print(f"shape：{arr.shape}")

        file_dir = self._get_target_date_dir(target_date)

        for i in range(arr.shape[0]):
            str_i = str(i).zfill(4)
            df = pd.DataFrame(arr[i])
            df.to_csv(os.path.join(file_dir, str_i) + ".csv", header=False, index=False)

        print("output csv finished.")

    def _get_target_date_dir(self, target_date: str) -> str:
        """ ファイル出力先のパスを取得する """

        data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")
        file_dir: str = os.path.join(data_dir, target_date)

        return file_dir

    def process_csv_files(
        self, target_date: str, exists_timestamp: bool, start_time: datetime, use_cols, cols_name, sampling_interval
    ) -> DataFrame:
        """ csvファイルのデータを加工する """

        file_dir = self._get_target_date_dir(target_date)
        files = self._get_files(file_dir, pattern="*.csv")

        seq_num = 0  # ファイル跨ぎの連番
        for file in files:
            # FIXME: ヘッダーありの場合等の考慮
            df = pd.read_csv(file, header=None, skiprows=0, usecols=use_cols)
            df = df.set_axis(cols_name, axis="columns")

            # timestampと連番付与
            if not exists_timestamp:
                df, start_time, seq_num = self._add_timestamp(df, start_time, seq_num, sampling_interval)

            # 並べ替え
            cols = ["sequential_number", "timestamp"] + cols_name
            df = df.reindex(columns=cols)

            self._to_pickle(df, file_dir, file)

    def _add_timestamp(self, df: DataFrame, start_time, seq_num, sampling_interval):
        """ timestamp列追加
            FIXME: ついでに連番も付けているが、本来は別メソッドにすべき。
        """

        seq_nums = []
        datetime_list = []
        for _ in df.itertuples():
            time = start_time + timedelta(microseconds=sampling_interval) * seq_num
            datetime_list.append(time.timestamp() - 9 * 60 * 60)
            seq_nums.append(seq_num)
            seq_num += 1

        df["sequential_number"] = seq_nums
        df["timestamp"] = datetime_list

        return df, start_time, seq_num

    def _to_pickle(self, df: DataFrame, file_dir: str, file: str):
        """ DataFrameをpickleに変換 """

        pickle_filename: str = os.path.splitext(os.path.basename(file))[0]
        pickle_filepath: str = os.path.join(file_dir, pickle_filename) + ".pkl"
        df.to_pickle(pickle_filepath)

    def import_by_shot_pkl(self, target_date: str):
        """ ショット毎に分割されたpickleファイルからElasticsearchにインポートする """

        # TODO: メソッド化
        shots_index: str = "shots-" + target_date + "-data"
        ElasticManager.delete_exists_index(index=shots_index)
        mapping_shots: str = common.get_config_value(common.APP_CONFIG_PATH, "mapping_shots_path")
        setting_shots: str = common.get_config_value(common.APP_CONFIG_PATH, "setting_shots_path")
        ElasticManager.create_index(index=shots_index, mapping_file=mapping_shots, setting_file=setting_shots)

        # TODO: メソッド化
        shots_meta_index: str = "shots-" + target_date + "-meta"
        ElasticManager.delete_exists_index(index=shots_meta_index)
        mapping_shots_meta: str = common.get_config_value(common.APP_CONFIG_PATH, "mapping_shots_meta_path")
        setting_shots_meta: str = common.get_config_value(common.APP_CONFIG_PATH, "setting_shots_meta_path")
        ElasticManager.create_index(
            index=shots_meta_index, mapping_file=mapping_shots_meta, setting_file=setting_shots_meta
        )

        file_dir = self._get_target_date_dir(target_date)
        files = self._get_files(file_dir, "*.pkl")

        all_df = pd.DataFrame([])
        shots_meta_records = []
        shot_number = 1
        start = 0
        for file in files:
            df = pd.read_pickle(file)
            df["shot_number"] = shot_number
            df["sequential_number_by_shot"] = pd.RangeIndex(0, len(df), 1)
            df["rawdata_sequential_number"] = pd.RangeIndex(start, start + len(df), 1)
            df["tags"] = pd.Series([[] for _ in range(len(df))])  # tagsは[]で初期化
            all_df = pd.concat([all_df, df], axis=0, ignore_index=True)

            timestamp = df.timestamp.iloc[0]
            shots_meta_records.append(
                {
                    "timestamp": datetime.fromtimestamp(timestamp),
                    "shot_number": shot_number,
                    "num_of_samples_in_cut_out": len(df),
                }
            )

            shot_number += 1
            start += len(df)

        all_df["timestamp"] = all_df["timestamp"].apply(lambda x: datetime.fromtimestamp(x))
        shots_dict = all_df.to_dict(orient="records")
        shots_index = "shots-" + target_date + "-data"

        print("shots_index bulk insert starting...")
        ElasticManager.bulk_insert(shots_dict, shots_index)
        print("shots_index bulk insert finished.")

        # TODO: メソッド化して、cut_out_shotと共有
        shots_meta_df = pd.DataFrame(shots_meta_records)
        # diffを取るため、一時的にtimestampに変更
        shots_meta_df["timestamp"] = shots_meta_df["timestamp"].apply(lambda x: x.timestamp())
        shots_meta_df["time_diff"] = shots_meta_df.timestamp.diff(-1)
        shots_meta_df["spm"] = round(60.0 / abs(shots_meta_df.time_diff), 2)
        # NOTE: Noneに置き換えないとそのレコードがElasticsearchに弾かれる。
        # shots_meta_df["spm"] = shots_meta_df["spm"].where(shots_meta_df["spm"].notna(), None)
        # NOTE: おそらくpandasのバージョン依存で、ver1.3.0では上のコードでは置き換えができない
        shots_meta_df.replace(dict(spm={np.nan: None}), inplace=True)
        shots_meta_df.drop(columns=["time_diff"], inplace=True)
        # NOTE: 一度datetimeからtimestampに変換し、再度datetimeに戻すとJSTになってしまうため、-9時間してUTCにする。
        shots_meta_df["timestamp"] = shots_meta_df["timestamp"].apply(
            lambda x: datetime.fromtimestamp(x - 9 * 60 * 60)
        )

        shots_meta_dict = shots_meta_df.to_dict(orient="records")
        shots_meta_index = "shots-" + target_date + "-meta"
        ElasticManager.bulk_insert(shots_meta_dict, shots_meta_index)
        print("shots_meta_index bulk insert finished.")


if __name__ == "__main__":
    # テスト用のインデックス
    target_date = "20210701180000"
    start_time = datetime(2021, 7, 1, 18, 0, 0)
    # target_date = "20210708113000"
    # start_time = datetime(2021, 7, 8, 11, 30, 0)
    # 何列目を使うか。
    use_cols = [2, 6, 7, 11, 57]
    cols_name: List[str] = ["load01", "load02", "load03", "load04", "displacement"]
    # sampling_interval = 10 # 100k
    sampling_interval = 1000  # 1k

    di = DataImporter()

    # npyをショット毎のcsvファイルに分割
    # di.split_np_array_by_shot(
    #     "/home/ymiyamoto5/h-one-experimental-system/shared/data/all_sensors_201905standardized.npy", target_date
    # )

    # csvを加工してpklにする
    # di.process_csv_files(
    #     target_date=target_date,
    #     exists_timestamp=False,
    #     start_time=start_time,
    #     use_cols=use_cols,
    #     cols_name=cols_name,
    #     sampling_interval=sampling_interval,
    # )

    # pklをelasticsearchに格納
    di.import_by_shot_pkl(target_date)

"""
 ==================================
  data_importer.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

# NOTE: 本来の仕様外の処理のため、ややアドホックな記述にしている。

from typing import List, Optional
from pandas.core.frame import DataFrame
import os
import sys
import numpy as np
import pandas as pd
import glob
from datetime import datetime, timedelta
from dateutil import tz

JST = tz.gettz("Asia/Tokyo")
UTC = tz.gettz("UTC")

from backend.elastic_manager.elastic_manager import ElasticManager
from backend.common import common
from backend.common.common_logger import logger


class DataImporter:
    """DataFrameで提供されるデータをElasticsearchに格納するためのクラス"""

    def __init__(self):
        pass

    # TODO: 共通化
    def _get_files(self, file_dir, pattern: str):
        """pattern に一致するファイルをdirから取得する"""

        files: List[str] = glob.glob(os.path.join(file_dir, pattern))

        if len(files) == 0:
            logger.info("File not found.")
            sys.exit(1)

        files.sort()

        return files

    def split_np_array_by_shot(self, target_file_path: str, target: str):
        """numpy arrayのデータファイルをloadし、ショット毎に1csvファイルとして分割する。
        numpy arrayは3次元データとし、0次元がショット軸であることが前提である。
        """

        arr = np.load(target_file_path)
        logger.info(f"shape：{arr.shape}")

        file_dir = self._get_target_date_dir(target)

        for i in range(arr.shape[0]):
            str_i = str(i).zfill(4)
            df = pd.DataFrame(arr[i])
            df.to_csv(os.path.join(file_dir, str_i) + ".csv", header=False, index=False)

        logger.info("output csv finished.")

    def _get_target_date_dir(self, target: str) -> str:
        """ファイル出力先のパスを取得する"""

        data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")
        file_dir: str = os.path.join(data_dir, target)

        return file_dir

    def process_csv_files(
        self,
        target: str,
        exists_timestamp: bool,
        start_time: Optional[datetime],
        use_cols,
        cols_name,
        sampling_interval,
        timestamp_file=None,
    ) -> DataFrame:
        """csvファイルのデータを加工する"""

        file_dir = self._get_target_date_dir(target)
        files = self._get_files(file_dir, pattern="*.csv")

        if start_time is not None:
            # UTCに変換
            start_time = start_time.astimezone(UTC)

        if timestamp_file is not None:
            timestamp_df = pd.read_csv(timestamp_file, header=None, names=("file_number", "timestamp"))
            # JSTで記録された文字列をUTC datetimeに変換
            timestamp_df["timestamp"] = timestamp_df["timestamp"].apply(
                lambda x: datetime.strptime(x, "%Y/%m/%d-%H%M%S").astimezone(UTC)
            )

        seq_num = 0  # ファイル跨ぎの連番
        for file in files:
            # FIXME: ヘッダーありの場合等の考慮
            df = pd.read_csv(file, header=None, skiprows=0, usecols=use_cols)
            # TODO: 変位を強制的に追加
            df["displacement"] = df.iloc[:, 0]

            df = df.set_axis(cols_name, axis="columns")

            # timestampがなければ付与
            if not exists_timestamp:
                df, start_time = self._add_timestamp(df, start_time, sampling_interval)
            # timestampがある場合。ここではショット毎のタイムスタンプを記録したcsvがある前提
            else:
                file_number = int(os.path.splitext(os.path.basename(file))[0])
                df = self._add_timestamp_from_file(df, file_number, timestamp_df, sampling_interval)

            # 連番付与
            df, seq_num = self._add_seq_num(df, seq_num)

            # 並べ替え
            cols = ["sequential_number", "timestamp"] + cols_name
            df = df.reindex(columns=cols)

            self._to_pickle(df, file_dir, file)

    def _add_timestamp_from_file(
        self, df: DataFrame, file_number: int, timestamp_df: DataFrame, sampling_interval: float
    ):
        """ショット毎のタイムスタンプが記録されたDFを使って、元のDFのサンプルデータにタイムスタンプを付与する"""

        start_time = timestamp_df[timestamp_df.file_number == file_number].timestamp.iloc[0]

        df, _ = self._add_timestamp(df, start_time, sampling_interval)

        return df

    def _add_timestamp(self, df: DataFrame, start_time, sampling_interval):
        """timestamp列追加
        NOTE: start_timeはタイムゾーンUTCのdatetimeを前提とする。
        """

        datetime_list = []
        for i in range(len(df)):
            time = start_time + timedelta(microseconds=sampling_interval) * i
            datetime_list.append(time.timestamp())

        df["timestamp"] = datetime_list

        time += timedelta(microseconds=sampling_interval)

        return df, time

    def _add_seq_num(self, df: DataFrame, seq_num):
        seq_nums = []

        for _ in range(len(df)):
            seq_nums.append(seq_num)
            seq_num += 1

        df["sequential_number"] = seq_nums

        return df, seq_num

    def _to_pickle(self, df: DataFrame, file_dir: str, file: str):
        """DataFrameをpickleに変換"""

        pickle_filename: str = os.path.splitext(os.path.basename(file))[0]
        pickle_filepath: str = os.path.join(file_dir, pickle_filename) + ".pkl"
        df.to_pickle(pickle_filepath)

    def import_by_shot_pkl(self, target: str):
        """ショット毎に分割されたpickleファイルからElasticsearchにインポートする"""

        # TODO: メソッド化
        shots_index: str = "shots-" + target + "-data"
        ElasticManager.delete_exists_index(index=shots_index)
        mapping_shots: str = common.get_config_value(common.APP_CONFIG_PATH, "mapping_shots_path")
        setting_shots: str = common.get_config_value(common.APP_CONFIG_PATH, "setting_shots_path")
        ElasticManager.create_index(index=shots_index, mapping_file=mapping_shots, setting_file=setting_shots)

        # TODO: メソッド化
        shots_meta_index: str = "shots-" + target + "-meta"
        ElasticManager.delete_exists_index(index=shots_meta_index)
        mapping_shots_meta: str = common.get_config_value(common.APP_CONFIG_PATH, "mapping_shots_meta_path")
        setting_shots_meta: str = common.get_config_value(common.APP_CONFIG_PATH, "setting_shots_meta_path")
        ElasticManager.create_index(
            index=shots_meta_index, mapping_file=mapping_shots_meta, setting_file=setting_shots_meta
        )

        file_dir = self._get_target_date_dir(target)
        files = self._get_files(file_dir, "*.pkl")

        shots_index = "shots-" + target + "-data"

        shots_meta_records = []
        shot_number = 1
        start = 0

        logger.info("shots_index bulk insert starting...")
        for file in files:
            logger.info(f"import {file} starting...")
            df = pd.read_pickle(file)
            df["shot_number"] = shot_number
            df["sequential_number_by_shot"] = pd.RangeIndex(0, len(df), 1)
            df["rawdata_sequential_number"] = pd.RangeIndex(start, start + len(df), 1)
            df["tags"] = pd.Series([[] for _ in range(len(df))])  # tagsは[]で初期化

            timestamp = df.timestamp.iloc[0]
            shots_meta_records.append(
                {
                    "timestamp": datetime.utcfromtimestamp(timestamp),
                    "shot_number": shot_number,
                    "num_of_samples_in_cut_out": len(df),
                }
            )

            df["timestamp"] = df["timestamp"].apply(lambda x: datetime.utcfromtimestamp(x))
            shots_dict = df.to_dict(orient="records")

            # NOTE: 並列化すると遅かったため、シングルプロセス
            ElasticManager.bulk_insert(shots_dict, shots_index)

            shot_number += 1
            start += len(df)

        logger.info("shots_index bulk insert finished.")

        # TODO: メソッド化して、cut_out_shotと共有
        shots_meta_df = pd.DataFrame(shots_meta_records)
        # NOTE: diffを取るため、一時的にtimestampに変更。
        # 　　　 timestamp()メソッドはデフォルトでローカル時間になってしまうため、timezoneを指定すること
        shots_meta_df["timestamp"] = shots_meta_df["timestamp"].apply(lambda x: x.replace(tzinfo=UTC).timestamp())
        shots_meta_df["time_diff"] = shots_meta_df.timestamp.diff(-1)
        shots_meta_df["spm"] = round(60.0 / abs(shots_meta_df.time_diff), 2)
        # NOTE: np.NaNをNoneに置き換えないとそのレコードがElasticsearchに弾かれる。
        #       pandasのバージョン依存により、ver1.3.0ではwhereでの置き換えができない。
        # shots_meta_df["spm"] = shots_meta_df["spm"].where(shots_meta_df["spm"].notna(), None)
        shots_meta_df.replace(dict(spm={np.nan: None}), inplace=True)
        shots_meta_df.drop(columns=["time_diff"], inplace=True)
        shots_meta_df["timestamp"] = shots_meta_df["timestamp"].apply(lambda x: datetime.utcfromtimestamp(x))

        shots_meta_dict = shots_meta_df.to_dict(orient="records")
        shots_meta_index = "shots-" + target + "-meta"
        ElasticManager.bulk_insert(shots_meta_dict, shots_meta_index)
        logger.info("shots_meta_index bulk insert finished.")


if __name__ == "__main__":
    # 射出成形
    # target_date = "20190523094129"
    # start_time = None

    # デバッグ用少量データ
    # target_date = "20210708113000"
    # start_time = datetime(2021, 7, 8, 11, 30, 0)

    # ダミーデータ
    machine_id = "machine-01"
    target_date = "20210709190000"
    target = machine_id + "-" + target_date
    start_time = datetime(2021, 7, 9, 19, 0, 0)

    target_file_path = "/mnt/datadrive/data/press_senario.npy"

    # 何列目を使うか。
    # use_cols = [2, 6, 7, 11, 57]
    # cols_name: List[str] = ["load01", "load02", "load03", "load04", "displacement"]
    use_cols = [0]
    cols_name: List[str] = ["load01", "displacement"]

    sampling_interval = 10  # 100k
    # sampling_interval = 1000  # 1k

    di = DataImporter()

    # npyをショット毎のcsvファイルに分割
    di.split_np_array_by_shot(target_file_path, target)

    # timestamp_file = "/home/ymiyamoto5/h-one-experimental-system/shared/data/all_sensors_201905_timelist.csv"

    logger.info("process csv files starting...")
    # csvを加工してpklにする
    # timestampファイルがある場合
    # di.process_csv_files(
    #     target_date=target_date,
    #     exists_timestamp=True,
    #     start_time=start_time,
    #     use_cols=use_cols,
    #     cols_name=cols_name,
    #     sampling_interval=sampling_interval,
    #     timestamp_file=timestamp_file,
    # )

    # timestampファイルがない場合
    di.process_csv_files(
        target=target,
        exists_timestamp=False,
        start_time=start_time,
        use_cols=use_cols,
        cols_name=cols_name,
        sampling_interval=sampling_interval,
    )

    logger.info("process csv files finished")

    # pklをelasticsearchに格納
    di.import_by_shot_pkl(target)

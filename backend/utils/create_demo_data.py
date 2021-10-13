"""
デモ用データ作成

対象：press_senario.py
プレス機の刃のなまりを模したダミーデータ。
荷重センサー1つのみ。

データ加工：
パルス値を付与し、ショット切り出しできるようにする。
タイムスタンプ列を付与する。
"""

import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def main():

    machine_id = "demo-machine"
    # ファイル読み込み
    target_file_path = "/mnt/datadrive/data/"
    target_file = "press_senario.npy"
    arr = np.load(target_file_path + target_file)
    # 出力先
    file_dir = target_file_path + machine_id + "-20210709190000"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    start_time = datetime(2021, 7, 9, 19, 0, 0)
    start_time_utc = start_time - timedelta(hours=9)
    sequential_number = 0

    # 4000ショット分ループ
    for shot in arr:
        shot_df = pd.DataFrame(shot, columns=["load01"])

        # pulse列を用意し、1で初期化
        shot_df["pulse"] = 1
        # 最初の1000サンプルと後ろの500サンプルのpulseを0に設定し、切り捨て対象とする。
        shot_df.loc[:1000, "pulse"] = 0
        shot_df.loc[3500:, "pulse"] = 0

        # 連番、時刻列追加
        sequential_numbers = []
        datetime_list = []
        for i in range(len(shot_df)):
            sequential_numbers.append(sequential_number)
            sequential_number += 1
            time = start_time_utc + timedelta(microseconds=10) * i
            datetime_list.append(time.timestamp())
        shot_df["sequential_number"] = sequential_numbers
        shot_df["timestamp"] = datetime_list

        # pickleに出力
        file_datetime_str = datetime.strftime(start_time_utc, "%Y%m%d-%H%M%S.%f")
        pickle_filename: str = machine_id + "_demo-GW_demo-handler_" + file_datetime_str + ".pkl"
        pickle_filepath: str = os.path.join(file_dir, pickle_filename)
        shot_df.to_pickle(pickle_filepath)
        print(f"{pickle_filepath} processed.")

        # 次のループのために1カウント進める
        start_time_utc = time + timedelta(microseconds=10)


if __name__ == "__main__":
    main()

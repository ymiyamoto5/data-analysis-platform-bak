import argparse
import os
import struct
import sys
import time
from datetime import datetime
from typing import Any, Dict, Final, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../../"))

from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.db.session import SessionLocal


def main(machine_id: str):
    db = SessionLocal()

    machine = CRUDMachine.select_by_id(db, machine_id)
    data_collect_history = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)
    sampling_ch_num = data_collect_history.sampling_ch_num

    # 元データ
    freq = 1  # 周波数
    orignal_sampling = 10000
    x = np.linspace(0, 1, orignal_sampling)
    displacement = np.cos(2 * np.pi * x * freq) + 1  # +1上に平行移動
    # +1上に平行移動してノイズを足す
    load01 = np.sin(2 * np.pi * x * freq) + 1 + np.random.randn(orignal_sampling) * 10 ** -2
    load02 = np.sin(2 * np.pi * x * freq) + 1 + np.random.randn(orignal_sampling) * 10 ** -2
    load03 = np.sin(2 * np.pi * x * freq) + 1 + np.random.randn(orignal_sampling) * 10 ** -2
    load04 = np.sin(2 * np.pi * x * freq) + 1 + np.random.randn(orignal_sampling) * 10 ** -2

    sampling_rate = 1 / 100  # 100Hz
    resampling = int(orignal_sampling * sampling_rate)
    x_sample = np.linspace(0, 1, resampling)
    displacement_sample = np.cos(2 * np.pi * x_sample * freq) + 1
    load01_sample = np.sin(2 * np.pi * x_sample * freq) + 1 + np.random.randn(resampling) * 10 ** -2
    load02_sample = np.sin(2 * np.pi * x_sample * freq) + 1 + np.random.randn(resampling) * 10 ** -2
    load03_sample = np.sin(2 * np.pi * x_sample * freq) + 1 + np.random.randn(resampling) * 10 ** -2
    load04_sample = np.sin(2 * np.pi * x_sample * freq) + 1 + np.random.randn(resampling) * 10 ** -2

    # plt.figure()
    # plt.plot(x, displacement, alpha=0.5)
    # plt.plot(x, load01, alpha=0.5)
    # plt.plot(x, load02, alpha=0.5)
    # plt.plot(x, load03, alpha=0.5)
    # plt.plot(x, load04, alpha=0.5)
    # plt.plot(x_sample, displacement_sample, "o")
    # plt.plot(x_sample, load01_sample, "o")
    # plt.plot(x_sample, load02_sample, "o")
    # plt.plot(x_sample, load03_sample, "o")
    # plt.plot(x_sample, load04_sample, "o")
    # plt.savefig("tmp.png")

    data_dir = os.environ["data_dir"]
    gateway_id = machine.gateways[0].gateway_id
    handler_id = machine.gateways[0].handlers[0].handler_id

    for _ in range(100):
        binaries = b""
        for i in range(resampling):
            binary = struct.pack("<ddddd", displacement_sample[i], load01_sample[i], load02_sample[i], load03_sample[i], load04_sample[i])
            binaries += binary

        utc_now = datetime.utcnow()
        now_str = datetime.strftime(utc_now, "%Y%m%d_%H%M%S.%f")
        file_name = f"{machine_id}_{gateway_id}_{handler_id}_{now_str}.dat"
        file_path = os.path.join(data_dir, file_name)

        # 文字列のバイナリファイルへの書き込み
        with open(file_path, "wb") as f:
            f.write(binaries)

        print(f"dat file created: {file_path}")

        # debug
        # read_binary(binaries, sampling_ch_num)

        time.sleep(1)


def read_binary(binary, sampling_ch_num):
    BYTE_SIZE: Final[int] = 8
    SAMPLING_CH_NUM: Final[int] = sampling_ch_num
    ROW_BYTE_SIZE: Final[int] = BYTE_SIZE * SAMPLING_CH_NUM  # 8 byte * チャネル数
    UNPACK_FORMAT: Final[str] = "<" + "d" * SAMPLING_CH_NUM  # 5chの場合 "<ddddd"
    ROUND_DIGITS: Final[int] = 3

    dataset_number: int = 0  # ファイル内での連番
    samples: List[Dict[str, Any]] = []

    sensor_ids_other_than_displacement = ["load01", "load02", "load03", "load04"]

    # バイナリファイルからチャネル数分を1setとして取得し、処理
    while True:
        start_index: int = dataset_number * ROW_BYTE_SIZE
        end_index: int = start_index + ROW_BYTE_SIZE
        binary_dataset: bytes = binary[start_index:end_index]

        if len(binary_dataset) == 0:
            break

        dataset: Tuple[Any, ...] = struct.unpack(UNPACK_FORMAT, binary_dataset)

        sample: Dict[str, Any] = {
            "stroke_displacement": round(dataset[0], ROUND_DIGITS),
        }

        # 変位センサー以外のセンサー
        for i, s in enumerate(sensor_ids_other_than_displacement):
            sample[s] = round(dataset[i + 1], ROUND_DIGITS)

        samples.append(sample)

        dataset_number += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--machine", help="set machine_id", required=True)
    args = parser.parse_args()
    machine_id: str = args.machine

    main(machine_id)

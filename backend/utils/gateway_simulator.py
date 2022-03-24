import argparse
import os
import struct
import sys
from datetime import datetime
from typing import Any, Dict, Final, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../../"))

from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.db.session import SessionLocal


def main(machine_id: str, show_fig: bool = False):
    """バイナリデータを生成する。対象機器でデータ収集を開始後に実行すること"""
    db = SessionLocal()

    try:
        data_collect_history = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)
        handlers = CRUDDataCollectHistory.select_cut_out_target_handlers_by_hisotry_id(db, data_collect_history.id)
        sensors = CRUDDataCollectHistory.select_cut_out_target_sensors_by_history_id(db, data_collect_history.id)
    except Exception:
        print("Read DB error.")

    is_multi_handler = True if len(handlers) >= 2 else False

    # 元データ
    freq = 1  # 周波数
    original = 10000
    x = np.linspace(0, 1, original)

    y = {}
    for sensor in sensors:
        if sensor.sensor_id == "dummy":
            y[sensor.sensor_id] = np.array([0.0] * 10000)
        elif sensor.sensor_id == "stroke_displacement":
            y[sensor.sensor_id] = np.cos(2 * np.pi * x * freq) + 1  # cos波を+1上に平行移動
        else:
            y[sensor.sensor_id] = np.sin(2 * np.pi * x * freq) + 1 + np.random.randn(original) * 10 ** -2  # sin波を+1上に平行移動しノイズを追加

    # 元データをサンプリング
    sampling_rate = 100  # 100Hz
    sampling_interval = 1 / sampling_rate
    resampling = int(original * sampling_interval)
    x_sample = np.linspace(0, 1, resampling)
    y_sample = {}
    for k, v in y.items():
        y_sample[k] = v[::resampling]

    if show_fig:
        save_fig(x, y, x_sample, y_sample)

    if is_multi_handler:
        simulate_multi_handler(machine_id, handlers, resampling, y_sample)
    else:
        simulate_single_handler(machine_id, handlers[0], resampling, y_sample)


def save_fig(x, y, x_sample, y_sample):
    """グラフ表示"""
    plt.figure()
    for v in y.values():
        plt.plot(x, v, alpha=0.5)

    for v in y_sample.values():
        plt.plot(x_sample, v, "o")

    plt.savefig("tmp.png")


def output_file(machine_id, gateway_id, handler_id, file_number, binaries):
    """バイナリファイル出力"""
    data_dir = os.environ["data_dir"]
    utc_now = datetime.utcnow()
    now_str = datetime.strftime(utc_now, "%Y%m%d_%H%M%S.%f")
    file_name = f"{machine_id}_{gateway_id}_{handler_id}_{now_str}_{file_number}.dat"
    file_path = os.path.join(data_dir, file_name)

    # 文字列のバイナリファイルへの書き込み
    with open(file_path, "wb") as f:
        f.write(binaries)

    print(f"dat file created: {file_path}")


def simulate_single_handler(machine_id, handler, resampling, y_sample):
    gateway_id = handler.data_collect_history_gateway.gateway_id
    handler_id = handler.handler_id

    for file_number in range(100):
        binaries = b""
        for i in range(resampling):
            binary = struct.pack(
                "<ddddd",
                y_sample["stroke_displacement"][i],
                y_sample["load01"][i],
                y_sample["load02"][i],
                y_sample["load03"][i],
                y_sample["load04"][i],
            )
            binaries += binary

        output_file(machine_id, gateway_id, handler_id, file_number, binaries)


def simulate_multi_handler(machine_id, handlers, resampling, y_sample):
    gateway_id = handlers[0].data_collect_history_gateway.gateway_id
    handler_ids = [x.handler_id for x in handlers]

    for file_number in range(100):
        binaries = b""
        for i in range(resampling):
            binary = struct.pack(
                "<dddddd",
                y_sample["stroke_displacement"][i],
                y_sample["load01"][i],
                y_sample["load02"][i],
                y_sample["load03"][i],
                y_sample["load04"][i],
                y_sample["dummy"][i],
            )
            binaries += binary

        output_file(machine_id, gateway_id, handler_ids[0], file_number, binaries)


def read_binary(binary, sampling_ch_num):
    """生成したバイナリファイルの読み込み（デバッグ用）"""
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
    parser.add_argument("-s", "--show_fig", help="show figure(tmp.png)", action="store_true")
    args = parser.parse_args()
    machine_id: str = args.machine
    show_fig: bool = args.show_fig

    main(machine_id, show_fig)

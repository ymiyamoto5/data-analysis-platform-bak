import os
import sys

# import csv
import json
import glob
import re
import shutil
import asyncio
import struct
import logging
import logging.handlers
import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone
from typing import Final, NamedTuple, Tuple, Coroutine
import pandas as pd
import multiprocessing

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
from elastic_manager import ElasticManager
import common

LOG_FILE: Final = "log/data_recorder/data_recorder.log"
MAX_LOG_SIZE: Final = 1024 * 1024  # 1MB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=5),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class FileInfo(NamedTuple):
    file_path: str
    timestamp: datetime


def _create_file_timestamp(filepath: str) -> datetime:
    """ ファイル名から日時データを作成する """

    filename: str = os.path.basename(filepath)

    parts: list = re.findall(r"\d+", filename)
    timestamp_str: str = parts[1] + parts[2] + parts[3]
    timestamp: datetime = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S%f")
    return timestamp


def _get_target_interval(config_file_path: str):
    """ 処理対象となる区間（開始/終了時刻）を取得する """

    with open(config_file_path, "r") as f:
        config: dict = json.load(f)

    if config.get("start_time") is None:
        logger.info("data collect is not started.")
        return None, None

    start_time: datetime = datetime.strptime(config["start_time"], "%Y%m%d%H%M%S%f")

    if config.get("end_time") is None:
        end_time: datetime = datetime.max
    else:
        end_time: datetime = datetime.strptime(config["end_time"], "%Y%m%d%H%M%S%f")

    if start_time > end_time:
        logger.exception(f"start_time({start_time}) > end_time({end_time}). This is abnormal condition.")
        raise ValueError

    logger.info(f"target interval: {start_time} - {end_time}")

    return start_time, end_time


def _get_target_files(files_info: list, start_time: datetime, end_time: datetime) -> list:
    """ 処理対象(開始/終了区間に含まれる）ファイルリストを返す """

    return list(filter(lambda x: start_time <= x.timestamp <= end_time, files_info))


def _read_binary_file(file: str, sequential_number: int):
    """ バイナリファイルを読んで、そのデータをリストにして返す """

    ROW_BYTE_SIZE: Final = 8 * 5  # 8 byte * 5 column

    dataset_number = 0  # ファイル内での連番
    timestamp: float = file.timestamp.timestamp()
    samples: list = []

    with open(file.file_path, "rb") as f:
        binary = f.read()
        while True:
            # バイナリファイルから5ch分を1setとして取得し、処理
            start_index = dataset_number * ROW_BYTE_SIZE
            end_index = start_index + ROW_BYTE_SIZE
            binary_dataset = binary[start_index:end_index]

            if len(binary_dataset) == 0:
                break

            dataset: Tuple = struct.unpack("<ddddd", binary_dataset)
            logger.debug(dataset)

            data = {
                "sequential_number": sequential_number,
                "timestamp": timestamp,
                "displacement": round(dataset[0], 3),
                "load01": round(dataset[1], 3),
                "load02": round(dataset[2], 3),
                "load03": round(dataset[3], 3),
                "load04": round(dataset[4], 3),
            }

            samples.append(data)

            dataset_number += 1
            sequential_number += 1
            timestamp += 0.000010  # 100k sample

    return samples, sequential_number


def _multi_process(files: list, index_to_import: str, processed_dir_path: str, num_of_process: int = 8):
    num_of_files = len(files)

    # batch_size, mod = divmod(num_of_files, num_of_process)

    procs: list = []

    # 均等配分
    # ex) num_of_files: 39, num_of_process: 8  = [4, 5, 5, 5, 5, 5, 5, 5]
    file_num_by_proc: list = [(num_of_files + i) // num_of_process for i in range(num_of_process)]

    start_index: int = 0
    for proc_number, file_num in enumerate(file_num_by_proc):
        end_index: int = start_index + file_num
        target_files: list = files[start_index:end_index]
        start_index += file_num

        logger.info(f"process {proc_number} will execute {len(target_files)} files.")

        proc = multiprocessing.Process(
            target=_binary_to_storage, args=(target_files, index_to_import, processed_dir_path)
        )
        proc.start()
        procs.append(proc)

    for p in procs:
        p.join()


def _binary_to_storage(target_files: list, index_to_import: str, processed_dir_path: str):
    ROW_BYTE_SIZE: Final = 8 * 5  # 8 byte * 5 column

    # timestamp: float = file.timestamp.timestamp()
    samples: list = []

    for file_number, file in enumerate(target_files):
        with open(file.file_path, "rb") as f:
            binary = f.read()
            dataset_number = 0  # ファイル内での連番
            timestamp = file.timestamp

            while True:
                # バイナリファイルから5ch分を1setとして取得し、処理
                start_index = dataset_number * ROW_BYTE_SIZE
                end_index = start_index + ROW_BYTE_SIZE
                binary_dataset = binary[start_index:end_index]

                if len(binary_dataset) == 0:
                    break

                dataset: Tuple = struct.unpack("<ddddd", binary_dataset)
                logger.debug(dataset)

                data = {
                    # "sequential_number": timestamp,
                    "timestamp": timestamp,
                    "displacement": round(dataset[0], 3),
                    "load01": round(dataset[1], 3),
                    "load02": round(dataset[2], 3),
                    "load03": round(dataset[3], 3),
                    "load04": round(dataset[4], 3),
                }
                samples.append(data)
                dataset_number += 1
                # timestamp += 0.000010
                timestamp += timedelta(microseconds=10)

        procs = ElasticManager.multi_process_bulk_lazy_join(
            data=samples, index_to_import=index_to_import, num_of_process=12, chunk_size=5000
        )

        # テンポラリファイル出力
        df = pd.DataFrame(samples)
        # df.set_index("timestamp", inplace=True)

        pickle_filename = os.path.splitext(os.path.basename(file.file_path))[0] + ".pkl"
        pickle_filepath = os.path.join(processed_dir_path, pickle_filename)
        df.to_pickle(pickle_filepath)

        for p in procs:
            p.join()

        logger.info(f"pid: {os.getpid()}, {len(samples)} sample processed. {pickle_filename}")
        samples = []


def _create_files_info(shared_dir: str) -> list:
    # バイナリファイルの情報（パスとファイル名から抽出した日時）リストを生成

    file_list: list = glob.glob(os.path.join(shared_dir, "*.dat"))
    if len(file_list) == 0:
        return None
    file_list.sort()

    # ファイルリストから時刻データを生成
    files_timestamp = map(_create_file_timestamp, file_list)
    # リストを作成 [{"file_path": "xxx", "timestamp": "yyy"},...]
    files_info: list = [FileInfo._make(row) for row in zip(file_list, files_timestamp)]

    return files_info


def main() -> None:
    settings_file_path: str = os.path.dirname(__file__) + "/../common/settings.json"

    # データディレクトリを確認し、ファイルリストを作成
    data_dir = common.get_settings_value(settings_file_path, "data_dir")
    files_info: list = _create_files_info(data_dir)

    if files_info is None:
        logger.info(f"No files in {data_dir}")
        return

    # configファイルからstart-endtimeを取得
    config_file = common.get_settings_value(settings_file_path, "config_file_path")
    start_time, end_time = _get_target_interval(config_file)

    if start_time is None:
        return

    # 対象となるファイルに絞り込む
    target_files: list = _get_target_files(files_info, start_time, end_time)
    # [print(x.file_path) for x in target_files]

    # TODO: 含まれないファイルは削除する

    if len(target_files) == 0:
        logger.info(f"No files in target inteverl {start_time} - {end_time}.")
        return

    # 処理済みファイルおよびテンポラリファイル格納用のディレクトリ作成
    jst = start_time.astimezone(timezone("Asia/Tokyo"))
    processed_dir_path = os.path.join(data_dir, datetime.strftime(jst, "%Y%m%d%H%M%S"))
    os.makedirs(processed_dir_path, exist_ok=True)

    # Elasticsearch rawdataインデックス名
    rawdata_index: str = "rawdata-" + datetime.strftime(jst, "%Y%m%d%H%M%S")

    # テスト用の実装
    if ElasticManager.exists_index(rawdata_index):
        ElasticManager.delete_index(rawdata_index)
    mapping_file = "mappings/mapping_rawdata.json"
    ElasticManager.create_index(rawdata_index, mapping_file)

    # 本来の実装
    # if not ElasticManager.exists_index(rawdata_index):
    #     mapping_file = "mappings/mapping_rawdata.json"
    #     ElasticManager.create_index(rawdata_index, mapping_file)

    # TODO: sequential_numberの初期値を決めるため、ESからcountを取る

    # テンポラリファイル名のプレフィックス
    # pickle_filename_prefix: str = os.path.join(processed_dir_path, "tmp")

    _multi_process(target_files, rawdata_index, processed_dir_path, 8)

    # 処理済みディレクトリに退避
    # shutil.move(file.file_path, processed_dir_path)
    # logger.info(f"processed: {file.file_path}")

    logger.info("all file processed.")


if __name__ == "__main__":
    main()

import multiprocessing
import os
import sys

import json
import glob
import re
import shutil
import struct
import logging
import logging.handlers
import pandas as pd
from datetime import datetime
from pandas.core.frame import DataFrame
from pytz import timezone
from typing import Final, Tuple, List, Mapping
import pandas as pd
import dataclasses

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


@dataclasses.dataclass
class FileInfo:
    __slots__ = (
        "file_path",
        "timestamp",
    )
    file_path: str
    timestamp: datetime


def _create_file_timestamp(filepath: str) -> datetime:
    """ ファイル名から日時データを作成する。
        ファイル名は AD-XX_YYYYmmddHHMMSS.ffffff 形式が前提となる。
    """

    filename: str = os.path.basename(filepath)

    parts: List[str] = re.findall(r"\d+", filename)
    timestamp_str: str = parts[-3] + parts[-2] + parts[-1]
    timestamp: datetime = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S%f")
    return timestamp


def _get_target_interval(config_file_path: str) -> Tuple[datetime, datetime]:
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
        raise ValueError(f"start_time({start_time}) > end_time({end_time}). This is abnormal condition.")

    logger.info(f"target interval: {start_time} - {end_time}")

    return start_time, end_time


def _get_target_files(files_info: List[FileInfo], start_time: datetime, end_time: datetime) -> List[FileInfo]:
    """ 処理対象(開始/終了区間に含まれる）ファイルリストを返す """

    return list(filter(lambda x: start_time <= x.timestamp <= end_time, files_info))


def _read_binary_files(file: FileInfo, sequential_number: int) -> Tuple[List[dict], int]:
    """ バイナリファイルを読んで、そのデータをリストにして返す """

    ROW_BYTE_SIZE: Final = 8 * 5  # 8 byte * 5 column

    dataset_number: int = 0  # ファイル内での連番
    timestamp: float = file.timestamp.timestamp()
    samples: List[dict] = []

    with open(file.file_path, "rb") as f:
        binary: bytes = f.read()

    # バイナリファイルから5ch分を1setとして取得し、処理
    while True:
        start_index: int = dataset_number * ROW_BYTE_SIZE
        end_index: int = start_index + ROW_BYTE_SIZE
        binary_dataset: bytes = binary[start_index:end_index]

        if len(binary_dataset) == 0:
            break

        dataset: Tuple[float, float, float, float, float] = struct.unpack("<ddddd", binary_dataset)
        logger.debug(dataset)

        sample: dict = {
            "sequential_number": sequential_number,
            "timestamp": timestamp,
            "displacement": round(dataset[0], 3),
            "load01": round(dataset[1], 3),
            "load02": round(dataset[2], 3),
            "load03": round(dataset[3], 3),
            "load04": round(dataset[4], 3),
        }

        samples.append(sample)

        dataset_number += 1
        sequential_number += 1
        timestamp += 0.000010  # 100k sample

    return samples, sequential_number


def _create_files_info(shared_dir: str) -> List[FileInfo]:
    """ バイナリファイルの情報（パスとファイル名から抽出した日時）リストを生成 """

    file_list: List[str] = glob.glob(os.path.join(shared_dir, "*.dat"))

    if len(file_list) == 0:
        return None

    file_list.sort()

    # ファイルリストから時刻データを生成
    files_timestamp: Mapping = map(_create_file_timestamp, file_list)
    # リストを作成 [{"file_path": "xxx", "timestamp": "yyy"},...]
    files_info: List[FileInfo] = [
        FileInfo(file_path=row[0], timestamp=row[1]) for row in zip(file_list, files_timestamp)
    ]

    return files_info


def _export_to_pickle(samples: list, file: FileInfo, processed_dir_path: str) -> None:
    """ pickleファイルに出力する """

    # テンポラリファイルにsequential_numberは不要なので除去
    samples: List[dict] = [
        {
            "timestamp": x["timestamp"],
            "displacement": x["displacement"],
            "load01": x["load01"],
            "load02": x["load02"],
            "load03": x["load03"],
            "load04": x["load04"],
        }
        for x in samples
    ]
    df: DataFrame = pd.DataFrame(samples)
    # df.set_index("timestamp", inplace=True)
    pickle_filename: str = os.path.splitext(os.path.basename(file.file_path))[0]
    pickle_filepath: str = os.path.join(processed_dir_path, pickle_filename) + ".pkl"
    df.to_pickle(pickle_filepath)


def main(settings_file_path: str, mode=None) -> None:

    # データディレクトリを確認し、ファイルリストを作成
    data_dir: str = common.get_settings_value(settings_file_path, "data_dir")
    files_info: list = _create_files_info(data_dir)

    if len(files_info) == 0:
        logger.info(f"No files in {data_dir}")
        return

    # configファイルからstart-endtimeを取得
    config_file: str = common.get_settings_value(settings_file_path, "config_file_path")
    start_time: datetime
    end_time: datetime
    start_time, end_time = _get_target_interval(config_file)

    if start_time is None:
        return

    # 対象となるファイルに絞り込む
    target_files: list = _get_target_files(files_info, start_time, end_time)

    # TODO: 含まれないファイルは削除する

    if len(target_files) == 0:
        logger.info(f"No files in target inteverl {start_time} - {end_time}.")
        return

    logger.info(f"{len(target_files)} / {len(files_info)} files are target.")

    # 処理済みファイルおよびテンポラリファイル格納用のディレクトリ作成。ディレクトリ名はconfigのstart_timeを基準とする。
    start_time_jst: datetime = start_time.astimezone(timezone("Asia/Tokyo"))
    processed_dir_path: str = os.path.join(data_dir, datetime.strftime(start_time_jst, "%Y%m%d%H%M%S"))
    os.makedirs(processed_dir_path, exist_ok=True)

    # Elasticsearch rawdataインデックス名
    rawdata_index: str = "rawdata-" + datetime.strftime(start_time_jst, "%Y%m%d%H%M%S")

    # テスト時はインデックスを都度再作成する。
    if mode == "TEST":
        if ElasticManager.exists_index(rawdata_index):
            ElasticManager.delete_index(rawdata_index)
        mapping_file: str = "mappings/mapping_rawdata.json"
        setting_file: str = "mappings/setting_rawdata.json"
        ElasticManager.create_index(rawdata_index, mapping_file, setting_file)
    # 通常はconfigのstart_timeが変わらない（格納先が変わらない）限り、同一インデックスにデータを追記していく
    else:
        if not ElasticManager.exists_index(rawdata_index):
            mapping_file: str = "mappings/mapping_rawdata.json"
            setting_file: str = "mappings/setting_rawdata.json"
            ElasticManager.create_index(rawdata_index, mapping_file, setting_file)

    sequential_number: int = ElasticManager.count(rawdata_index)  # ファイルを跨いだ連番

    procs: List[multiprocessing.context.Process] = []
    for file in target_files:
        # バイナリファイルを読み取り、データリストを取得
        samples: List[dict]
        sequential_number: int
        samples, sequential_number = _read_binary_files(file, sequential_number)

        if len(procs) > 0:
            for p in procs:
                p.join()
            procs = []

        procs = ElasticManager.multi_process_bulk_lazy_join(
            data=samples, index_to_import=rawdata_index, num_of_process=12, chunk_size=5000
        )

        _export_to_pickle(samples, file, processed_dir_path)

        # 処理済みディレクトリに退避。テスト時は退避しない。
        if mode != "TEST":
            shutil.move(file.file_path, processed_dir_path)
        logger.info(f"processed: {file.file_path}")

    # 最終ループでjoinできていないprocessを待機。
    if len(procs) > 0:
        for p in procs:
            p.join()

    logger.info("all file processed.")


if __name__ == "__main__":
    settings_file_path: str = os.path.dirname(__file__) + "/../common/app_config.json"
    main(settings_file_path, mode="TEST")

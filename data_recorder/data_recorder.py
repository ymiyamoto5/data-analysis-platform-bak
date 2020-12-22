import os
import sys
import csv
import json
import glob
import re
import shutil
import struct
import logging
import logging.handlers
from datetime import datetime, timedelta
from pytz import timezone
from typing import Final, NamedTuple

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
from elastic_manager import ElasticManager

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


def create_file_timestamp(filename: str) -> dict:
    """ ファイル名から日時データを作成する """

    parts: list = re.findall(r"\d+", filename)
    timestamp_str: str = parts[1] + parts[2] + parts[3]
    timestamp: datetime = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S%f")
    return timestamp


def main() -> None:
    # バイナリファイルリストを生成
    shared_dir = "data/pseudo_data/"
    file_list: list = glob.glob(shared_dir + "*.dat")
    if len(file_list) == 0:
        return
    file_list.sort()

    # configファイルからstart-endtimeを取得
    settings_file_path = os.path.dirname(__file__) + "/../common/settings.json"
    with open(settings_file_path, "r") as f:
        settings: dict = json.load(f)
        config_file_path = settings["config_file_path"]
    with open(config_file_path, "r") as f:
        config: dict = json.load(f)

    if config.get("start_time") is None:
        logger.info("data collect is not started.")
        return

    start_time: datetime = datetime.strptime(config["start_time"], "%Y%m%d%H%M%S%f")

    if config.get("end_time") is None:
        end_time: datetime = datetime.max
    else:
        end_time: datetime = datetime.strptime(config["end_time"], "%Y%m%d%H%M%S%f")

    logger.info(f"target interval: {start_time} - {end_time}")

    # ファイルリストから時刻データを生成
    files_timestamp = map(create_file_timestamp, file_list)
    # [{"file_path": "xxx", "timestamp": "yyy"},...]
    files_info: list = [FileInfo._make(row) for row in zip(file_list, files_timestamp)]

    # 対象となるファイルに絞り込む
    target_files: list = list(filter(lambda x: start_time <= x.timestamp <= end_time, files_info))
    # [print(x.file_path) for x in target_files]

    # TODO: 含まれないファイルは削除する

    # 区間に含まれるファイルがなければreturn
    if len(target_files) == 0:
        logger.info(f"No files in target inteverl {start_time} - {end_time}.")
        return

    # 処理済みのファイル格納用ディレクトリ作成。starttimeを名前とする。
    processed_dir_path = os.path.join(shared_dir, datetime.strftime(start_time, "%Y%m%d%H%M%S%f"))
    os.makedirs(processed_dir_path, exist_ok=True)

    # 出力csvパス
    csv_file: str = os.path.join(processed_dir_path, datetime.strftime(start_time, "%Y%m%d%H%M%S%f") + ".csv")
    # Elasticsearch rawdataインデックス名
    jst = start_time.astimezone(timezone("Asia/Tokyo"))
    rawdata_index: str = "rawdata-" + datetime.strftime(jst, "%Y%m%d%H%M%S")

    if not ElasticManager.exists_index(rawdata_index):
        ElasticManager.create_index(rawdata_index)

    sequential_number: int = ElasticManager.count(rawdata_index)  # ファイルを跨いだ連番

    ROW_BYTE_SIZE: Final = 8 * 5  # 8 byte * 5 column

    for file in target_files:
        dataset_number = 0  # ファイル内での連番
        dataset_timestamp: datetime = file.timestamp
        samples: list = []

        # バイナリ読み込み
        with open(file.file_path, "rb") as f:
            binary = f.read()
            while True:
                # バイナリファイルから5ch分を1setとして取得し、処理
                start_index = dataset_number * ROW_BYTE_SIZE
                end_index = start_index + ROW_BYTE_SIZE
                binary_dataset = binary[start_index:end_index]

                if len(binary_dataset) == 0:
                    break

                dataset = struct.unpack("<ddddd", binary_dataset)
                logger.debug(dataset)

                data = {
                    "sequential_number": sequential_number,
                    "timestamp": dataset_timestamp.isoformat(),
                    "displacement": dataset[0],
                    "load01": dataset[1],
                    "load02": dataset[2],
                    "load03": dataset[3],
                    "load04": dataset[4],
                }
                samples.append(data)

                dataset_number += 1
                sequential_number += 1
                dataset_timestamp += timedelta(microseconds=10)  # 100k sample

        # elasticsearch出力
        NUM_OF_PROCESS: Final = 8
        BULK_CHUNK_SIZE: Final = 5000
        ElasticManager.multi_process_bulk(samples, rawdata_index, NUM_OF_PROCESS, BULK_CHUNK_SIZE)

        # csv出力
        with open(csv_file, "a") as f:
            writer = csv.DictWriter(
                f, ["sequential_number", "timestamp", "displacement", "load01", "load02", "load03", "load04"]
            )
            writer.writerows(samples)

        # 処理済みディレクトリに退避
        shutil.move(file.file_path, processed_dir_path)


if __name__ == "__main__":
    main()

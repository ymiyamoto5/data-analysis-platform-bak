from datetime import datetime, time, timedelta
import os
import sys
import json
import glob
import re
import shutil
import logging
import logging.handlers
from typing import Final, NamedTuple
from collections import namedtuple

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


# class Interval(NamedTuple):
#     start_time: datetime
#     end_time: datetime


def record() -> None:
    """ """
    shared_dir = "data/pseudo_data/"

    file_list: list = glob.glob(shared_dir + "*.dat")
    if len(file_list) == 0:
        return
    file_list.sort()

    # configファイルからstart-endtimeを取得。
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
        end_time: datetime = config["end_time"]

    logger.info(f"target section: {start_time} - {end_time}")

    # ファイルリストから時刻データを生成
    files_timestamp = map(create_file_timestamp, file_list)
    # [{"file_path": "xxx", "timestamp": "yyy"},...]
    files_info: list = [FileInfo._make(row) for row in zip(file_list, files_timestamp)]

    # 対象となるファイルに絞り込む
    target_files: list = list(filter(lambda x: start_time <= x.timestamp <= end_time, files_info))
    for x in target_files:
        print(x)

    # 含まれないファイルは削除する

    # 区間に含まれるファイルがなければreturn
    if len(target_files) == 0:
        logger.info(f"No files in target inteverl {start_time} - {end_time}.")
        return

    # starttimeを名前とするディレクトリを作成し、そこにファイルを退避
    processed_dir_path = os.path.join(shared_dir, datetime.strftime(start_time, "%Y%m%d%H%M%S%f"))
    os.makedirs(processed_dir_path, exist_ok=True)

    for file in target_files:
        # バイナリ読み込み

        # csv, es出力

        # 処理済みディレクトリに退避
        # shutil.move(file, processed_dir_path)


def create_file_timestamp(filename: str) -> dict:
    """ ファイル名から日時データを作成する """

    parts: list = re.findall(r"\d+", filename)
    timestamp_str: str = parts[1] + parts[2] + parts[3]
    timestamp: datetime = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S%f")
    return timestamp


# def extract_files_in_target(file_info: dict, interval):
#     if file_info.timestamp


def main():
    record()


if __name__ == "__main__":
    main()

import multiprocessing
import os
import sys
import glob
import re
import shutil
import struct
import logging
import logging.handlers
import pandas as pd
from datetime import datetime, timezone
from pandas.core.frame import DataFrame
from typing import Final, Tuple, List, Mapping, Optional
import dataclasses
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import common
from utils.common import DisplayTime
from time_logger import time_log

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class FileInfo:
    __slots__ = (
        "file_path",
        "timestamp",
    )
    file_path: str
    timestamp: float


def _create_file_timestamp(filepath: str) -> float:
    """ ファイル名から日時データを作成する。
        ファイル名は AD-XX_YYYYmmddHHMMSS.ffffff 形式が前提となる。
    """

    filename: str = os.path.basename(filepath)

    parts: List[str] = re.findall(r"\d+", filename)
    timestamp_str: str = parts[-3] + parts[-2] + parts[-1]
    timestamp: float = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S%f").timestamp()
    return timestamp


def _get_collect_start_time(events: List[dict]) -> Optional[float]:
    """ events_indexから収集（段取）開始時間を取得 """

    setup_events: List[dict] = [x for x in events if x["event_type"] == "setup"]

    if len(setup_events) == 0:
        logger.error("Data collection has not started yet.")
        raise SystemExit

    setup_event: dict = setup_events[0]
    collect_start_time: float = datetime.fromisoformat(setup_event["occurred_time"]).timestamp()

    return collect_start_time


def _get_collect_end_time(events: List[dict]) -> float:
    """ events_indexから収集終了時間を取得 """

    end_events: List[dict] = [x for x in events if x["event_type"] == "stop"]

    if len(end_events) == 0:
        logger.info("Data collect is not finished yet. end_time is set to max.")
        end_time: float = common.TIMESTAMP_MAX
    else:
        end_event: dict = end_events[0]
        end_time: float = datetime.fromisoformat(end_event["occurred_time"]).timestamp()

    return end_time


def _get_target_interval(events: List[dict]) -> Tuple[float, float]:
    """ 処理対象となる区間（開始/終了時刻）を取得する """

    start_time: float = _get_collect_start_time(events)

    if start_time is None:
        raise SystemExit

    end_time: float = _get_collect_end_time(events)

    if end_time == common.TIMESTAMP_MAX:
        logger.info(f"target interval: {datetime.fromtimestamp(start_time)} - ")
    else:
        logger.info(f"target interval: {datetime.fromtimestamp(start_time)} - {datetime.fromtimestamp(end_time)}")

    return start_time, end_time


def _get_target_files(files_info: List[FileInfo], start_time: float, end_time: float) -> List[FileInfo]:
    """ 処理対象(開始/終了区間に含まれる）ファイルリストを返す """

    return list(filter(lambda x: start_time <= x.timestamp <= end_time, files_info))


def _get_not_target_files(files_info: List[FileInfo], start_time: float, end_time: float) -> List[FileInfo]:
    """ 処理対象外(開始/終了区間に含まれない）ファイルリストを返す """

    return list(filter(lambda x: (x.timestamp < start_time or x.timestamp > end_time), files_info))


def _read_binary_files(file: FileInfo, sequential_number: int) -> Tuple[List[dict], int]:
    """ バイナリファイルを読んで、そのデータをリストにして返す """

    ROW_BYTE_SIZE: Final = 8 * 5  # 8 byte * 5 column

    dataset_number: int = 0  # ファイル内での連番
    timestamp: float = file.timestamp
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

        timestamp += common.SAMPLING_INTERVAL  # 100k sample固定

    return samples, sequential_number


def _create_files_info(data_dir: str) -> Optional[List[FileInfo]]:
    """ バイナリファイルの情報（パスとファイル名から抽出した日時）リストを生成 """

    file_list: List[str] = glob.glob(os.path.join(data_dir, "*.dat"))

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


def _export_to_pickle(samples: List[dict], file: FileInfo, processed_dir_path: str) -> None:
    """ pickleファイルに出力する """

    df: DataFrame = pd.DataFrame(samples)

    pickle_filename: str = os.path.splitext(os.path.basename(file.file_path))[0]
    pickle_filepath: str = os.path.join(processed_dir_path, pickle_filename) + ".pkl"
    df.to_pickle(pickle_filepath)


def _data_record(rawdata_index: str, target_files: List[FileInfo], processed_dir_path: str) -> None:
    """ バイナリファイル読み取りおよびES/pkl出力 """

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

        procs = ElasticManager.multi_process_bulk_lazy_join(
            data=samples, index_to_import=rawdata_index, num_of_process=12, chunk_size=5000
        )

        _export_to_pickle(samples, file, processed_dir_path)

        # 処理済みディレクトリに退避。テスト時は退避しない。
        if MODE != "TEST":
            shutil.move(file.file_path, processed_dir_path)
        logger.info(f"processed: {file.file_path}")

    if len(procs) > 0:
        for p in procs:
            p.join()


@time_log
def main() -> None:

    # データディレクトリを確認し、ファイルリストを作成
    data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")
    files_info: Optional[List[FileInfo]] = _create_files_info(data_dir)

    if files_info is None:
        logger.info(f"No files in {data_dir}")
        return

    # 直近のevents_indexからイベント取得
    latest_events_index: Optional[str] = ElasticManager.get_latest_events_index()
    if latest_events_index is None:
        logger.error("events_index is not found.")
        return

    # TODO: 削除
    if MODE == "TEST":
        latest_events_index: str = "events-20201216165900"

    suffix: str = latest_events_index.split("-")[1]
    events_index: str = "events-" + suffix
    query: dict = {"sort": {"event_id": {"order": "asc"}}}
    events: List[dict] = ElasticManager.get_docs(index=events_index, query=query)

    # 最後のイベントがrecordedの場合、前回のデータ採取＆記録完了から状態が変わっていないので、何もしない
    if events[-1]["event_type"] == "recorded":
        logger.info("Exits because the latest event is 'recorded'. May be data collect has not started yet.")
        return

    start_time: float
    end_time: float
    start_time, end_time = _get_target_interval(events)

    # 対象となるファイルに絞り込む
    target_files: List[FileInfo] = _get_target_files(files_info, start_time, end_time)

    # 含まれないファイルは削除する
    not_target_files: List[FileInfo] = _get_not_target_files(files_info, start_time, end_time)
    if MODE != "TEST":
        for file in not_target_files:
            os.remove(file.file_path)
            logger.info(f"{file.file_path} has been deleted because it is out of range.")

    if len(target_files) == 0:
        logger.info("No files in target inteverl")
        return

    logger.info(f"{len(target_files)} / {len(files_info)} files are target.")

    # 処理済みファイルおよびテンポラリファイル格納用のディレクトリ作成。
    processed_dir_path: str = os.path.join(data_dir, suffix)
    if os.path.isdir(processed_dir_path):
        logger.debug(f"{processed_dir_path} is already exists")
    else:
        os.makedirs(processed_dir_path)
        logger.info(f"{processed_dir_path} created.")

    # Elasticsearch rawdataインデックス名
    rawdata_index: str = "rawdata-" + suffix

    # テスト時はインデックスを都度再作成する。
    if MODE == "TEST":
        if ElasticManager.exists_index(rawdata_index):
            ElasticManager.delete_index(rawdata_index)
        mapping_file: str = common.get_config_value(common.APP_CONFIG_PATH, "mapping_rawdata_path")
        setting_file: str = common.get_config_value(common.APP_CONFIG_PATH, "setting_rawdata_path")
        ElasticManager.create_index(rawdata_index, mapping_file, setting_file)
    # 通常はconfigのstart_timeが変わらない（格納先が変わらない）限り、同一インデックスにデータを追記していく
    else:
        if not ElasticManager.exists_index(rawdata_index):
            mapping_file: str = common.get_config_value(common.APP_CONFIG_PATH, "mapping_rawdata_path")
            setting_file: str = common.get_config_value(common.APP_CONFIG_PATH, "setting_rawdata_path")
            ElasticManager.create_index(rawdata_index, mapping_file, setting_file)

    _data_record(rawdata_index, target_files, processed_dir_path)

    logger.info("all file processed.")


def _is_now_recording() -> bool:
    """ 多重記録防止のため、現在データ収集中かを判断する。直近のevents_indexのdocがrecordedでなければ記録中。 """

    latest_events_index: Optional[str] = ElasticManager.get_latest_events_index()

    if latest_events_index is None:
        logger.error("Exits because latest events index not exists.")
        return True

    latest_events_index_doc: Optional[dict] = ElasticManager.get_latest_events_index_doc(latest_events_index)

    if latest_events_index_doc is None:
        logger.error("Exits because latest events index doc not exists.")
        return True

    event_type: str = latest_events_index_doc["event_type"]

    if event_type != "recorded":
        logger.error(f"Exits because latest event is {event_type}. Latest event should be 'recorded'.")
        return True


@time_log
def manual_record(rawdata_dir_name: str):
    """ 手動での生データ記録。手動実行時の時刻をベースにevents_indexとrawdata_indexを生成する。 """

    files_info: Optional[List[FileInfo]] = _create_files_info(rawdata_dir_name)

    if files_info is None:
        logger.info(f"No files in {rawdata_dir_name}")
        return

    if _is_now_recording():
        return

    utc_now: datetime = datetime.utcnow()
    jst_now: DisplayTime = DisplayTime(utc_now)
    suffix: str = jst_now.to_string()

    # events_index作成
    events_index: str = "events-" + suffix
    ElasticManager.delete_exists_index(index=events_index)
    ElasticManager.create_index(events_index)

    ElasticManager.create_doc(
        index=events_index, doc_id=0, query={"event_id": 0, "event_type": "setup", "occurred_time": utc_now}
    )
    ElasticManager.create_doc(
        index=events_index, doc_id=1, query={"event_id": 1, "event_type": "start", "occurred_time": utc_now}
    )

    # rawdata-index作成
    rawdata_index: str = "rawdata-" + suffix
    ElasticManager.delete_exists_index(index=rawdata_index)
    mapping_file: str = common.get_config_value(common.APP_CONFIG_PATH, "mapping_rawdata_path")
    setting_file: str = common.get_config_value(common.APP_CONFIG_PATH, "setting_rawdata_path")
    ElasticManager.create_index(rawdata_index, mapping_file, setting_file)

    processed_dir_path: str = os.path.join(rawdata_dir_name, suffix)
    os.makedirs(processed_dir_path, exist_ok=True)

    _data_record(rawdata_index, files_info, processed_dir_path)

    utc_now: datetime = datetime.utcnow()

    ElasticManager.create_doc(
        index=events_index, doc_id=2, query={"event_id": 2, "event_type": "stop", "occurred_time": utc_now}
    )

    ElasticManager.create_doc(
        index=events_index, doc_id=3, query={"event_id": 3, "event_type": "recorded", "occurred_time": utc_now},
    )

    logger.info("manual import finished.")


if __name__ == "__main__":
    LOG_FILE: Final[str] = os.path.join(
        common.get_config_value(common.APP_CONFIG_PATH, "log_dir"), "data_recorder/data_recorder.log"
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.handlers.RotatingFileHandler(
                LOG_FILE, maxBytes=common.MAX_LOG_SIZE, backupCount=common.BACKUP_COUNT
            ),
            logging.StreamHandler(),
        ],
    )

    MODE: Final[str] = os.environ.get("DATA_RECORDER_MODE", "TEST")

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="set import directory (manual import)")
    args = parser.parse_args()

    if args.dir is None:
        main()

    else:
        if not os.path.isdir(args.dir):
            logger.error(f"{args.dir} is not exists.")
            sys.exit(1)
        manual_record(args.dir)

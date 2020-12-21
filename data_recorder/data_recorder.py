from datetime import datetime
import os
import sys
import json
import glob
import shutil
import logging
import logging.handlers
from typing import Final

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


def record() -> None:
    """ """
    shared_dir = "data/pseudo_data/"

    files: list = glob.glob(shared_dir + "*.dat")
    if len(files) == 0:
        return
    files.sort()

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

    # 作成したファイルリストと、start-endtimeを比較し、start-endに含まれるファイルのみにフィルターする
    # 含まれないファイルは削除する

    # 区間に含まれるファイルがなければreturn
    # あればそのstarttimeを名前とするディレクトリを作成し、そこにファイルを退避

    # 退避したファイルを1つずつ読み込み
    # バイナリをデコードしてセンサーデータ読み取り
    # 先頭行の時刻=ファイル名であるはずなので、その時刻を設定
    # 行ごとにサンプリングレートから換算される時間を加算
    # rawdata_indexおよびcsvに出力する


def main():
    record()


if __name__ == "__main__":
    main()

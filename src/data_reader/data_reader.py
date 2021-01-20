from typing import Final, List
from datetime import datetime
from pandas.core.frame import DataFrame
import os
import sys
import logging
import logging.handlers
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
from time_logger import time_log
import common

LOG_FILE: Final[str] = os.path.join(
    common.get_config_value(common.APP_CONFIG_PATH, "log_dir"), "data_reader/data_reader.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=common.MAX_LOG_SIZE, backupCount=common.BACKUP_COUNT),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class DataReader:
    def read_shot(self, index: str, shot_number: int) -> DataFrame:
        """ 特定ショットのデータを取得し、連番の昇順にソートして返却する """

        query: dict = {"query": {"term": {"shot_number": {"value": shot_number}}}}

        result: List[dict] = ElasticManager.get_docs(index=index, query=query)
        result.sort(key=lambda x: x["sequential_number"])

        df: DataFrame = pd.DataFrame(result)
        return df

    @time_log
    def read_all(self, index: str) -> DataFrame:
        """ 全件取得し、連番の昇順ソート結果を返す """

        logger.info("データを全件取得します。データ件数が多い場合、長時間かかる場合があります。")

        num_of_data: int = ElasticManager.count(index=index)

        logger.info(f"データ件数: {num_of_data}")

        result: List[dict] = ElasticManager.multi_process_range_scan(
            index=index, num_of_data=num_of_data, num_of_process=28
        )
        result.sort(key=lambda x: x["sequential_number"])

        logger.info("Data reading has finished.")

        df: DataFrame = pd.DataFrame(result)
        return df

    def read_shots_meta(self, index: str) -> DataFrame:
        """ メタデータを取得する """

        query: dict = {"sort": {"shot_number": {"order": "asc"}}}
        result: List[dict] = ElasticManager.get_docs(index=index, query=query)

        df: DataFrame = pd.DataFrame(result)
        return df


def main():
    data_reader = DataReader()
    data_reader.read_all("shots-20201201010000")


if __name__ == "__main__":
    main()


import os
import shutil
from backend.app.models.data_collect_history import DataCollectHistory
from backend.common import common
from datetime import datetime, timedelta
from backend.common.common_logger import logger
from backend.elastic_manager.elastic_manager import ElasticManager


class DataCollectHistoryService:
    @staticmethod
    def get_target(history: DataCollectHistory) -> str:
        """機器ID-収集日時の文字列を返す"""

        # UTCのDatetimeからJSTのYYYYMMDDhhmmss文字列に変換
        jst_started_at: datetime = history.started_at + timedelta(hours=9)
        target_date_str: str = datetime.strftime(jst_started_at, "%Y%m%d%H%M%S")
        target: str = history.machine_id + "-" + target_date_str

        return target

    @staticmethod
    def delete_data_directory(target: str):
        """対象となるデータディレクトリを削除"""

        data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")
        data_full_path: str = os.path.join(data_dir, target)

        if os.path.exists(data_full_path):
            shutil.rmtree(data_full_path)
            logger.info(f"{data_full_path} was deleted.")

    @staticmethod
    def delete_elastic_index(target: str):
        """対象となるElasticsearchインデックスを削除"""

        target_indicies = (
            "events-" + target,
            "rawdata-" + target,
            "shots-" + target + "-data",
            "shots-" + target + "-meta",
            "shots-" + target + "-start-point",
            "shots-" + target + "-max-point",
            "shots-" + target + "-break-point",
            "shots-" + target + "-start-break-diff",
        )

        for target_index in target_indicies:
            ElasticManager.delete_exists_index(target_index)

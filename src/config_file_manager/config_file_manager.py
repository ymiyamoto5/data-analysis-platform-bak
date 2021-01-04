import os
import sys
import json
import logging
from typing import Tuple, Optional, Union

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import common

logger = logging.getLogger(__name__)


class ConfigFileManager:
    def __init__(self, app_config_path: str = None):
        """ app_config.jsonからconfigファイルのパスを取得 """

        if app_config_path is None:
            app_config_path = "app_config.json"

        self.config_file_path = common.get_config_value(app_config_path, "config_file_path")

    def config_exists(self) -> bool:
        """ configファイルの存在確認 """

        return os.path.isfile(self.config_file_path)

    def create(self, initial_config_path: Optional[str] = None) -> bool:
        """ configファイル作成 """

        logger.info("Creating config file.")

        if initial_config_path is None:
            initial_config_path: str = os.path.dirname(__file__) + "/initial_config.json"

        try:
            initial_config: dict = self._read_config(initial_config_path)
        except Exception:
            return False

        successful: bool = self._dump_config_file(initial_config)

        if not successful:
            return successful

        logger.info("Finished creating config file.")

        return successful

    def update(self, params: dict) -> bool:
        """ 既存のconfigファイルを更新 """

        logger.info("Updating config file.")

        try:
            new_config: dict = self._read_config(self.config_file_path)
        except Exception:
            return False

        # C言語のint上限値に達したら0クリア
        if new_config["sequence_number"] == 2_147_483_647:
            new_config["sequence_number"] = 0
        new_config["sequence_number"] = new_config["sequence_number"] + 1

        # NOTE: 現状のUIから変更される可能性があるパラメータは以下の3つのみ。
        if "status" in params:
            new_config["status"] = params["status"]
        if "start_time" in params:
            new_config["start_time"] = params["start_time"]
        if "end_time" in params:
            new_config["end_time"] = params["end_time"]

        successful: bool = self._dump_config_file(new_config)

        logger.info("Finished updating config file.")

        return successful

    def _read_config(self, config_file_path) -> Union[dict, FileNotFoundError, Exception]:
        """ configファイルを読み取り、dictで返す """

        try:
            with open(config_file_path, "r") as f:
                current_config: dict = json.load(f)
                return current_config
        except FileNotFoundError as e:
            logger.exception(str(e))
            raise FileNotFoundError
        except Exception as e:
            logger.exception(str(e))
            raise e

    def _dump_config_file(self, config: dict) -> bool:
        """ configファイルに吐き出す """

        path_ext_pair: Tuple[str, str] = os.path.splitext(self.config_file_path)
        tmp_file_path: str = path_ext_pair[0] + ".tmp"

        config_str: str = json.dumps(config, indent=2, ensure_ascii=False)

        # ファイル生成途中で読み込まれないよう、tmpファイルに出力した後にリネーム
        try:
            with open(tmp_file_path, mode="w") as f:
                f.write(config_str)
        except Exception as e:
            logger.exception(str(e))
            return False

        file_path: str = path_ext_pair[0] + ".cnf"
        try:
            os.rename(tmp_file_path, file_path)
            return True
        except OSError as e:
            logger.exception(str(e))
            return False

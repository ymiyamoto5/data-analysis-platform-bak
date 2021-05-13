"""
 ==================================
  config_file_manager.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import os
import sys
import json
import logging
import fcntl
from typing import Tuple, Optional, Union

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import common

logger = logging.getLogger(__name__)


class ConfigFileManager:
    def __init__(self, app_config_path: str = None):
        """ app_config.jsonからconfigファイルのパスを取得 """

        app_config_path: str = common.APP_CONFIG_PATH if app_config_path is None else app_config_path

        self.config_file_path = common.get_config_value(app_config_path, "config_file_path")

    def config_exists(self) -> bool:
        """ configファイルの存在確認 """

        return os.path.isfile(self.config_file_path)

    def create(self, initial_config_path: Optional[str] = None) -> bool:
        """ configファイル作成 """

        logger.info("Creating config file.")

        if initial_config_path is None:
            initial_config_path: str = common.get_config_value(common.APP_CONFIG_PATH, "initial_config_file_path")

        try:
            initial_config: dict = self.read_config(initial_config_path)
        except Exception:
            logger.exception("Initial config file not found.")
            return False

        successful: bool = self._dump_config_file(initial_config)

        if not successful:
            return successful

        logger.info("Finished creating config file.")

        return successful

    def update(self, params: dict) -> bool:
        """ 既存のconfigファイルを更新 """

        logger.info(f"Updating config file. Params: {params}")

        try:
            new_config: dict = self.read_config()
        except Exception:
            return False

        # C言語のint上限値に達したら0クリア
        if new_config["sequence_number"] == 2_147_483_647:
            new_config["sequence_number"] = 0
        new_config["sequence_number"] = new_config["sequence_number"] + 1

        # NOTE: 現状のUIから変更される可能性があるパラメータはstatusのみ。
        if "status" in params:
            new_config["status"] = params["status"]

        successful: bool = self._dump_config_file(new_config)

        logger.info("Finished updating config file.")

        return successful

    def read_config(self, config_file_path: str = None) -> Union[dict, FileNotFoundError, Exception]:
        """ configファイルを読み取り、dictで返す """

        if config_file_path is None:
            config_file_path: str = self.config_file_path

        try:
            with open(config_file_path, "r") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    current_config: dict = json.load(f)
                    return current_config
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except FileNotFoundError as e:
            logger.exception(str(e))
            raise FileNotFoundError
        except Exception as e:
            logger.exception(str(e))
            raise Exception

    def _dump_config_file(self, config: dict) -> bool:
        """ configファイルに吐き出す """

        config_str: str = json.dumps(config, indent=2, ensure_ascii=False)

        # 排他ロックを確保して書き込み
        try:
            with open(self.config_file_path, "w") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.write(config_str)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    return True
        except FileNotFoundError as e:
            logger.exception(str(e))
            raise FileNotFoundError
        except Exception as e:
            logger.exception(str(e))
            raise Exception

import os
import json
from typing import Tuple

from data_collect_manager import app


class ConfigFileManager:
    def __init__(self, app_config_path: str = None):
        """ app_config.jsonからconfigファイルのパスを取得 """

        if app_config_path is None:
            app_config_path = os.path.dirname(__file__) + "/../../common/app_config.json"

        with open(app_config_path, "r") as f:
            settings: dict = json.load(f)
            self.config_file_path = settings["config_file_path"]

    def config_exists(self) -> bool:
        """ configファイルの存在確認 """

        return os.path.isfile(self.config_file_path)

    def create(self) -> bool:
        """ configファイル作成 """

        app.logger.info("Creating config file.")

        initial_config_path = os.path.dirname(__file__) + "/initial_config.json"
        with open(initial_config_path, "r") as f:
            initial_config: dict = json.load(f)

        successful: bool = self._dump_config_file(initial_config)

        if not successful:
            return successful

        app.logger.info("Finished creating config file.")

        return successful

    def update(self, params: dict, should_change_sequence: bool = False) -> bool:
        """ 既存のconfigファイルを更新 """

        app.logger.info("Updating config file.")

        new_config: dict = self.read_config()

        if should_change_sequence:
            new_config["sequence_number"] = int(new_config["sequence_number"]) + 1

        # TODO: すべてのパラメータを再設定
        if "status" in params:
            new_config["status"] = params["status"]
        if "start_time" in params:
            new_config["start_time"] = params["start_time"]
        if "end_time" in params:
            new_config["end_time"] = params["end_time"]

        successful: bool = self._dump_config_file(new_config)

        app.logger.info("Finished updating config file.")

        return successful

    def read_config(self):
        with open(self.config_file_path, "r") as f:
            try:
                current_config: dict = json.load(f)
                return current_config
            except json.decoder.JSONDecodeError as e:
                app.logger.error(str(e))

    def _dump_config_file(self, config: dict) -> bool:
        """ configファイルに吐き出す """

        path_ext_pair: Tuple[str, str] = os.path.splitext(self.config_file_path)
        tmp_file_path: str = path_ext_pair[0] + ".tmp"

        config_str: str = json.dumps(config, indent=2, ensure_ascii=False)

        # ファイル生成途中で読み込まれないよう、tmpファイルに出力した後にリネーム
        with open(tmp_file_path, mode="w") as f:
            f.write(config_str)

        file_path: str = path_ext_pair[0] + ".cnf"
        try:
            os.rename(tmp_file_path, file_path)
            return True
        except OSError as e:
            app.logger.error(str(e))
            return False

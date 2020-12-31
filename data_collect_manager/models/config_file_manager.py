import os
import json
from typing import Tuple

from data_collect_manager import app


class ConfigFileManager:
    def __init__(self, file_path: str = None):
        if file_path is None:
            settings_file_path = os.path.dirname(__file__) + "/../../common/app_config.json"
            with open(settings_file_path, "r") as f:
                settings: dict = json.load(f)
                self.file_path = settings["config_file_path"]
        else:
            self.file_path = file_path

    def config_exists(self) -> bool:
        """ configファイルの存在確認 """
        return os.path.isfile(self.file_path)

    def create(self) -> bool:
        """ configファイル作成 """

        app.logger.info("Creating config file.")

        initial_config_path = os.path.dirname(__file__) + "/initial_config.json"
        with open(initial_config_path, "r") as f:
            initial_config: dict = json.load(f)

        config_json_str: str = self.__create_json_str(initial_config)
        successful: bool = self.__dump_config_file(config_json_str)

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

        new_config_json: str = self.__create_json_str(new_config)
        successful: bool = self.__dump_config_file(new_config_json)

        app.logger.info("Finished updating config file.")

        return successful

    def read_config(self):
        with open(self.file_path, "r") as f:
            try:
                current_config: dict = json.load(f)
                return current_config
            except json.decoder.JSONDecodeError as e:
                app.logger.error(str(e))

    def __create_json_str(self, config) -> str:
        """ JSONフォーマットのstringに変換 """

        return json.dumps(config, indent=2, ensure_ascii=False)

    def __dump_config_file(self, config) -> bool:
        """ configファイルに吐き出す """

        path_ext_pair: Tuple = os.path.splitext(self.file_path)
        tmp_file_path: str = path_ext_pair[0] + ".tmp"

        # ファイル生成途中で読み込まれないよう、tmpファイルに出力した後にリネーム
        with open(tmp_file_path, mode="w") as f:
            f.write(config)

        file_path: str = path_ext_pair[0] + ".cnf"
        try:
            os.rename(tmp_file_path, file_path)
            return True
        except OSError as e:
            app.logger.error(str(e))
            return False

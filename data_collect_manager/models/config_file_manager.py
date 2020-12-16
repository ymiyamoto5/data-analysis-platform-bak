import os
import json
from typing import Tuple

from data_collect_manager import app


class ConfigFileManager:
    def __init__(self, file_path: str = None):
        if file_path is None:
            # TODO: ファイルパス設定
            self.file_path = "/home/ymiyamoto5/shared/conf_Gw-00.cnf"
        else:
            self.file_path = file_path

    def is_running(self) -> bool:
        """ configファイルがあればステータスを確認し、runningであればTrueを返す """

        if os.path.isfile(self.file_path):
            with open(self.file_path, "r") as f:
                try:
                    current_config = json.load(f)
                except json.decoder.JSONDecodeError:
                    return False
            is_started: bool = current_config["status"] == "running"
            return is_started

    def init_config(self, params: dict = None) -> bool:
        """ configファイルがすでにあればupdate、なければcreate """

        if os.path.isfile(self.file_path):
            successful: bool = self.update(params)
            return successful
        else:
            successful: bool = self.create(params)
            return successful

    def create(self, params: dict) -> bool:
        """ configファイル作成 """

        app.logger.info("Creating config file.")

        initial_config: dict = {
            "sequence_number": 1,
            "gateway_result": 0,
            "status": params["status"],
            "gateway_id": "Gw-00",
            "Log_Level": 5,
            "ADC_0": {
                "handler_id": "AD-00",
                "handler_type": "USB_1608HS",
                "ADC_SerialNum": "01234567",
                "sampling_frequency": 100000,
                "sampling_chnum": 5,
                "filewrite_time": 3600,
            },
            "meta_index": params["meta_index"],
        }

        config_json_str: str = self.__create_json_str(initial_config)
        successful: bool = self.__dump_config_file(config_json_str)

        if not successful:
            return successful

        app.logger.info("Finished creating config file.")

        return successful

    def update(self, params) -> bool:
        """ 既存のconfigファイルを更新 """

        app.logger.info("Updating config file.")

        new_config: dict = self.read_config()

        # TODO: すべてのパラメータを再設定
        new_config["sequence_number"] = int(new_config["sequence_number"]) + 1

        if "status" in params:
            new_config["status"] = params["status"]
        if "meta_index" in params:
            new_config["meta_index"] = params["meta_index"]

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

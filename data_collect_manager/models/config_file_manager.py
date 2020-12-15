import os
import json
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
            is_success: bool = self.update(params)
            return is_success
        else:
            is_success: bool = self.create()
            return is_success

    def create(self) -> bool:
        """ configファイル作成 """

        app.logger.info("Creating config file.")

        initial_config: dict = {
            "sequence_number": 1,
            "gateway_result": 0,
            "status": "running",
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
        }

        config_json_str: str = self.__create_json_str(initial_config)
        is_success: bool = self.__dump_config_file(config_json_str)

        app.logger.info("Finished creating config file.")

        return is_success

    def update(self, params) -> bool:
        """ 既存のconfigファイルを更新 """

        app.logger.info("Updating config file.")

        with open(self.file_path, "r") as f:
            try:
                current_config = json.load(f)
            except json.decoder.JSONDecodeError:
                return False

        new_config: dict = current_config

        new_config["sequence_number"] = int(current_config["sequence_number"]) + 1
        new_config["status"] = params["status"]

        new_config_json: str = self.__create_json_str(new_config)
        is_success: bool = self.__dump_config_file(new_config_json)

        app.logger.info("Finished updating config file.")

        return is_success

    def __create_json_str(self, config) -> str:
        """ JSONフォーマットのstringに変換 """

        return json.dumps(config, indent=2, ensure_ascii=False)

    def __dump_config_file(self, config) -> bool:
        """ configファイルに吐き出す """

        path_ext_pair = os.path.splitext(self.file_path)
        tmp_file_path = path_ext_pair[0] + ".tmp"

        # ファイル生成途中で読み込まれないよう、tmpファイルに出力した後にリネーム
        with open(tmp_file_path, mode="w") as f:
            f.write(config)

        file_path = path_ext_pair[0] + ".cnf"
        try:
            os.rename(tmp_file_path, file_path)
            return True
        except OSError as e:
            app.logger.error(str(e))
            return False

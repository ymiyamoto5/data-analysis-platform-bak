import os
import json


class ConfigFileManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def check_file_exists(self) -> bool:
        return os.path.isfile(self.file_path)

    def create(self) -> bool:
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

        file_dir = "~/shared/"
        tmp_file_path = file_dir + self.file_path + ".tmp"

        # ファイル生成途中で読み込まれないよう、tmpファイルに出力した後にリネーム
        with open(tmp_file_path, mode="w") as f:
            f.write(config_json_str)

        file_path = file_dir + self.file_path + ".json"
        os.rename(tmp_file_path, file_path)

    def update(self, update_params):
        with open(self.file_path, "r") as f:
            current_config = json.load(f)

        new_config: dict = {
            "sequence_number": int(current_config["sequence_number"]) + 1,
            "gateway_result": update_params["gateway_result"],
            "status": update_params["status"],
            "gateway_id": update_params["gateway_id"],
            "Log_Level": update_params["Log_Level"],
        }
        # "ADC_0": {
        #     "handler_id": "AD-00",
        #     "handler_type": "USB_1608HS",
        #     "ADC_SerialNum": "01234567",
        #     "sampling_frequency": 100000,
        #     "sampling_chnum": 5,
        #     "filewrite_time": 3600,
        # },

        self.__create_json_str(new_config)

    def __create_json_str(self, config) -> str:
        return json.dumps(config, indent=2, ensure_ascii=False)

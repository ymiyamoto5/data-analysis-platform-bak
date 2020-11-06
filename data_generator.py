import os
import time
import numpy as np
import json
from datetime import datetime
from pytz import timezone


def main():
    n = 50
    x, y = generate_sin_data(n)

    abnormal_y = create_abnormal_data(y)

    # 1秒毎に1データをJSONに変換し、ファイル出力
    for i, data in enumerate(abnormal_y):
        utc_now = datetime.now(timezone('UTC'))
        json_str = create_json_str(data, utc_now)

        file_dir = "data/"
        os.makedirs(file_dir + "processed", exist_ok=True)

        utc_now = utc_now.strftime("%Y%m%d%H%M%S")
        tmp_file_path = file_dir + utc_now + ".tmp"

        # ファイル生成途中で読み込まれないよう、tmpファイルに出力した後にリネーム
        with open(tmp_file_path, mode="w") as f:
            f.write(json_str)

        file_path = file_dir + utc_now + ".json"
        os.rename(tmp_file_path, file_path)

        print(f"{i + 1} data generated")
        time.sleep(1)


def create_json_str(data: float, timestamp: datetime) -> str:
    ''' ダミーデータのJSON文字列の生成 '''
    json_data = {
        "molding_machine_name": "テスト成形機",
        "mold_name": "テスト金型",
        "material_name": "テスト材料",
        "timestamp": timestamp.isoformat(),
        "displacement": data
    }

    return json.dumps(json_data, indent=2, ensure_ascii=False)


def generate_sin_data(n: int) -> None:
    ''' 正弦波データを生成 '''
    x = np.linspace(0, 2*np.pi, n)
    y = np.sin(x)

    return x, y


def create_abnormal_data(y: np.array) -> np.array:
    ''' 異常データを生成。配列の最後の5個を0にする '''
    abnormal_y = []
    for i, v in enumerate(y):
        if i <= len(y) - 6:
            abnormal_y.append(v)
        else:
            abnormal_y.append(0)

    return abnormal_y


if __name__ == '__main__':
    main()

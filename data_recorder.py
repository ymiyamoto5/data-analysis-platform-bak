import json
import glob
import shutil
from datetime import datetime
from backend.models.es_wrapper import ElasticsearchWrapper


def data_record():
    '''
     センサーデータ(JSONファイル)を監視し、ファイルがあればElasticsearchに保存
     TODO: ファイル監視実装（https://qiita.com/ksato9700/items/ea4b769d010e8cf1fb0c）
    '''

    # TODO: 共通の定数はコンフィグファイルから読み取る
    SENSOR_DATA_INDEX = "sensor-data"
    es = ElasticsearchWrapper()
    es.create_index(index=SENSOR_DATA_INDEX)

    while True:
        file_list = glob.glob("data/*.json")
        file_list.sort()

        for file in file_list:
            with open(file) as f:
                json_obj = json.load(f)

                json_obj['timestamp'] = datetime.fromisoformat(json_obj['timestamp'])
                es.create(index=SENSOR_DATA_INDEX, data=json_obj)

            # 処理したファイルは退避
            shutil.move(file, "data/processed/")

            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{now}] {file} was processed")


if __name__ == '__main__':
    data_record()

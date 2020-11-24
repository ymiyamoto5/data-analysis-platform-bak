import os
import json
from typing import Iterable, Tuple
from elasticsearch import helpers
from csv import DictReader
from datetime import datetime, timezone, timedelta
from elastic_manager import ElasticManager
from time_logger import time_log

# datetime取得時に日本時間を指定する
JST = timezone(timedelta(hours=+9), 'JST')


class DataImporter:
    """
     データインポートクラス
     現状は from csv to Elasticsearch のみ実装

     TODO:
           from elasticsearch(生データ) to elasticsearch処理追加
           meta_index作成
           並列処理化
    """

    @time_log
    def import_raw_data(self, data_to_import: str, index_to_import: str) -> None:
        """ rawデータインポート処理 """

        ElasticManager.delete_exists_index(index=index_to_import)
        ElasticManager.create_index(index=index_to_import)

        ElasticManager.parallel_bulk(
            doc_generator=self.__doc_generator(data_to_import, index_to_import),
            data_to_import=data_to_import,
            index_to_import=index_to_import,
            thread_count=2,
            chunk_size=5000)

    @time_log
    def import_data_by_shot(
            self,
            rawdata_index: str,
            shots_index: str,
            start_displacement: float,
            end_displacement: float,
            start_seq_num: int):
        """
         データインポート処理(変位値に応じてshot切り出し)
        """

        # ☆並列実行のため一時的にコメントアウト
        ElasticManager.delete_exists_index(index=shots_index)
        ElasticManager.create_index(index=shots_index)

        # TODO: マルチプロセス化
        # 生データを取得（ジェネレータ）
        raw_data_gen: Iterable = ElasticManager.scan(index=rawdata_index)

        PROCESS_COUNT: int = 4
        # ショット切り出し
        shot_data: list = self.__cut_out_shot(raw_data_gen, start_displacement, end_displacement)

        # データをプロセスの数に分割
        splitted_data_list = self.__split_data(shot_data, num_of_split=PROCESS_COUNT)

        for data_list in splitted_data_list:
            print(len(data_list))

        # ここからマルチプロセス

        ElasticManager.parallel_bulk(
            doc_generator=self._doc_generator_by_shot(
                rawdata_index, shots_index, start_displacement, end_displacement, start_seq_num),
            data_to_import=rawdata_index,
            index_to_import=shots_index,
            thread_count=2,
            chunk_size=5000)

    def __doc_generator(self, csv_file: str, index_name: str) -> dict:
        """ csv を読み込んで一行ずつ辞書型で返すジェネレータ

        TODO:
            csv_file読み込みからpcmファイル読み込みに変更する
        """

        DISPLAY_THROUGHPUT_DOC_NUM = 100000

        with open(csv_file, "rt", encoding="utf-8") as file:
            reader = DictReader(file, fieldnames=[
                                "#EndHeader", "日時(μs)", "time(μs）", "(3)HA-V01", "(3)HA-V02", "(3)HA-V03", "(3)HA-V04", "(3)HA-C01"])
            _ = next(reader)

            dt_now = datetime.now(JST)

            for i, row in enumerate(reader):
                if i % DISPLAY_THROUGHPUT_DOC_NUM == 0:
                    self.__throughput_counter(i, dt_now)

                wave = {
                    "sequential_number": i,
                    "load01": float(row["(3)HA-V01"]),
                    "load02": float(row["(3)HA-V02"]),
                    "load03": float(row["(3)HA-V03"]),
                    "load04": float(row["(3)HA-V04"]),
                    "displacement": float(row["(3)HA-C01"])
                }

                yield {
                    "_index": index_name,
                    "_id": wave["sequential_number"],
                    "_source": wave
                }

    @time_log
    def __cut_out_shot(self, raw_data: Iterable, start_displacement: float, end_displacement: float) -> list:
        """
        ショット切り出し処理。生データの変位値を参照し、ショット対象となるデータのみをリストに含めて返す。
        メモリ上に展開するため、データ量に要注意。

        Args:
            raw_data: 生データ
            start_displacement: ショット開始となる変位値
            end_displacement: ショット終了となる変位値

        Returns:
            list: ショットデータのリスト
        """

        dt_now = datetime.now(JST)

        is_shot_start: bool = False
        sequential_number: int = 0
        sequential_number_by_shot: int = 0
        shot_number: int = 0
        inserted_count: int = 0  # Thoughput算出用
        shots: list = []

        for data in raw_data:
            if inserted_count % 100000 == 0 and inserted_count != 0:
                self.__throughput_counter(inserted_count, dt_now)

            load = data['_source']['load']
            displacement = data['_source']['displacement']

            # ショット開始判定
            if (not is_shot_start) and (displacement >= start_displacement):
                is_shot_start = True
                shot_number += 1
                sequential_number_by_shot = 0

            if not is_shot_start:
                continue

            shot = {
                "sequential_number": sequential_number,
                "sequential_number_by_shot": sequential_number_by_shot,
                "load": load,
                "displacement": displacement,
                "shot_number": shot_number
            }

            shots.append(shot)

            # shotの終了
            if displacement <= end_displacement:
                is_shot_start = False
                sequential_number_by_shot = 0

            sequential_number += 1
            sequential_number_by_shot += 1
            inserted_count += 1

        return shots

    def _split_data(self, shot_data: list, num_of_split: int) -> list:
        """
            マルチプロセスで実行するために、ショットデータをプロセスの数に分割する

            args:
                shot_data: ショットデータ
                num_of_split: 分割数

            returns:
                list: 分割されたデータを要素として持つリスト
        """

        print(f"分割前データ数{len(shot_data)}")

        batch_size, mod = divmod(len(shot_data), num_of_split)
        splitted_data_list: list = []

        # ex) [a, b, c, d, e, f, g] を3分割 => [[a, b],[c, d], [e, f, g]]
        for i in range(num_of_split):
            start_index: int = i * batch_size
            splitted_data: list = shot_data[start_index:start_index + batch_size]
            splitted_data_list.append(splitted_data)

        # 余りを一番最後のリストに追加
        mod_start_index: int = num_of_split * batch_size
        mod_list = shot_data[mod_start_index:]
        for x in mod_list:
            splitted_data_list[-1].append(x)

        return splitted_data_list

    def __doc_generator_by_shot(
        self,
        rawdata_index: str,
        shots_index: str
    ) -> dict:
        pass

    def _doc_generator_by_shot(
            self,
            csv_file: str,
            index_name: str,
            start_displacement: float,
            end_displacement: float,
            start_seq_num: int) -> dict:
        '''
         csvを読み込み、shot切り出し後のデータのみ返却するジェネレーター（廃止予定）

        '''

        with open('notebooks/wave1-15-5ch-3.csv', "rt", encoding="utf-8") as file:
            reader = DictReader(file, fieldnames=[
                                "#EndHeader", "日時(μs)", "time(μs）", "(3)HA-V01", "(3)HA-V02", "(3)HA-V03", "(3)HA-V04", "(3)HA-C01"])

            _ = next(reader)

            dt_old = datetime.now(JST)

            is_shot_start = False
            sequential_number = 0
            sequential_number_by_shot = 0
            shot_number = 0
            inserted_count = 0  # Thoughput算出用

            for row in reader:
                if inserted_count % 100000 == 0 and inserted_count != 0:
                    self.__throughput_counter(inserted_count, dt_old)

                displacement = float(row["(3)HA-C01"])

                # ショット開始判定
                if (not is_shot_start) and (displacement >= start_displacement):
                    is_shot_start = True
                    shot_number += 1
                    sequential_number_by_shot = 0

                if not is_shot_start:
                    continue

                shot = {
                    "sequential_number": sequential_number + start_seq_num,
                    "sequential_number_by_shot": sequential_number_by_shot,
                    "load01": float(row["(3)HA-V01"]),
                    "load02": float(row["(3)HA-V02"]),
                    "load03": float(row["(3)HA-V03"]),
                    "load04": float(row["(3)HA-V04"]),
                    "displacement": displacement,
                    "shot_number": shot_number,
                    "tags": []
                }

                # テスト用アドホック処理
                if 3000 <= sequential_number <= 30000:
                    shot["tags"].append("プレス機異常")
                if 20000 <= sequential_number <= 50000:
                    shot["tags"].append("センサーに異常が発生")

                yield {
                    "_index": index_name,
                    "_id": shot["sequential_number"],
                    "_source": shot
                }

                # shotの終了
                if displacement <= end_displacement:
                    is_shot_start = False
                    sequential_number_by_shot = 0

                sequential_number += 1
                sequential_number_by_shot += 1
                inserted_count += 1

    def __throughput_counter(self, processed_count: int, dt_old: datetime) -> None:
        """ スループットの表示 """

        dt_now = datetime.now(JST)
        dt_delta = dt_now - dt_old
        total_sec = dt_delta.total_seconds()
        throughput = processed_count / total_sec

        print(f"{dt_now}, processed_count: {processed_count}, throughput: {throughput}")


if __name__ == '__main__':
    ''' スクリプト直接実行時はテスト用インデックスにインポートする '''
    print(os.getcwd())
    data_importer = DataImporter()
    data_importer.import_raw_data('notebooks/wave1-15-5ch-3.csv', 'rawdata-test')
    # data_importer.import_data_by_shot('rawdata-test', 'shots-test', -15, -17, 0)

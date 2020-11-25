import os
from typing import Iterable, Iterator
from csv import DictReader
from datetime import datetime, timezone, timedelta
from itertools import islice, tee
from more_itertools import ilen
from elastic_manager import ElasticManager
from time_logger import time_log

# datetime取得時に日本時間を指定する
JST = timezone(timedelta(hours=+9), 'JST')


class DataImporter:
    """
     データインポートクラス

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
    def import_data_by_shot(self, rawdata_index: str, shots_index: str, start_displacement: float,
                            end_displacement: float, num_of_process: int = 4):
        """ shotデータインポート処理 """

        ElasticManager.delete_exists_index(index=shots_index)
        ElasticManager.create_index(index=shots_index)

        # rawデータを取得するジェネレータ
        raw_data_gen: Iterator = ElasticManager.scan(index=rawdata_index)

        # ショット切り出し
        shot_data: list = self._cut_out_shot(raw_data_gen, start_displacement, end_displacement)

        # データをプロセスの数に分割し、ジェネレーターのリストにする。
        # shot_data_list = self._create_splitted_data_gen(shot_data, num_of_split=num_of_process)

        # マルチプロセスでデータ投入
        ElasticManager.multi_process_bulk(
            shot_data=shot_data,
            index_to_import=shots_index,
            num_of_process=num_of_process,
            chunk_size=5000
        )

    def __doc_generator(self, csv_file: str, index_name: str) -> Iterator:
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

    def _cut_out_shot(self, raw_data: Iterable, start_displacement: float, end_displacement: float) -> Iterator:
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
        print(f"{dt_now} cut_off start.")

        DISPLAY_THROUGHPUT_DOC_NUM = 100000

        is_shot_start: bool = False
        sequential_number: int = 0
        sequential_number_by_shot: int = 0
        shot_number: int = 0
        inserted_count: int = 0  # Thoughput算出用
        shots: list = []

        for data in raw_data:
            if inserted_count % DISPLAY_THROUGHPUT_DOC_NUM == 0 and inserted_count != 0:
                self.__throughput_counter(inserted_count, dt_now)

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
                "load01": data['_source']['load01'],
                "load02": data['_source']['load02'],
                "load03": data['_source']['load03'],
                "load04": data['_source']['load04'],
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

        print(f"{dt_now} cut_off finished.")

        return shots

    def _create_splitted_data_gen(self, shot_data_gen, num_of_split: int) -> list:
        """
            マルチプロセスで実行するために、ショットデータをプロセスの数に分割する
            ex) [a, b, c, d, e, f, g] を3分割 => [[a, b],[c, d], [e, f, g]]
            なお、メモリ節約のため、データそのものを返すのではなくジェネレータのリストを返す。

            args:
                shot_data_gen: ショットデータのジェネレーター
                num_of_split: 分割数

            returns:
                list: 分割されたデータのジェネレーターを要素として持つリスト
        """

        # NOTE: ilenでジェネレーターは一度データを取得してしまう。
        #       ジェネレーターは再利用できないので、再利用可能なようにteeでジェネレーターを複製しておく。
        gen, gen_backup = tee(shot_data_gen)

        # NOTE: ジェネレーターから件数を取得するため、ilenを利用
        num_of_data: int = ilen(gen)
        print(f"num_of_all：{num_of_data}")

        # 何個ずつのデータに分割するのか計算
        batch_size, mod = divmod(num_of_data, num_of_split)

        shot_data_gen_list: list = []

        # 最後のジェネレーターには余り分も含めるため、一つ手前まで生成
        for i in range(num_of_split - 1):
            start_index: int = i * batch_size
            end_index: int = start_index + batch_size
            shot_data_gen_list.append(islice(gen_backup, start_index, end_index))

        # 一番最後のジェネレーター
        start_index_of_last_gen: int = (num_of_split - 1) * batch_size
        shot_data_gen_list.append(islice(gen_backup, start_index_of_last_gen, None))

        return shot_data_gen_list

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
    # print(os.getcwd())
    data_importer = DataImporter()
    # data_importer.import_raw_data('notebooks/wave1-15-5ch-3.csv', 'rawdata-test')
    data_importer.import_data_by_shot('rawdata-test', 'shots-test', -15, -17, 4)

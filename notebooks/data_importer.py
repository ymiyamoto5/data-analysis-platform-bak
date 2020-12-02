from typing import Iterable, Iterator, Mapping
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
            thread_count=4,
            chunk_size=5000)

    @time_log
    def import_data_by_shot(self, rawdata_index: str, shots_index: str, start_displacement: float,
                            end_displacement: float, num_of_process: int = 4):
        """ shotデータインポート処理 """

        mapping_file = "notebooks/mapping_shots.json"
        # mapping_file = None

        ElasticManager.delete_exists_index(index=shots_index)
        ElasticManager.create_index(index=shots_index, mapping_file=mapping_file)

        self._cut_out_shot(rawdata_index, shots_index, start_displacement, end_displacement)

    def __doc_generator(self, csv_file: str, index_name: str) -> Iterator:
        """ csv を読み込んで一行ずつ辞書型で返すジェネレータ

        TODO:
            csv_file読み込みからpcmファイル読み込みに変更する
        """

        DISPLAY_THROUGHPUT_DOC_NUM = 100000

        with open(csv_file, "rt", encoding="utf-8") as file:
            reader = DictReader(file, fieldnames=["#EndHeader", "日時(μs)", "(2)HA-V01", "(2)HA-V02", "(2)HA-V03", "(2)HA-V04", "(2)HA-C01", "(2)HA-C02"])
            _ = next(reader)

            dt_now = datetime.now(JST)

            for i, row in enumerate(reader):
                if i % DISPLAY_THROUGHPUT_DOC_NUM == 0:
                    self.__throughput_counter(i, dt_now)

                wave = {
                    "sequential_number": i,
                    "load01": float(row["(2)HA-V01"]),
                    "load02": float(row["(2)HA-V02"]),
                    "load03": float(row["(2)HA-V03"]),
                    "load04": float(row["(2)HA-V04"]),
                    "displacement": float(row["(2)HA-C01"])
                }

                yield {
                    "_index": index_name,
                    "_id": wave["sequential_number"],
                    "_source": wave
                }

    @time_log
    def _cut_out_shot(self, rawdata_index: str, shots_index: str, start_displacement: float, end_displacement: float) -> None:
        """
        ショット切り出し処理。生データの変位値を参照し、ショット対象となるデータのみをリストに含めて返す。

        Args:
            raw_data: 生データ
            start_displacement: ショット開始となる変位値
            end_displacement: ショット終了となる変位値

        Returns:
            list: ショットデータのリスト
        """

        dt_now = datetime.now(JST)

        rawdata_count = ElasticManager.count(index=rawdata_index)

        # rawdataをN分割する。暫定で100。
        SPLIT_SIZE: int = 100
        batch_size, mod = divmod(rawdata_count, SPLIT_SIZE)

        is_shot_section: bool = False   # ショット内か否かを判別する
        is_target_of_cut_off: bool = False   # ショットの内、切り出し対象かを判別する
        sequential_number: int = 0
        sequential_number_by_shot: int = 0
        shot_number: int = 0
        inserted_count: int = 0  # Thoughput算出用
        shots: list = []

        # 分割した数だけループ
        for i in range(SPLIT_SIZE + 1):
            print(f"start batch number: {i + 1} / {SPLIT_SIZE + 1}")

            # batch_size分のデータをElasticsearchから取得する
            start_index = i * batch_size
            end_index = start_index + batch_size
            # 最後のループの場合、残った全てのデータを取得する
            if i == SPLIT_SIZE:
                end_index = rawdata_count + 1

            # rawdata_list = ElasticManager.range_scan(index=rawdata_index, start=start_index, end=end_index)
            rawdata_list = ElasticManager.multi_process_range_scan(index=rawdata_index, num_of_data=batch_size, start=start_index, end=end_index)

            # 分割されたものの中のデータ1件ずつ確認していく
            for rawdata in rawdata_list:
                # ショット開始判定
                if (not is_shot_section) and (rawdata['displacement'] <= start_displacement):
                    is_shot_section = True
                    is_target_of_cut_off = True
                    shot_number += 1
                    sequential_number_by_shot = 0

                    # N件遡ってshotsに加える。暫定で1000件。
                    # TODO: キャッシュ検討
                    previous_start_index = rawdata['sequential_number'] - 1000 if rawdata['sequential_number'] >= 1000 else 0
                    previous_end_index = rawdata['sequential_number']
                    previous_rawdata_list = ElasticManager.range_scan(index=rawdata_index, start=previous_start_index, end=previous_end_index)

                    for previous_rawdata in previous_rawdata_list:
                        shot: dict = {
                            "sequential_number": sequential_number,
                            "sequential_number_by_shot": sequential_number_by_shot,
                            "load01": previous_rawdata['load01'],
                            "load02": previous_rawdata['load02'],
                            "load03": previous_rawdata['load03'],
                            "load04": previous_rawdata['load04'],
                            "displacement": previous_rawdata['displacement'],
                            "shot_number": shot_number,
                            "tags": []
                        }
                        shots.append(shot)
                        sequential_number += 1
                        sequential_number_by_shot += 1

                # ショット区間の終了判定
                # 0.1（暫定値）はノイズの影響等で変位値が単調減少しなかった場合、ショット区間がすぐに終わってしまうことを防ぐためのバッファ
                if rawdata['displacement'] > start_displacement + 0.1:
                    is_shot_section = False

                # ショット未開始ならば後続は何もしない
                if not is_shot_section:
                    continue

                # 切り出し区間の終了判定
                if rawdata['displacement'] <= end_displacement:
                    is_target_of_cut_off = False
                    sequential_number_by_shot = 0

                # 切り出し区間に到達していなければ後続は何もしない
                if not is_target_of_cut_off:
                    continue

                sequential_number += 1
                sequential_number_by_shot += 1

                # 切り出し対象としてリストに加える
                shot = {
                    "sequential_number": sequential_number,
                    "sequential_number_by_shot": sequential_number_by_shot,
                    "load01": rawdata['load01'],
                    "load02": rawdata['load02'],
                    "load03": rawdata['load03'],
                    "load04": rawdata['load04'],
                    "displacement": rawdata['displacement'],
                    "shot_number": shot_number,
                    "tags": []
                }
                shots.append(shot)

                # ショットデータが一定件数（暫定で1,000,000）以上溜まったらElasticsearchに書き出す。
                if len(shots) >= 1_000_000:
                    ElasticManager.multi_process_bulk(shot_data=shots, index_to_import=shots_index, num_of_process=4, chunk_size=5000)
                    inserted_count += len(shots)
                    self.__throughput_counter(inserted_count, dt_now)
                    # print(f"Buffer was filled. Write to Elasticsearch {len(shots)} documents.")
                    shots = []

            # end of splitted rawdata loop
        # end of all rawdata loop

        # Elasticsearchに書き出されていないデータが残っていれば書き出す
        if len(shots) > 0:
            # 余りは少数のデータ、かつ分割プロセス数を下回る可能性があるので、シングルプロセスで実行
            ElasticManager.bulk_insert(shots, shots_index)
            inserted_count += len(shots)

        print(f"{dt_now} cut_off finished. {inserted_count} documents inserted.")

    def __throughput_counter(self, processed_count: int, dt_old: datetime) -> None:
        """ スループットの表示 """

        dt_now = datetime.now(JST)
        dt_delta = dt_now - dt_old
        total_sec = dt_delta.total_seconds()
        throughput = processed_count / total_sec

        print(f"{dt_now}, processed_count: {processed_count}, throughput: {throughput}")


if __name__ == '__main__':
    ''' スクリプト直接実行時はテスト用インデックスにインポートする '''
    data_importer = DataImporter()
    # data_importer.import_raw_data('notebooks/No11(25~30spm).CSV', 'rawdata-no11')
    # data_importer.import_raw_data('notebooks/No11_3000.csv', 'rawdata-no11-3000')
    # data_importer.import_data_by_shot('rawdata-no11', 'shots-no11', 47, 34, 4)
    data_importer.import_data_by_shot('rawdata-no11-3000', 'shots-no11-3000', 47, 34, 4)



##############################################

    # def _doc_generator_by_shot(
    #         self,
    #         csv_file: str,
    #         index_name: str,
    #         start_displacement: float,
    #         end_displacement: float,
    #         start_seq_num: int) -> dict:
    #     '''
    #      csvを読み込み、shot切り出し後のデータのみ返却するジェネレーター（廃止予定）
    #     '''

    #     with open('notebooks/wave1-15-5ch-3.csv', "rt", encoding="utf-8") as file:
    #         reader = DictReader(file, fieldnames=[
    #                             "#EndHeader", "日時(μs)", "time(μs）", "(3)HA-V01", "(3)HA-V02", "(3)HA-V03", "(3)HA-V04", "(3)HA-C01"])

    #         _ = next(reader)

    #         dt_old = datetime.now(JST)

    #         is_shot_start = False
    #         sequential_number = 0
    #         sequential_number_by_shot = 0
    #         shot_number = 0
    #         inserted_count = 0  # Thoughput算出用

    #         for row in reader:
    #             if inserted_count % 100000 == 0 and inserted_count != 0:
    #                 self.__throughput_counter(inserted_count, dt_old)

    #             displacement = float(row["(3)HA-C01"])

    #             # ショット開始判定
    #             if (not is_shot_start) and (displacement >= start_displacement):
    #                 is_shot_start = True
    #                 shot_number += 1
    #                 sequential_number_by_shot = 0

    #             if not is_shot_start:
    #                 continue

    #             shot = {
    #                 "sequential_number": sequential_number + start_seq_num,
    #                 "sequential_number_by_shot": sequential_number_by_shot,
    #                 "load01": float(row["(3)HA-V01"]),
    #                 "load02": float(row["(3)HA-V02"]),
    #                 "load03": float(row["(3)HA-V03"]),
    #                 "load04": float(row["(3)HA-V04"]),
    #                 "displacement": displacement,
    #                 "shot_number": shot_number,
    #                 "tags": []
    #             }

    #             # テスト用アドホック処理
    #             if 3000 <= sequential_number <= 30000:
    #                 shot["tags"].append("プレス機異常")
    #             if 20000 <= sequential_number <= 50000:
    #                 shot["tags"].append("センサーに異常が発生")

    #             yield {
    #                 "_index": index_name,
    #                 "_id": shot["sequential_number"],
    #                 "_source": shot
    #             }

    #             # shotの終了
    #             if displacement <= end_displacement:
    #                 is_shot_start = False
    #                 sequential_number_by_shot = 0

    #             sequential_number += 1
    #             sequential_number_by_shot += 1
    #             inserted_count += 1



    # def _create_splitted_data_gen(self, shot_data_gen, num_of_split: int) -> list:
    #     """
    #         マルチプロセスで実行するために、ショットデータをプロセスの数に分割する
    #         ex) [a, b, c, d, e, f, g] を3分割 => [[a, b],[c, d], [e, f, g]]
    #         なお、メモリ節約のため、データそのものを返すのではなくジェネレータのリストを返す。

    #         args:
    #             shot_data_gen: ショットデータのジェネレーター
    #             num_of_split: 分割数

    #         returns:
    #             list: 分割されたデータのジェネレーターを要素として持つリスト
    #     """

    #     # NOTE: ilenでジェネレーターは一度データを取得してしまう。
    #     #       ジェネレーターは再利用できないので、再利用可能なようにteeでジェネレーターを複製しておく。
    #     gen, gen_backup = tee(shot_data_gen)

    #     # NOTE: ジェネレーターから件数を取得するため、ilenを利用
    #     num_of_data: int = ilen(gen)
    #     print(f"num_of_all：{num_of_data}")

    #     # 何個ずつのデータに分割するのか計算
    #     batch_size, mod = divmod(num_of_data, num_of_split)

    #     shot_data_gen_list: list = []

    #     # 最後のジェネレーターには余り分も含めるため、一つ手前まで生成
    #     for i in range(num_of_split - 1):
    #         start_index: int = i * batch_size
    #         end_index: int = start_index + batch_size
    #         shot_data_gen_list.append(islice(gen_backup, start_index, end_index))

    #     # 一番最後のジェネレーター
    #     start_index_of_last_gen: int = (num_of_split - 1) * batch_size
    #     shot_data_gen_list.append(islice(gen_backup, start_index_of_last_gen, None))

    #     return shot_data_gen_list


            # 検証用のアドホック処理
            # if sequential_number == 1000:
            #     shot["is_load_starting_point_01"] = True
            # if sequential_number == 1001:
            #     shot["is_load_starting_point_02"] = True
            #     shot["is_load_starting_point_03"] = True
            # if sequential_number == 1002:
            #     shot["is_load_starting_point_04"] = True
            # if sequential_number == 40000:
            #     shot["is_load_starting_point_01"] = True
            #     shot["is_load_starting_point_02"] = True
            #     shot["is_load_starting_point_03"] = True
            #     shot["is_load_starting_point_04"] = True

            # if sequential_number == 2000 or sequential_number == 44000:
            #     shot["is_load_max_point_01"] = True
            #     shot["is_load_max_point_02"] = True
            #     shot["is_load_max_point_03"] = True
            #     shot["is_load_max_point_04"] = True

            # if sequential_number == 1500 or sequential_number == 42000:
            #     shot["is_load_break_point_01"] = True
            #     shot["is_load_break_point_02"] = True
            #     shot["is_load_break_point_03"] = True
            #     shot["is_load_break_point_04"] = True

from typing import Iterator
from csv import DictReader
from datetime import datetime, timezone, timedelta
import itertools
from elastic_manager import ElasticManager
from time_logger import time_log
import logging

# logger = logging.getLogger(__name__)
# handler = logging.FileHandler("log/data_importer.log")
# logger.addHandler(handler)

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
    def import_raw_data(self, data_to_import: str, index_to_import: str, thread_count = 4) -> None:
        """ rawデータインポート処理 """

        mapping_file = "notebooks/mapping_rawdata.json"
        # mapping_file = None
        setting_file = "notebooks/setting_rawdata.json"
        # setting_file = None

        ElasticManager.delete_exists_index(index=index_to_import)
        ElasticManager.create_index(index=index_to_import, mapping_file=mapping_file, setting_file=setting_file)

        ElasticManager.parallel_bulk(
            doc_generator=self.__doc_generator(data_to_import, index_to_import),
            thread_count=thread_count,
            chunk_size=5000)

    @time_log
    def multi_process_import_raw_data(self, data_to_import: str, index_to_import: str, num_of_process: int) -> None:
        """ 使い捨て?。マルチプロセス読み込み """

        mapping_file = "notebooks/mapping_rawdata.json"
        # mapping_file = None
        setting_file = "notebooks/setting_rawdata.json"
        # setting_file = None

        ElasticManager.delete_exists_index(index=index_to_import)
        ElasticManager.create_index(index=index_to_import, mapping_file=mapping_file, setting_file=setting_file)

        rawdata_gen = self.__doc_generator(data_to_import, index_to_import)

        BUFFER_SIZE = 10_000_000

        i = 0
        while True:
            rawdata = [x['_source'] for x in itertools.islice(rawdata_gen, 0, BUFFER_SIZE)]

            if len(rawdata) == 0:
                break

            ElasticManager.multi_process_bulk(data=rawdata, index_to_import=index_to_import,
                                              num_of_process=num_of_process, chunk_size=5000)
            i += 1

    @time_log
    def import_data_by_shot(self, rawdata_index: str, shots_index: str, start_displacement: float,
                            end_displacement: float, num_of_process: int = 4):
        """ shotデータインポート処理 """

        mapping_file = "notebooks/mapping_shots.json"
        # mapping_file = None

        ElasticManager.delete_exists_index(index=shots_index)
        ElasticManager.create_index(index=shots_index, mapping_file=mapping_file)

        self._cut_out_shot(rawdata_index, shots_index, start_displacement, end_displacement, num_of_process)

    def __doc_generator(self, csv_file: str, index_name: str) -> Iterator:
        """ csv を読み込んで一行ずつ辞書型で返すジェネレータ

        TODO:
            csv_file読み込みからpcmファイル読み込みに変更する
        """

        DISPLAY_THROUGHPUT_DOC_NUM = 100000

        with open(csv_file, "rt", encoding="utf-8") as file:
            reader = DictReader(file, fieldnames=["#EndHeader", "日時(μs)", "(2)HA-V01", "(2)HA-V02",
                                                  "(2)HA-V03", "(2)HA-V04", "(2)HA-C01", "(2)HA-C02"])
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
    def _cut_out_shot(self, rawdata_index: str, shots_index: str, start_displacement: float,
                      end_displacement: float, num_of_process: int) -> None:
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
        print(f"rawdata count: {rawdata_count}")

        # rawdataをN分割する。暫定値。
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
            # 最後のループの場合、残った全てのデータを取得する。
            if i == SPLIT_SIZE:
                end_index = rawdata_count + 1

            rawdata_list = ElasticManager.multi_process_range_scan(
                index=rawdata_index, num_of_data=batch_size, start=start_index,
                end=end_index, num_of_process=num_of_process)

            # 分割されたものの中のデータ1件ずつ確認していく
            for i, rawdata in enumerate(rawdata_list):
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
                    previous_rawdata_list = ElasticManager.single_process_range_scan(
                        index=rawdata_index, start=previous_start_index, end=previous_end_index)

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
                    ElasticManager.multi_process_bulk(data=shots, index_to_import=shots_index,
                                                      num_of_process=num_of_process, chunk_size=5000)
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

        dt_now = datetime.now(JST)
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
    # formatter = "%(levelname)s : %(asctime)s : %(message)s"
    # logging.basicConfig(level=logging.INFO, format=formatter)

    data_importer = DataImporter()
    # data_importer.multi_process_import_raw_data('notebooks/No13_3000.csv', 'rawdata-no13-3000', 8)
    # data_importer.import_raw_data('notebooks/No13_3000.csv', 'rawdata-no13-3000-2', 8)
    data_importer.import_data_by_shot('rawdata-no13-3000-2', 'shots-no13-3000', 47, 34, 8)

from typing import Final, Tuple
from datetime import datetime, timezone, timedelta
import logging
import logging.handlers
import pandas as pd

from elastic_manager import ElasticManager
from time_logger import time_log
from throughput_counter import throughput_counter

LOG_FILE: Final = "log/data_importer.log"
MAX_LOG_SIZE: Final = 1024 * 1024  # 1MB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler("log/data_importer.log", maxBytes=MAX_LOG_SIZE, backupCount=7),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# datetime取得時に日本時間を指定する
JST = timezone(timedelta(hours=+9), "JST")


class DataImporter:
    """
     データインポートクラス

     TODO:
           from elasticsearch(生データ) to elasticsearch処理追加
           meta_index作成
    """

    @time_log
    def import_raw_data(self, data_to_import: str, index_to_import: str, thread_count=4) -> None:
        """ rawデータインポート処理（廃止予定） """

        mapping_file = "mappings/mapping_rawdata.json"
        setting_file = "mappings/setting_rawdata.json"

        ElasticManager.delete_exists_index(index=index_to_import)
        ElasticManager.create_index(index=index_to_import, mapping_file=mapping_file, setting_file=setting_file)

        ElasticManager.parallel_bulk(
            doc_generator=self.__doc_generator(data_to_import, index_to_import),
            thread_count=thread_count,
            chunk_size=5000,
        )

    @time_log
    def multi_process_import_rawdata(self, rawdata_filename: str, index_to_import: str, num_of_process: int) -> None:
        """ rawdata csvのマルチプロセス読み込み
         本番ではバイナリファイル読み込みのため、本メソッドはテスト用途。
        """

        ElasticManager.delete_exists_index(index=index_to_import)

        mapping_file = "mappings/mapping_rawdata.json"
        setting_file = "mappings/setting_rawdata.json"
        ElasticManager.create_index(index=index_to_import, mapping_file=mapping_file, setting_file=setting_file)

        CHUNK_SIZE: Final = 10_000_000
        cols = (
            "load01",
            "load02",
            "load03",
            "load04",
            "displacement",
        )

        samples = []  # rawdataのサンプルを貯めるリスト
        now: datetime = datetime.now(JST)

        for loop_count, rawdata_df in enumerate(pd.read_csv(rawdata_filename, chunksize=CHUNK_SIZE, names=cols)):
            processed_count: int = loop_count * CHUNK_SIZE if loop_count != 0 else CHUNK_SIZE
            throughput_counter(processed_count, now)

            for row in rawdata_df.itertuples():
                sample = {
                    "sequential_number": row.Index,
                    "load01": row.load01,
                    "load02": row.load02,
                    "load03": row.load03,
                    "load04": row.load04,
                    "displacement": row.displacement,
                }
                samples.append(sample)

            ElasticManager.multi_process_bulk(
                data=samples, index_to_import=index_to_import, num_of_process=num_of_process, chunk_size=5000,
            )

            samples = []

    @time_log
    def import_data_by_shot(
        self,
        rawdata_filename: str,
        shots_index: str,
        start_displacement: float,
        end_displacement: float,
        num_of_process: int = 4,
    ):
        """ shotデータインポート処理 """

        ElasticManager.delete_exists_index(index=shots_index)

        mapping_file = "mappings/mapping_shots.json"
        ElasticManager.create_index(index=shots_index, mapping_file=mapping_file)

        self.__cut_out_shot_from_csv(
            rawdata_filename=rawdata_filename,
            shots_index=shots_index,
            start_displacement=start_displacement,
            end_displacement=end_displacement,
            num_of_process=num_of_process,
        )

    # 廃止予定
    @time_log
    def _cut_out_shot(
        self,
        rawdata_index: str,
        shots_index: str,
        start_displacement: float,
        end_displacement: float,
        num_of_process: int,
    ) -> None:
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
        SPLIT_SIZE: int = 50
        batch_size, mod = divmod(rawdata_count, SPLIT_SIZE)

        is_shot_section: bool = False  # ショット内か否かを判別する
        is_target_of_cut_off: bool = False  # ショットの内、切り出し対象かを判別する
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
                index=rawdata_index,
                num_of_data=batch_size,
                start=start_index,
                end=end_index,
                num_of_process=num_of_process,
            )

            # 分割されたものの中のデータ1件ずつ確認していく
            for i, rawdata in enumerate(rawdata_list):
                # ショット開始判定
                if (not is_shot_section) and (rawdata["displacement"] <= start_displacement):
                    is_shot_section = True
                    is_target_of_cut_off = True
                    shot_number += 1
                    sequential_number_by_shot = 0
                    # print(f"shot is detected. shot_number: {shot_number}")

                    # N件遡ってshotsに加える。暫定で1000件。
                    # TODO: キャッシュ検討
                    previous_start_index = (
                        rawdata["sequential_number"] - 1000 if rawdata["sequential_number"] >= 1000 else 0
                    )
                    previous_end_index = rawdata["sequential_number"]
                    previous_rawdata_list = ElasticManager.single_process_range_scan(
                        index=rawdata_index, start=previous_start_index, end=previous_end_index,
                    )

                    for previous_rawdata in previous_rawdata_list:
                        shot: dict = {
                            "sequential_number": sequential_number,
                            "sequential_number_by_shot": sequential_number_by_shot,
                            "load01": previous_rawdata["load01"],
                            "load02": previous_rawdata["load02"],
                            "load03": previous_rawdata["load03"],
                            "load04": previous_rawdata["load04"],
                            "displacement": previous_rawdata["displacement"],
                            "shot_number": shot_number,
                            "tags": [],
                        }
                        shots.append(shot)
                        sequential_number += 1
                        sequential_number_by_shot += 1

                # ショット区間の終了判定
                # 0.1（暫定値）はノイズの影響等で変位値が単調減少しなかった場合、ショット区間がすぐに終わってしまうことを防ぐためのバッファ
                if rawdata["displacement"] > start_displacement + 0.1:
                    is_shot_section = False

                # ショット未開始ならば後続は何もしない
                if not is_shot_section:
                    continue

                # 切り出し区間の終了判定
                if rawdata["displacement"] <= end_displacement:
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
                    "load01": rawdata["load01"],
                    "load02": rawdata["load02"],
                    "load03": rawdata["load03"],
                    "load04": rawdata["load04"],
                    "displacement": rawdata["displacement"],
                    "shot_number": shot_number,
                    "tags": [],
                }
                shots.append(shot)

                # ショットデータが一定件数（暫定で1,000,000）以上溜まったらElasticsearchに書き出す。
                if len(shots) >= 1_000_000:
                    dt_now = datetime.now(JST)
                    ElasticManager.multi_process_bulk(
                        data=shots, index_to_import=shots_index, num_of_process=num_of_process, chunk_size=5000,
                    )
                    inserted_count += len(shots)
                    throughput_counter(len(shots), dt_now)
                    shots = []

            # end of splitted rawdata loop
        # end of all rawdata loop

        # Elasticsearchに書き出されていないデータが残っていれば書き出す
        if len(shots) > 0:
            # 余りは少数のデータ、かつ分割プロセス数を下回る可能性があるので、シングルプロセスで実行
            ElasticManager.bulk_insert(shots, shots_index)
            inserted_count += len(shots)

        dt_now = datetime.now(JST)
        print(f"{dt_now} cut_off finished. {len(shots)} documents inserted.")

    @time_log
    def __cut_out_shot_from_csv(
        self,
        rawdata_filename: str,
        shots_index: str,
        start_displacement: float,
        end_displacement: float,
        num_of_process: int,
    ) -> None:
        """
        ショット切り出し処理。生データの変位値を参照し、ショット対象となるデータのみをリストに含めて返す。

        Args:
            rawdata_filename: 生データcsvのファイル名
            shots_index: ショットデータの格納先インデックス
            start_displacement: ショット開始となる変位値
            end_displacement: ショット終了となる変位値
            num_of_process: 並列処理のプロセス数
        """

        CHUNK_SIZE: Final = 1_000_000  # csvから一度に読み出す行数
        TAIL_SIZE: Final = 1_000  # 末尾データ保持数（chunk跨ぎの際に利用）
        BUFFER_SIZE: Final = 1_000_000  # ショットをESに書き出す前のバッファサイズ

        is_shot_section: bool = False  # ショット内か否かを判別する
        is_target_of_cut_off: bool = False  # ショットの内、切り出し対象かを判別する
        sequential_number: int = 0
        sequential_number_by_shot: int = 0
        shot_number: int = 0
        inserted_count: int = 0  # Thoughput算出用
        shots: list = []

        cols: Tuple = (
            "load01",
            "load02",
            "load03",
            "load04",
            "displacement",
        )

        current_df_tail = pd.DataFrame(index=[], columns=cols)  # 現在のCHUNKの末尾N件を保持
        previous_df_tail = pd.DataFrame(index=[], columns=cols)  # 1つ前のCHUNKの末尾N件を保持

        start_time: datetime = datetime.now(JST)

        # CHUNK_SIZE分を一度に読み出し、全件読み終わるまで繰り返し
        for loop_count, rawdata_df in enumerate(pd.read_csv(rawdata_filename, chunksize=CHUNK_SIZE, names=cols)):
            processed_count: int = loop_count * CHUNK_SIZE if loop_count != 0 else CHUNK_SIZE
            logger.info(f"Processing...{processed_count} samples")

            # chunk開始直後にショットを検知した場合、N件遡るためのデータを保持しておく必要がある。
            # TODO: メソッド化
            if loop_count == 0:
                current_df_tail = rawdata_df[-TAIL_SIZE:]
            else:
                previous_df_tail = current_df_tail
                current_df_tail = rawdata_df[-TAIL_SIZE:]

            # chunk内のDataFrameを1件ずつ走査し、ショット判別する
            # TODO: メソッド化
            for row_number, rawdata in enumerate(rawdata_df.itertuples()):
                # ショット開始判定
                # TODO: メソッド化
                if (not is_shot_section) and (rawdata.displacement <= start_displacement):
                    is_shot_section = True
                    is_target_of_cut_off = True
                    shot_number += 1
                    sequential_number_by_shot = 0
                    logger.info(f"Detect shot. Shot number is {shot_number}")

                    # N件遡ってshotsに加える。
                    # 遡って取得するデータが現在のDataFrameに含まれる場合
                    if row_number >= TAIL_SIZE:
                        # ショットを検知したところから1,000件遡ってデータを取得
                        start_index: int = row_number - TAIL_SIZE
                        end_index: int = row_number
                        preceding_df = rawdata_df[start_index:end_index]

                    # 遡って取得するデータが現在のDataFrameに含まれない場合
                    else:
                        # 含まれない範囲のデータを過去のDataFrameから取得
                        start_index: int = row_number
                        preceding_df = previous_df_tail[start_index:]

                    # 遡るデータをショットに含める
                    for row in preceding_df.itertuples():
                        shot = {
                            "sequential_number": sequential_number,
                            "sequential_number_by_shot": sequential_number_by_shot,
                            "load01": row.load01,
                            "load02": row.load02,
                            "load03": row.load03,
                            "load04": row.load04,
                            "displacement": row.displacement,
                            "shot_number": shot_number,
                            "tags": [],
                        }
                        shots.append(shot)
                        sequential_number += 1
                        sequential_number_by_shot += 1

                # ショット区間の終了判定
                # 0.1（暫定値）はノイズの影響等で変位値が単調減少しなかった場合、ショット区間がすぐに終わってしまうことを防ぐためのバッファ
                if is_shot_section and (rawdata.displacement > start_displacement + 0.1):
                    is_shot_section = False

                # ショット未開始ならば後続は何もしない
                if not is_shot_section:
                    continue

                # 切り出し区間の終了判定
                if rawdata.displacement <= end_displacement:
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
                    "load01": float(format(rawdata.load01, ".3f")),
                    "load02": float(format(rawdata.load02, ".3f")),
                    "load03": float(format(rawdata.load03, ".3f")),
                    "load04": float(format(rawdata.load04, ".3f")),
                    "displacement": rawdata.displacement,
                    "shot_number": shot_number,
                    "tags": [],
                }
                shots.append(shot)

                # ショットデータが一定件数以上溜まったらElasticsearchに書き出す。
                if len(shots) >= BUFFER_SIZE:
                    logger.info(f"Shots Buffer is filled. Bulk insert {len(shots)} documents.")
                    bulk_started: datetime = datetime.now(JST)
                    ElasticManager.multi_process_bulk(
                        data=shots, index_to_import=shots_index, num_of_process=num_of_process, chunk_size=5000,
                    )
                    logger.info(f"Bulk insert finished. {len(shots)} documents inserted.")
                    inserted_count += len(shots)
                    throughput_counter(len(shots), bulk_started)
                    shots = []

            # end of splitted rawdata loop
            throughput_counter(processed_count, start_time)

        # end of all rawdata loop

        # Elasticsearchに書き出されていないデータが残っていれば書き出す
        if len(shots) > 0:
            logger.info(f"Bulk insert {len(shots)} documents.")
            # 余りは少数のデータ、かつ分割プロセス数を下回る可能性があるので、シングルプロセスで実行
            ElasticManager.bulk_insert(shots, shots_index)
            inserted_count += len(shots)

        logger.info(f"Cut_off finished. {len(shots)} documents inserted.")


if __name__ == "__main__":
    """ スクリプト直接実行時はテスト用インデックスにインポートする """

    data_importer = DataImporter()
    # small data
    # data_importer.multi_process_import_rawdata("data/No13.csv", "rawdata-no13", 7)
    data_importer.import_data_by_shot("data/No13.csv", "shots-no13", 47, 34, 8)

    # big data
    # data_importer.multi_process_import_rawdata(
    #     "data/No13_3000.csv", "rawdata-no13-3000", 8
    # )
    # data_importer.import_data_by_shot(
    #     "data/No13_3000.csv", "shots-no13-3000", 47, 34, 8
    # )


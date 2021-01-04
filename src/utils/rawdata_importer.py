from typing import Final
from datetime import datetime

import logging
import logging.handlers
import pandas as pd

from elastic_manager import ElasticManager
from time_logger import time_log
from throughput_counter import throughput_counter

LOG_FILE: Final = "log/rawdata_importer/rawdata_importer.log"
MAX_LOG_SIZE: Final = 1024 * 1024  # 1MB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=5),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class RawdataImporter:
    @time_log
    def import_raw_data(self, data_to_import: str, index_to_import: str, thread_count=4) -> None:
        """ rawデータインポート処理 """

        ElasticManager.delete_exists_index(index=index_to_import)

        mapping_file = "mappings/mapping_rawdata.json"
        setting_file = "mappings/setting_rawdata.json"
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

        now: datetime = datetime.now()

        CHUNK_SIZE: Final = 10_000_000
        cols = ("load01", "load02", "load03", "load04", "displacement")

        samples = []
        for loop_count, rawdata_df in enumerate(pd.read_csv(rawdata_filename, chunksize=CHUNK_SIZE, names=cols)):
            processed_count: int = loop_count * CHUNK_SIZE
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


def main():
    rawdata_importer = RawdataImporter()
    # rawdata_importer.multi_process_import_rawdata("data/No13.csv", "rawdata-no13", 8)
    rawdata_importer.multi_process_import_rawdata("data/No04.CSV", "rawdata-no04", 8)


if __name__ == "__main__":
    main()

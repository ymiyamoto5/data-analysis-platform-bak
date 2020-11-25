from elastic_manager import ElasticManager


def create_shot_analy_index(self, data_to_import: str, index_to_import: str) -> None:
    """ rawデータインポート処理 """

    ElasticManager.delete_exists_index(index=index_to_import)
    ElasticManager.create_index(index=index_to_import)

    ElasticManager.parallel_bulk(
        doc_generator=self.__doc_generator(data_to_import, index_to_import),
        data_to_import=data_to_import,
        index_to_import=index_to_import,
        thread_count=2,
        chunk_size=5000)


def __doc_generator():
    for i in range(1, 10):
        data = {
            "shot_number": i,
            "load01_start_value": i * 0.1,
            "load01_start_sequential_number_by_shot": 1000,
            "load02_start_value": i * 0.2,
            "load02_start_sequential_number_by_shot": 1001,
        }

        yield data
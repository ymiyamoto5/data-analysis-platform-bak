from elastic_manager import ElasticManager
from elasticsearch import Elasticsearch

class ShotAnalyzed():
    def create_shot_analy_index(self, data_to_import: str, index_to_import: str) -> None:
        """ rawデータインポート処理 """

        ElasticManager.delete_exists_index(index=index_to_import)
        ElasticManager.create_index(index=index_to_import)

        # ElasticManager.parallel_bulk(
        #     doc_generator=self.__doc_generator(data_to_import, index_to_import),
        #     thread_count=2,
        #     chunk_size=5000)

        es = Elasticsearch(hosts="localhost:9200", http_auth=('elastic', 'P@ssw0rd12345'), timeout=50000)

        data = {
            "shot_number": 2,
            "sequential_number": 7550,
            "load01_start_value": 0.392,
            "load01_start_sequential_number_by_shot": 7550,
            "load02_start_value": 0.292,
            "load02_start_sequential_number_by_shot": 7551,
            "load01_max_value": 5.376,
            "load01_max_sequential_number_by_shot": 8600,
            "load02_max_value": 5.276,
            "load02_max_sequential_number_by_shot": 8601,
            "load01_cut_value": 2.308,
            "load01_cut_sequential_number_by_shot": 7900,
            "load02_cut_value": 2.208,
            "load02_cut_sequential_number_by_shot": 7901,
        }
        
        es.create(index=index_to_import, id=1, body=data)

        data = {
            "shot_number": 3,
            "sequential_number": 19800,
            "load01_start_value": 0.392,
            "load01_start_sequential_number_by_shot": 19800,
            "load02_start_value": 0.292,
            "load02_start_sequential_number_by_shot": 19850,
            "load01_max_value": 5.376,
            "load01_max_sequential_number_by_shot": 21000,
            "load02_max_value": 5.276,
            "load02_max_sequential_number_by_shot": 21050,
            "load01_cut_value": 2.308,
            "load01_cut_sequential_number_by_shot": 20400,
            "load02_cut_value": 2.208,
            "load02_cut_sequential_number_by_shot": 20450,
            "tmp": True,
        }
        
        es.create(index=index_to_import, id=2, body=data)

    # def __doc_generator(self, data_to_import, index_to_import):
    #     for i in range(1, 10):
    #         data = {
    #             "shot_number": i,
    #             "sequential_number": i * 1000,
    #             "load01_start_value": i * 0.1,
    #             "load01_start_sequential_number_by_shot": 1000 * i,
    #             "load02_start_value": i * 0.2,
    #             "load02_start_sequential_number_by_shot": 1500 * i,
    #             "load01_max_value": i + 1,
    #             "load01_max_sequential_number_by_shot": 1000 * i,
    #             "load02_max_value": i + 2,
    #             "load02_max_sequential_number_by_shot": 1500 * i,
    #             "load01_cut_value": i * 1,
    #             "load01_cut_sequential_number_by_shot": 1000 * i,
    #             "load02_cut_value": i * 2,
    #             "load02_cut_sequential_number_by_shot": 1500 * i,
    #         }

    #         yield {
    #             "_index": index_to_import,
    #             "_id": data["shot_number"],
    #             "_source": data
    #         }


if __name__ == '__main__':
    sa = ShotAnalyzed()
    sa.create_shot_analy_index('', 'analyzed-test')

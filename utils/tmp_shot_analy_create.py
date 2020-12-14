from elastic_manager import ElasticManager
from elasticsearch import Elasticsearch


class ShotAnalyzed:
    def create_shot_analy_index(self) -> None:
        """ rawデータインポート処理 """

        es = Elasticsearch(hosts="localhost:9200", http_auth=("elastic", "P@ssw0rd12345"), timeout=50000)

        start_point_index = "features-01-start-point"
        ElasticManager.delete_exists_index(index=start_point_index)
        ElasticManager.create_index(index=start_point_index)

        data = {
            "load": "load01",
            "shot_number": 1,
            "sequential_number": 1001,
            "value": 0.192,
        }
        es.create(index=start_point_index, id=1, body=data)
        data = {
            "load": "load02",
            "shot_number": 1,
            "sequential_number": 1002,
            "value": 0.252,
        }
        es.create(index=start_point_index, id=2, body=data)
        data = {
            "load": "load03",
            "shot_number": 1,
            "sequential_number": 1003,
            "value": 0.113,
        }
        es.create(index=start_point_index, id=3, body=data)
        data = {
            "load": "load04",
            "shot_number": 1,
            "sequential_number": 1003,
            "value": 0.20,
        }
        es.create(index=start_point_index, id=4, body=data)

        data = {
            "load": "load01",
            "shot_number": 2,
            "sequential_number": 4100,
            "value": 0.22,
        }
        es.create(index=start_point_index, id=5, body=data)
        data = {
            "load": "load02",
            "shot_number": 2,
            "sequential_number": 4101,
            "value": 0.282,
        }
        es.create(index=start_point_index, id=6, body=data)
        data = {
            "load": "load03",
            "shot_number": 2,
            "sequential_number": 4100,
            "value": 0.153,
        }
        es.create(index=start_point_index, id=7, body=data)
        data = {
            "load": "load04",
            "shot_number": 2,
            "sequential_number": 4120,
            "value": 0.19,
        }
        es.create(index=start_point_index, id=8, body=data)

        ################################
        max_point_index = "features-01-max-point"
        ElasticManager.delete_exists_index(index=max_point_index)
        ElasticManager.create_index(index=max_point_index)

        data = {
            "load": "load01",
            "shot_number": 1,
            "sequential_number": 2191,
            "value": 2.72,
        }
        es.create(index=max_point_index, id=101, body=data)
        data = {
            "load": "load02",
            "shot_number": 1,
            "sequential_number": 2190,
            "value": 2.114,
        }
        es.create(index=max_point_index, id=102, body=data)
        data = {
            "load": "load03",
            "shot_number": 1,
            "sequential_number": 1988,
            "value": 1.365,
        }
        es.create(index=max_point_index, id=103, body=data)
        data = {
            "load": "load04",
            "shot_number": 1,
            "sequential_number": 1988,
            "value": 1.476,
        }
        es.create(index=max_point_index, id=104, body=data)

        break_point_index = "features-01-break-point"
        ElasticManager.delete_exists_index(index=break_point_index)
        ElasticManager.create_index(index=break_point_index)

        data = {
            "load": "load01",
            "shot_number": 1,
            "sequential_number": 2222,
            "value": 1.2,
        }
        es.create(index=break_point_index, id=1, body=data)
        data = {
            "load": "load02",
            "shot_number": 1,
            "sequential_number": 2222,
            "value": 1,
        }
        es.create(index=break_point_index, id=2, body=data)
        data = {
            "load": "load03",
            "shot_number": 1,
            "sequential_number": 2117,
            "value": 1,
        }
        es.create(index=break_point_index, id=3, body=data)
        data = {
            "load": "load04",
            "shot_number": 1,
            "sequential_number": 2150,
            "value": 0.8,
        }
        es.create(index=break_point_index, id=4, body=data)

    ################################
    # features_index = "features-01"
    # ElasticManager.delete_exists_index(index=features_index)
    # ElasticManager.create_index(index=features_index)

    # data = {
    #     "shot_number": 1,
    #     "load01_start_value": 0.192,
    #     "load01_start_sequential_number": 1000,
    #     "load02_start_value": 0.252,
    #     "load02_start_sequential_number": 1001,
    #     "load03_start_value": 0.113,
    #     "load03_start_sequential_number": 1000,
    #     "load04_start_value": 0.2,
    #     "load04_start_sequential_number": 1001,
    #     "load01_max_value": 2.72,
    #     "load01_max_sequential_number": 2100,
    #     "load02_max_value": 1.786,
    #     "load02_max_sequential_number": 2150,
    #     "load03_max_value": 1.365,
    #     "load03_max_sequential_number": 1900,
    #     "load04_max_value": 1.476,
    #     "load04_max_sequential_number": 1950,
    # }

    # es.create(index=features_index, id=1, body=data)

    # data = {
    #     "shot_number": 2,
    #     "load01_start_value": 0.192,
    #     "load01_start_sequential_number": 4100,
    #     "load02_start_value": 0.252,
    #     "load02_start_sequential_number": 4101,
    #     "load03_start_value": 0.113,
    #     "load03_start_sequential_number": 4100,
    #     "load04_start_value": 0.2,
    #     "load04_start_sequential_number": 4101,
    #     "load01_max_value": 1.7,
    #     "load01_max_sequential_number": 5200,
    #     "load02_max_value": 1.786,
    #     "load02_max_sequential_number": 5201,
    #     "load03_max_value": 1.365,
    #     "load03_max_sequential_number": 5203,
    #     "load04_max_value": 1.476,
    #     "load04_max_sequential_number": 5204,
    # }
    # es.create(index=features_index, id=2, body=data)


if __name__ == "__main__":
    sa = ShotAnalyzed()
    sa.create_shot_analy_index()

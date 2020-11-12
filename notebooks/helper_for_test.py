from elasticsearch import Elasticsearch
from elasticsearch import helpers


class MockIndex:
    ''' テスト用indexの作成、データ登録、削除を提供するクラス '''

    def __init__(self, index) -> None:
        self.es = Elasticsearch(hosts="localhost:9200", http_auth=(
            'elastic', 'P@ssw0rd12345'), timeout=50000)
        self.index = index
        self.delete_index()
        self.create_index()

    def __del__(self) -> None:
        self.es.close()

    def create_index(self) -> None:
        body = {"settings": {"index": {"max_result_window": 10000}}}
        self.es.indices.create(index=self.index, body=body)

    def delete_index(self) -> None:
        if self.es.indices.exists(index=self.index):
            self.es.indices.delete(index=self.index)

    def create(self, data) -> None:
        count_dict = self.es.count(index=self.index)
        id = count_dict["count"] + 1
        self.es.create(index=self.index, id=id, body=data)

    def bulk_insert(self, data) -> None:
        actions = []
        for d in data:
            actions.append({'_index': self.index, '_source': d})

        # NOTE: refreshパラメータを指定しないと、挿入したデータが検索可能になる前に取得しにいってしまう場合がある。
        helpers.bulk(self.es, actions, refresh=True)

    def search(self, query) -> None:
        result = self.es.search(index=self.index, body=query)
        for document in result["hits"]["hits"]:
            print(document["_source"])
        return result


if __name__ == '__main__':
    mock_index = MockIndex("test-raw-index")

    bulk_data = [
        {
            "sequential_number": 1,
            "load": 10
        },
        {
            "sequential_number": 2,
            "load": 20
        },
        {
            "sequential_number": 3,
            "load": 30
        },
    ]

    mock_index.bulk_insert(bulk_data)

    result = mock_index.search({})
    for r in result["hits"]["hits"]:
        print(r)

    mock_index.delete_index()

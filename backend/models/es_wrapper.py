from elasticsearch import Elasticsearch
from elasticsearch import helpers


class ElasticsearchWrapper:
    ''' ElasticsearchへのCRUD処理をラッピングして提供するクラス '''

    def __init__(self) -> None:
        # TODO: elasticsearchにつながらないときのエラーハンドリング
        self.es = Elasticsearch(hosts="localhost:9200", http_auth=(
            "elastic", "P@ssw0rd12345"))

    def __del__(self) -> None:
        self.es.close()

    def create_index(self, index) -> None:
        if not self.es.indices.exists(index=index):
            body = {"settings": {"index": {"max_result_window": 10000}}}
            self.es.indices.create(index=index, body=body)

    def delete_index(self, index) -> None:
        if self.es.indices.exists(index=index):
            self.es.indices.delete(index=index)

    def create(self, index, data, id=None) -> None:
        if id is None:
            count_dict = self.es.count(index=index)
            id = count_dict["count"] + 1
        # NOTE: refreshパラメータを指定しないと、挿入したデータが検索可能になる前に取得しにいってしまう場合がある。
        self.es.create(index=index, id=id, body=data, refresh=True)

    def exists(self, index, id) -> bool:
        return self.es.exists(index=index, id=id, refresh=True)

    def update(self, index, data, id) -> None:
        body = {
            "doc": data
        }
        self.es.update(index=index, id=id, body=body)

    def upsert(self, index, data, id) -> None:
        body = {
            'doc': data,
            'doc_as_upsert': True,
        }
        self.es.update(index=index, id=id, body=body)

    def bulk_insert(self, index, data) -> None:
        actions = []
        for d in data:
            actions.append({'_index': index, '_source': d})

        # NOTE: refreshパラメータを指定しないと、挿入したデータが検索可能になる前に取得しにいってしまう場合がある。
        helpers.bulk(self.es, actions, refresh=True)

    def search(self, index, query) -> None:
        result = self.es.search(index=index, body=query)

        listed_result = []
        for document in result["hits"]["hits"]:
            listed_result.append(document["_source"])

        return listed_result

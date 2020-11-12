from elasticsearch import Elasticsearch


class ElasticManager:
    es = Elasticsearch(hosts="localhost:9200", http_auth=('elastic', 'P@ssw0rd12345'), timeout=50000)

    @classmethod
    def show_indices(cls, show_all_index: bool = False) -> None:
        '''
         インデックス一覧を表示する。
            Args:
                show_all_index: Trueの場合、すべてのインデックスを表示する。デフォルトはFalseで、本プロジェクトに関係するインデックスのみ表示する。
        '''

        if show_all_index:
            indices = cls.es.cat.indices(
                index='*', v=True, h=['index', 'docs.count', 'store.size'], bytes='kb').splitlines()
        else:
            indices = cls.es.cat.indices(
                index=['rawdata-*', 'shots-*', 'meta-*'], v=True, h=['index', 'docs.count', 'store.size'], bytes='kb'
            ).splitlines()

        for index in indices:
            print(index)

    def delete_index(self) -> None:
        pass

    def delete_documents(self) -> None:
        pass


if __name__ == '__main__':
    ElasticManager.show_indices()

from .es_wrapper import ElasticsearchWrapper


class Reporting():
    def __init__(self) -> None:
        pass

    @classmethod
    def getMetaData(cls, query={"query": {"match_all": {}}, "size": 10000}) -> None:
        es = ElasticsearchWrapper()
        return es.search("meta-data", query)

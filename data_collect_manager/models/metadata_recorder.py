import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../utils"))
from elastic_manager import ElasticManager


class MetaDataRecorder:
    def __init__(self):
        pass

    def create_index(self, meta_index: str) -> bool:
        successful: bool = ElasticManager.create_index(meta_index)

        return successful

    def create_doc(self):
        pass

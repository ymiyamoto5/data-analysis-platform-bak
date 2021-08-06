import os
import sys
from typing import List
from pandas.core.frame import DataFrame
import logging
import logging.handlers

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager

logger = logging.getLogger(__name__)


def df_to_els(df: DataFrame, index: str, mapping: str = None, setting: str = None):
    """ DataFrameをList[dict]に変換し、指定したindex名でElasticsearchに登録する """

    if ElasticManager.exists_index(index):
        ElasticManager.delete_index(index)
    ElasticManager.create_index(index=index, mapping_file=mapping, setting_file=setting)

    data_list: List[dict] = df.to_dict(orient="records")

    ElasticManager.bulk_insert(data_list, index)

    logger.info(f"{index} created.")

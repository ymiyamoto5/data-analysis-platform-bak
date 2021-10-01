from typing import List

from backend.common.common_logger import logger
from backend.elastic_manager.elastic_manager import ElasticManager
from pandas.core.frame import DataFrame


def df_to_els(df: DataFrame, index: str, mapping: str = None, setting: str = None):
    """DataFrameをList[dict]に変換し、指定したindex名でElasticsearchに登録する"""

    if ElasticManager.exists_index(index):
        ElasticManager.delete_index(index)
    ElasticManager.create_index(index=index, mapping_file=mapping, setting_file=setting)

    data_list: List[dict] = df.to_dict(orient="records")

    ElasticManager.bulk_insert(data_list, index)

    logger.info(f"{index} created.")

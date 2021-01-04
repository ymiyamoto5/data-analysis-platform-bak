import json
import logging

logger = logging.getLogger(__name__)


def get_config_value(file_path: str, key: str):
    try:
        with open(file_path, "r") as f:
            config: dict = json.load(f)
    except Exception as e:
        logger.exception(str(e))
        raise e

    value = config.get(key)

    if value is None:
        logger.error(f"Key {key} is not found in {file_path}")
        raise KeyError

    return value

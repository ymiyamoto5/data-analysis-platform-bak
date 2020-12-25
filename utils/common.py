import json
import logging

logger = logging.getLogger(__name__)


def get_settings_value(settings_file_path: str, key: str):
    with open(settings_file_path, "r") as f:
        settings: dict = json.load(f)
    value = settings.get(key)

    if value is None:
        logger.error(f"Key {key} is not found in setting_file")
        raise KeyError

    return value

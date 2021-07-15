import os
import sys
import inspect
from logging import getLogger
from logging.config import dictConfig
from typing import Final

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import common

# MODULE_NAME = ""
# CONFIG = {}


def init_logger(module_name):

    # global MODULE_NAME
    # MODULE_NAME = modlue_name

    LOG_DIR: Final[str] = os.path.join(common.get_config_value(common.APP_CONFIG_PATH, "log_dir"), module_name)
    LOG_FILE: Final[str] = os.path.join(LOG_DIR, module_name + ".log")

    # global CONFIG
    CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "basic": {"format": "%(asctime)s [%(levelname)s] %(message)s", "datefmt": "%Y-%m-%d %H:%M:%S",}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "basic",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "basic",
                "filename": LOG_FILE,
                "maxBytes": common.MAX_LOG_SIZE,
                "backupCount": common.BACKUP_COUNT,
            },
        },
        "loggers": {module_name: {"level": "INFO", "handlers": ["console", "file"], "propagate": False}},
        "root": {"level": "INFO", "handlers": ["console", "file"]},
    }

    dictConfig(CONFIG)


def get_logger(module_name):
    return getLogger(module_name)

import multiprocessing
import os
import sys
import logging
import logging.handlers
import pandas as pd
import glob
from typing import Callable, Final, List, Optional
from datetime import datetime, timedelta
from pandas.core.frame import DataFrame

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
from time_logger import time_log
from throughput_counter import throughput_counter
import common

LOG_FILE: Final[str] = os.path.join(common.get_config_value(common.APP_CONFIG_PATH, "log_dir"), "analyze/analyze.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=common.MAX_LOG_SIZE, backupCount=common.BACKUP_COUNT),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


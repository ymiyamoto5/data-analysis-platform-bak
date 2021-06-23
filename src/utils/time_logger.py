"""
 ==================================
  time_logger.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

from typing import Callable, TypeVar
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

RT = TypeVar("RT")


def time_log(func: Callable[..., RT]) -> Callable[..., RT]:
    """ 開始・終了・経過時間を表示するデコレータ """

    def wrapper(*args, **kwargs):
        start = datetime.now()
        func(*args, **kwargs)
        end = datetime.now()
        delta = end - start
        logger.info(f"{func.__name__} finished. elapsed time: {delta}")

    return wrapper

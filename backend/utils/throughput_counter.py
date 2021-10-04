"""
 ==================================
  throughput_counter.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

from datetime import datetime, timedelta

from backend.common.common_logger import logger


def throughput_counter(processed_count: int, dt_old: datetime) -> None:
    """スループット（秒間の処理件数）の表示"""

    now: datetime = datetime.now()
    dt_delta: timedelta = now - dt_old
    total_sec: float = dt_delta.total_seconds()
    throughput: int = int(processed_count / total_sec)

    logger.info(f"Thoughput: {throughput} doc/sec, processed_count: {processed_count}")

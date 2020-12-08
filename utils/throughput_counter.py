from datetime import datetime, timedelta
import logging

# datetime取得時に日本時間を指定する
# JST = timezone(timedelta(hours=+9), "JST")
logger = logging.getLogger(__name__)


def throughput_counter(processed_count: int, dt_old: datetime) -> None:
    """ スループット（秒間の処理件数）の表示 """

    # now: datetime = datetime.now(JST)
    now: datetime = datetime.now()
    dt_delta: timedelta = now - dt_old
    total_sec: float = dt_delta.total_seconds()
    throughput: int = int(processed_count / total_sec)

    logger.info(f"Thoughput: {throughput} doc/sec, processed_count: {processed_count}")

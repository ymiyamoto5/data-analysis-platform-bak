from datetime import datetime, timezone, timedelta

# datetime取得時に日本時間を指定する
JST = timezone(timedelta(hours=+9), "JST")


def throughput_counter(processed_count: int, dt_old: datetime) -> None:
    """ スループット（秒間の処理件数）の表示 """

    now: datetime = datetime.now(JST)
    dt_delta: timedelta = now - dt_old
    total_sec: float = dt_delta.total_seconds()
    throughput: int = int(processed_count / total_sec)

    print(f"{now}, processed_count: {processed_count}, throughput: {throughput}")

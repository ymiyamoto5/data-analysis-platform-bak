import pandas as pd
from datetime import datetime, timedelta
from backend.utils.df_to_els import df_to_els


def create_events_index(start_datetime_jst: datetime) -> None:

    start_datetime_jst_str: str = start_datetime_jst.isoformat()
    index: str = "events-" + start_datetime_jst_str.replace("-", "").replace("T", "").replace(":", "")

    start_datetime_utc: datetime = start_datetime_jst + timedelta(hours=-9)
    start_datetime_utc_str: str = start_datetime_utc.isoformat()

    # 暫定でendは1時間後
    end_datetime_utc = start_datetime_utc + timedelta(hours=1)
    end_datetime_utc_str = end_datetime_utc.isoformat()

    events = [
        {"event_id": 0, "event_type": "setup", "occurred_time": start_datetime_utc_str},
        {"event_id": 1, "event_type": "start", "occurred_time": start_datetime_utc_str},
        {"event_id": 2, "event_type": "stop", "occurred_time": end_datetime_utc_str},
        {"event_id": 3, "event_type": "recorded", "occurred_time": end_datetime_utc_str},
    ]

    df = pd.DataFrame(events)

    df_to_els(df, index)

    print("finished.")


if __name__ == "__main__":
    prefix = "events-"
    # start_datetime_jst = datetime(2021, 7, 9, 19, 0, 0, 0)
    start_datetime_jst = datetime(2021, 1, 1, 0, 0, 0, 0)
    create_events_index(start_datetime_jst)

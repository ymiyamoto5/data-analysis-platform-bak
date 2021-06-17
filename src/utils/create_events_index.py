import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from pandas.core.frame import DataFrame
from typing import Final, Tuple
from pytz import timezone

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from data_reader.data_reader import DataReader

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import common
from df_to_els import df_to_els


def create_events_index(start_datetime_jst: str) -> None:

    start_datetime_jst_str = start_datetime_jst.isoformat()
    index = "events-" + start_datetime_jst_str.replace("-", "").replace("T", "").replace(":", "")

    start_datetime_utc = start_datetime_jst + timedelta(hours=-9)
    start_datetime_utc_str = start_datetime_utc.isoformat()

    # 暫定でendは1時間後
    end_datetime_utc = start_datetime_utc + timedelta(hours=1)
    end_datetime_utc_str = end_datetime_utc.isoformat()

    # start_time_str = t[:4] + "-" + t[4:6] + "-" + t[6:8] + "T" + t[8:10] + ":" + t[10:12] + ":" + t[12:14] + ".000000"
    # # end_timeは暫定で1時間後とする
    # end_time_str = (
    #     t[:4] + "-" + t[4:6] + "-" + t[6:8] + "T" + str(int(t[8:10]) + 1) + ":" + t[10:12] + ":" + t[12:14] + ".000000"
    # )

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
    start_datetime_jst = datetime(2021, 6, 17, 13, 0, 0, 0)
    create_events_index(start_datetime_jst)

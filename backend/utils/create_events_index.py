import os
import sys
from datetime import datetime, timedelta

import pandas as pd

# backend配下のモジュールをimportするために、プロジェクト直下へのpathを通す
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from backend.elastic_manager.elastic_manager import ElasticManager


def create_events_index(prefix: str, start_datetime_jst: datetime, hours=1, is_recorded: bool = True) -> None:

    start_datetime_jst_str: str = start_datetime_jst.isoformat()
    index: str = prefix + start_datetime_jst_str.replace("-", "").replace("T", "").replace(":", "")

    start_datetime_utc: datetime = start_datetime_jst + timedelta(hours=-9)
    start_datetime_utc_str: str = start_datetime_utc.isoformat()

    # 暫定でendは1時間後
    end_datetime_utc = start_datetime_utc + timedelta(hours=hours)
    end_datetime_utc_str = end_datetime_utc.isoformat()

    events = [
        {"event_id": 0, "event_type": "setup", "occurred_time": start_datetime_utc_str},
        {"event_id": 1, "event_type": "start", "occurred_time": start_datetime_utc_str},
        {"event_id": 2, "event_type": "stop", "occurred_time": end_datetime_utc_str},
    ]

    if is_recorded:
        events.append(
            {"event_id": 3, "event_type": "recorded", "occurred_time": end_datetime_utc_str},
        )

    df = pd.DataFrame(events)

    ElasticManager.df_to_els(df=df, index=index)

    print("finished.")


if __name__ == "__main__":
    # machine_id = "machine-01"
    machine_id = "demo-machine"
    prefix = "events-" + machine_id + "-"
    start_datetime_jst = datetime(2021, 7, 9, 19, 0, 0, 0)
    # start_datetime_jst = datetime(2021, 3, 27, 14, 15, 14, 0)
    # create_events_index(prefix, start_datetime_jst, hours=2, is_recorded=False)
    create_events_index(prefix, start_datetime_jst, hours=2, is_recorded=True)

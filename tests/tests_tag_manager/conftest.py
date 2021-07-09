"""
 ==================================
  conftest.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import pytest
import pandas as pd
from datetime import datetime
from pandas.core.frame import DataFrame
from typing import List

from tag_manager.tag_manager import TagManager


@pytest.fixture
def events():
    """ tagを含んだevents_indexのデータfixture。 """

    events: List[dict] = [
        {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
        {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
        {"event_type": "pause", "start_time": "2020-12-01T00:15:00.123456", "end_time": "2020-12-01T00:16:00.123456"},
        {"event_type": "tag", "tags": "tag1", "end_time": "2020-12-01T00:17:00.123456"},
        {"event_type": "stop", "occurred_time": "2020-12-01T00:20:00.123456"},
    ]

    yield events

    del events


@pytest.fixture
def shots_df():
    """ ショット切り出ししたDataFrame fixture """

    shots: List[dict] = [
        # 切り出し区間1-1
        {
            "shot_number": 1,
            "sequential_number": 0,
            "sequential_number_by_shot": 0,
            "rawdata_sequential_number": 2,
            "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
            "displacement": 47.0,
            "load01": 1.574,
            "load02": 1.308,
            "load03": 1.363,
            "load04": 1.432,
        },
        # 切り出し区間1-2
        {
            "shot_number": 1,
            "sequential_number": 1,
            "sequential_number_by_shot": 1,
            "rawdata_sequential_number": 3,
            "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
            "displacement": 47.1,
            "load01": 1.500,
            "load02": 1.200,
            "load03": 1.300,
            "load04": 1.400,
        },
        # 切り出し区間1-3
        {
            "shot_number": 1,
            "sequential_number": 2,
            "sequential_number_by_shot": 2,
            "rawdata_sequential_number": 4,
            "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
            "displacement": 34.961,
            "load01": -0.256,
            "load02": -0.078,
            "load03": 0.881,
            "load04": 0.454,
        },
        # 切り出し区間2-1
        {
            "shot_number": 2,
            "sequential_number": 3,
            "sequential_number_by_shot": 0,
            "rawdata_sequential_number": 9,
            "timestamp": datetime(2020, 12, 1, 10, 30, 19, 111111).timestamp(),
            "displacement": 47.0,
            "load01": 1.574,
            "load02": 1.308,
            "load03": 1.363,
            "load04": 1.432,
        },
        # 切り出し区間2-2
        {
            "shot_number": 2,
            "sequential_number": 4,
            "sequential_number_by_shot": 1,
            "rawdata_sequential_number": 10,
            "timestamp": datetime(2020, 12, 1, 10, 30, 20, 111111).timestamp(),
            "displacement": 47.1,
            "load01": 1.500,
            "load02": 1.200,
            "load03": 1.300,
            "load04": 1.400,
        },
        # 切り出し区間2-3
        {
            "shot_number": 2,
            "sequential_number": 5,
            "sequential_number_by_shot": 2,
            "rawdata_sequential_number": 11,
            "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
            "displacement": 34.961,
            "load01": -0.256,
            "load02": -0.078,
            "load03": 0.881,
            "load04": 0.454,
        },
    ]

    shots_df: DataFrame = pd.DataFrame(shots)
    yield shots_df

    del shots_df
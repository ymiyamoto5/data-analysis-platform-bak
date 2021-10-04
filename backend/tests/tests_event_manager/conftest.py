"""
 ==================================
  test_cut_out_shot.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

from datetime import datetime
from typing import List

import pytest


@pytest.fixture
def events_list():
    """ events_indexのデータfixture。
        本fixtureはsetup->start->stopの基本ケースのみを用意する。
        また、rawdata_df fixtureの全データがstart-end区間に含まれる。
        pauseやtag等の特殊イベントは各テストケースで用意すること。
    """

    events: List[dict] = [
        {"event_type": "setup", "occrred_time": datetime(2020, 12, 1, 10, 30, 0, 111111).timestamp()},
        {"event_type": "start", "occrred_time": datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp()},
        {"event_type": "end", "occrred_time": datetime(2020, 12, 1, 10, 30, 30, 111111).timestamp()},
    ]

    yield events

    del events

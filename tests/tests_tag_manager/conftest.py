# """
#  ==================================
#   conftest.py
#  ==================================

#   Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
#   CONFIDENTIAL
#   Author: UNIADEX, Ltd.

# """

# import pytest
# import pandas as pd
# from datetime import datetime
# from pandas.core.frame import DataFrame
# from typing import List

# from tag_manager.tag_manager import TagManager

# @pytest.fixture
# def events_list():
#     """ events_indexのデータfixture。
#     """

#     events: List[dict] = [
#         {"event_type": "setup", "occrred_time": datetime(2020, 12, 1, 10, 30, 0, 111111).timestamp()},
#         {"event_type": "start", "occrred_time": datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp()},
#         {"event_type": "end", "occrred_time": datetime(2020, 12, 1, 10, 30, 30, 111111).timestamp()},
#     ]

#     yield events

#     del events

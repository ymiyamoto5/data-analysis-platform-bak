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
from typing import List
from pandas.core.frame import DataFrame


@pytest.fixture
def start_df():
    """荷重開始点のDataFrame fixture"""
    start_data: List[dict] = [
        {
            "timestamp": "2021-08-06T00:00:00.111000",
            "shot_number": 1,
            "load": "load01",
            "sequential_number": 100,
            "sequential_number_by_shot": 100,
            "value": 0.1,
        },
        {
            "timestamp": "2021-08-06T00:00:00.222000",
            "shot_number": 2,
            "load": "load02",
            "sequential_number": 200,
            "sequential_number_by_shot": 200,
            "value": 0.2,
        },
        {
            "timestamp": "2021-08-06T00:00:00.333000",
            "shot_number": 3,
            "load": "load03",
            "sequential_number": 300,
            "sequential_number_by_shot": 300,
            "value": 0.3,
        },
        {
            "timestamp": "2021-08-06T00:00:00.444000",
            "shot_number": 4,
            "load": "load04",
            "sequential_number": 400,
            "sequential_number_by_shot": 400,
            "value": 0.4,
        },
    ]

    start_df: DataFrame = pd.DataFrame(start_data)
    yield start_df

    del start_df


@pytest.fixture
def break_df():
    """破断開始点のDataFrame fixture"""
    break_data: List[dict] = [
        {
            "timestamp": "2021-08-06T00:00:00.444000",
            "shot_number": 1,
            "load": "load01",
            "sequential_number": 100,
            "sequential_number_by_shot": 100,
            "value": 0.1,
            "break_channels": ["load03", "load04"],
        },
        {
            "timestamp": "2021-08-06T00:00:00.444000",
            "shot_number": 2,
            "load": "load02",
            "sequential_number": 200,
            "sequential_number_by_shot": 200,
            "value": 0.2,
            "break_channels": ["load03", "load04"],
        },
        {
            "timestamp": "2021-08-06T00:00:00.444000",
            "shot_number": 3,
            "load": "load03",
            "sequential_number": 300,
            "sequential_number_by_shot": 300,
            "value": 0.3,
            "break_channels": ["load03", "load04"],
        },
        {
            "timestamp": "2021-08-06T00:00:00.444000",
            "shot_number": 4,
            "load": "load04",
            "sequential_number": 400,
            "sequential_number_by_shot": 400,
            "value": 0.4,
            "break_channels": ["load03", "load04"],
        },
    ]

    break_df: DataFrame = pd.DataFrame(break_data)
    yield break_df

    del break_df

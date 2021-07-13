"""
 ==================================
  test_analyze.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import pandas as pd
from typing import List
from pandas.core.frame import DataFrame

from analyzer.analyzer import Analyzer


class TestExtractBreakChannels:
    def test_normal_1(self):
        target: str = "dummy"
        shots_df: DataFrame = pd.DataFrame([])
        shots_meta_df: DataFrame = pd.DataFrame([])

        analyzer = Analyzer(target, shots_df, shots_meta_df, None)

        values: List[float] = [1.0, 2.0, 3.0, 4.0]

        actual = analyzer._extract_break_channels(values)
        expedted = ("load01", "load02")

        assert actual == expedted

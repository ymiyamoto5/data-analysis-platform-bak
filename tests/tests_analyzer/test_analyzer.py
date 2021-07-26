"""
 ==================================
  test_analyze.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import pytest
import pandas as pd
from typing import List
from pandas.core.frame import DataFrame

from analyzer.analyzer import Analyzer


class TestExtractBreakChannels:
    test_data = [
        ([1.0, 2.0, 3.0, 4.0], ("load01", "load02")),
        ([2.0, 1.0, 3.0, 4.0], ("load01", "load02")),
        ([3.0, 4.0, 1.0, 2.0], ("load03", "load04")),
        ([3.0, 4.0, 2.0, 1.0], ("load03", "load04")),
    ]

    @pytest.mark.parametrize("values, expected", test_data)
    def test_normal(self, values, expected):
        target: str = "dummy"
        shots_df: DataFrame = pd.DataFrame([])
        shots_meta_df: DataFrame = pd.DataFrame([])

        analyzer = Analyzer(target, shots_df, shots_meta_df, None)
        actual = analyzer._extract_break_channels(values)

        assert actual == expected


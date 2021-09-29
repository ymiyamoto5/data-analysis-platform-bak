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
from pandas.core.frame import DataFrame
from typing import List, Optional, Tuple
from pandas.testing import assert_frame_equal
from backend.analyzer.analyzer import Analyzer
from backend.elastic_manager.elastic_manager import ElasticManager


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


class TestStartBreakDiff:
    def test_normal_no_exclude_shots(self, mocker, start_df, break_df):
        """正常系：荷重開始と破断開始の時間差計算（除外ショットなし）"""
        # mocker
        mocker.patch.object(ElasticManager, "delete_exists_index")
        mocker.patch.object(ElasticManager, "bulk_insert")

        target: str = "dummy"
        shots_df: DataFrame = pd.DataFrame([])
        shots_meta_df: DataFrame = pd.DataFrame([])
        exclude_shots: Optional[Tuple[int]] = None

        analyzer = Analyzer(target, shots_df, shots_meta_df, exclude_shots)

        actual = analyzer.start_break_diff(start_df, break_df)
        # indexをreset
        actual = actual.reset_index(drop=True)

        expected_data: List[dict] = [
            {"timestamp": "2021-08-06T00:00:00.111000", "shot_number": 1, "load": "load01", "diff": 0.333},
            {"timestamp": "2021-08-06T00:00:00.222000", "shot_number": 2, "load": "load02", "diff": 0.222},
            {"timestamp": "2021-08-06T00:00:00.333000", "shot_number": 3, "load": "load03", "diff": 0.111},
            {"timestamp": "2021-08-06T00:00:00.444000", "shot_number": 4, "load": "load04", "diff": 0.0},
        ]

        expected: DataFrame = pd.DataFrame(expected_data)

        assert_frame_equal(actual, expected)

    def test_normal_specify_exclude_shots(self, mocker, start_df, break_df):
        """正常系：荷重開始と破断開始の時間差計算（除外ショットあり）"""
        # mocker
        mocker.patch.object(ElasticManager, "delete_exists_index")
        mocker.patch.object(ElasticManager, "bulk_insert")

        target: str = "dummy"
        shots_df: DataFrame = pd.DataFrame([])
        shots_meta_df: DataFrame = pd.DataFrame([])
        exclude_shots: Optional[Tuple[int, ...]] = (1, 3)

        analyzer = Analyzer(target, shots_df, shots_meta_df, exclude_shots)

        actual = analyzer.start_break_diff(start_df, break_df)
        # indexをreset
        actual = actual.reset_index(drop=True)

        expected_data: List[dict] = [
            {"timestamp": "2021-08-06T00:00:00.222000", "shot_number": 2, "load": "load02", "diff": 0.222},
            {"timestamp": "2021-08-06T00:00:00.444000", "shot_number": 4, "load": "load04", "diff": 0.0},
        ]

        expected: DataFrame = pd.DataFrame(expected_data)

        assert_frame_equal(actual, expected)

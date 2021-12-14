"""
 ==================================
  test_cut_out_shot.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

from datetime import datetime
from decimal import Decimal
from typing import List

import numpy as np
import pandas as pd
import pytest
from backend.app.models.data_collect_history_event import DataCollectHistoryEvent
from backend.common import common
from backend.cut_out_shot.stroke_displacement_cutter import StrokeDisplacementCutter
from backend.data_converter.data_converter import DataConverter
from backend.elastic_manager.elastic_manager import ElasticManager
from pandas.core.frame import DataFrame
from pandas.testing import assert_frame_equal


class TestAutoCutOutShot:
    def test_exec(self, stroke_displacement_target, pkl_files):
        """自動ショット切り出し実行。実行できればOKとする。"""

        machine_id = "unittest-machine"
        shots_index: str = f"shots-{machine_id}-20201201103011-data"
        shots_meta_index: str = f"shots-{machine_id}-20201201103011-meta"

        pkl_file_list = []
        pkl_file_list.append(pkl_files.tmp_pkl_1._str)
        pkl_file_list.append(pkl_files.tmp_pkl_2._str)

        stroke_displacement_target.auto_cut_out_shot(pkl_file_list, shots_index, shots_meta_index)

        ElasticManager.delete_index(shots_index)
        ElasticManager.delete_index(shots_meta_index)

        assert True


class TestExcludeSetupInterval:
    def test_normal_exclude_all(self, stroke_displacement_target, rawdata_df):
        """正常系：段取区間除外（全データ）"""

        collect_start_time: Decimal = Decimal(datetime(2020, 12, 1, 10, 30, 22, 111112).timestamp())
        actual: DataFrame = stroke_displacement_target._exclude_setup_interval(rawdata_df, collect_start_time)

        expected: DataFrame = rawdata_df.drop(index=rawdata_df.index[:])

        assert_frame_equal(actual, expected)

    def test_normal_exclude_some_data(self, stroke_displacement_target, rawdata_df):
        """正常系：段取区間除外（部分データ）"""

        collect_start_time: Decimal = Decimal(datetime(2020, 12, 1, 10, 30, 20, 0).timestamp())
        actual: DataFrame = stroke_displacement_target._exclude_setup_interval(rawdata_df, collect_start_time)

        expected: DataFrame = rawdata_df.drop(index=rawdata_df.index[:-3])

        assert_frame_equal(actual, expected)

    def test_normal_not_exclude(self, stroke_displacement_target, rawdata_df):
        """正常系：段取区間除外（除外対象なし）"""

        # rawdata_dfの最初のサンプルと同時刻
        collect_start_time: Decimal = Decimal(datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp())
        actual: DataFrame = stroke_displacement_target._exclude_setup_interval(rawdata_df, collect_start_time)

        expected: DataFrame = rawdata_df

        assert_frame_equal(actual, expected)


class TestExcludePauseInterval:
    def test_normal_exclude_one_interval(self, stroke_displacement_target, rawdata_df):
        """正常系：中断区間(1回)除外"""

        start_time = datetime(2020, 12, 1, 10, 30, 11, 111111)
        end_time = datetime(2020, 12, 1, 10, 30, 21, 111111)

        pause_events: List[DataCollectHistoryEvent] = [
            DataCollectHistoryEvent(
                event_id=2,
                event_name=common.COLLECT_STATUS.PAUSE.value,
                occurred_at=start_time,
                ended_at=end_time,
            ),
        ]

        actual: DataFrame = stroke_displacement_target._exclude_pause_interval(rawdata_df, pause_events)

        # 最初と最後のサンプルを以外すべて除去される。
        expected: DataFrame = pd.concat([rawdata_df[:1], rawdata_df[-1:]], axis=0)

        assert_frame_equal(actual, expected)

    def test_normal_exclude_two_interval(self, stroke_displacement_target, rawdata_df):
        """正常系：中断区間(2回)除外"""

        start_time_1 = datetime(2020, 12, 1, 10, 30, 11, 111111)
        end_time_1 = datetime(2020, 12, 1, 10, 30, 15, 111111)
        start_time_2 = datetime(2020, 12, 1, 10, 30, 16, 111111)
        end_time_2 = datetime(2020, 12, 1, 10, 30, 21, 111111)

        pause_events: List[DataCollectHistoryEvent] = [
            DataCollectHistoryEvent(
                event_id=2,
                event_name=common.COLLECT_STATUS.PAUSE.value,
                occurred_at=start_time_1,
                ended_at=end_time_1,
            ),
            DataCollectHistoryEvent(
                event_id=3,
                event_name=common.COLLECT_STATUS.PAUSE.value,
                occurred_at=start_time_2,
                ended_at=end_time_2,
            ),
        ]

        actual: DataFrame = stroke_displacement_target._exclude_pause_interval(rawdata_df, pause_events)

        # 最初と最後のサンプルを以外すべて除去される。
        expected: DataFrame = pd.concat([rawdata_df[:1], rawdata_df[-1:]], axis=0)

        assert_frame_equal(actual, expected)


class TestSetToNoneForLowSpm:
    def test_normal(self, stroke_displacement_target, shots_meta_df):
        """最低spm (15spm) を下回る spm は None に設定する"""

        stroke_displacement_target.shots_meta_df = shots_meta_df
        stroke_displacement_target._set_to_none_for_low_spm()

        actual_df: DataFrame = stroke_displacement_target.shots_meta_df

        expected = [
            {"shot_number": 1, "spm": np.nan, "num_of_samples_in_cut_out": 400001},
            {"shot_number": 2, "spm": 80.0, "num_of_samples_in_cut_out": 3000},
            {"shot_number": 3, "spm": 40.0, "num_of_samples_in_cut_out": 6000},
            {"shot_number": 4, "spm": 60.0, "num_of_samples_in_cut_out": 4000},
        ]

        expected_df = pd.DataFrame(expected)

        assert_frame_equal(actual_df, expected_df)


class TestExcludeOverSample:
    def test_normal_exclude_one_shot(self, stroke_displacement_target, rawdata_df, shots_meta_df, stroke_displacement_sensors):
        """最大サンプル数（60/15*100k=400,000）を超えるショットを除外する。
        shots_meta_df fixtureのshot_number:1は400,001サンプルとしているため除外される。
        """

        stroke_displacement_target.shots_meta_df = shots_meta_df

        # サンプル切り出し
        cutter = StrokeDisplacementCutter(47.0, 34, 0.1, sensors=stroke_displacement_sensors)
        cutter.cut_out_shot(rawdata_df)
        cut_out_targets = cutter.cut_out_targets
        cut_out_targets_df = pd.DataFrame(cut_out_targets)

        actual: DataFrame = stroke_displacement_target._exclude_over_sample(cut_out_targets_df)

        expected: DataFrame = cut_out_targets_df[cut_out_targets_df.shot_number == 2]

        assert_frame_equal(actual, expected)

    def test_normal_not_exists_over_sample(self, stroke_displacement_target, rawdata_df, shots_meta_df, stroke_displacement_sensors):
        """最大サンプル数を超えるショットがなかった場合、何も除外されずに元のDataFrameが返る"""

        # 全ショットが最大サンプル以下になるようデータ書き換え
        shots_meta_df.at[0, "num_of_samples_in_cut_out"] = 5000
        stroke_displacement_target.shots_meta_df = shots_meta_df

        # サンプル切り出し
        cutter = StrokeDisplacementCutter(47.0, 34, 0.1, sensors=stroke_displacement_sensors)
        cutter.cut_out_shot(rawdata_df)
        cut_out_targets = cutter.cut_out_targets
        cut_out_targets_df = pd.DataFrame(cut_out_targets)

        actual: DataFrame = stroke_displacement_target._exclude_over_sample(cut_out_targets_df)

        expected: DataFrame = cut_out_targets_df

        assert_frame_equal(actual, expected)


class TestApplyPhysicalConversionFormula:
    def test_normal(self, mocker, stroke_displacement_target, rawdata_df):
        """正常系：lambda式適用"""

        # 全データを見る必要はないので一部スライス
        target_df: DataFrame = rawdata_df[:3].copy()

        mocker.patch.object(DataConverter, "get_physical_conversion_formula", return_value=lambda x: x + 1.0)

        actual_df: DataFrame = stroke_displacement_target._apply_physical_conversion_formula(target_df)

        expected = [
            {
                "sequential_number": 0,
                "timestamp": datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp(),
                "stroke_displacement": 50.284,
                "load01": 1.223,
                "load02": 1.211,
                "load03": 1.200,
                "load04": 1.218,
            },
            # 切り出し区間前2
            {
                "sequential_number": 1,
                "timestamp": datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp(),
                "stroke_displacement": 48.534,
                "load01": 1.155,
                "load02": 1.171,
                "load03": 1.180,
                "load04": 1.146,
            },
            # 切り出し区間1-1
            {
                "sequential_number": 2,
                "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
                "stroke_displacement": 48.0,
                "load01": 2.574,
                "load02": 2.308,
                "load03": 2.363,
                "load04": 2.432,
            },
        ]

        expected_df = pd.DataFrame(expected)

        assert_frame_equal(actual_df, expected_df)


class TestSetStartSequentialNumber:
    def test_normal_1(self, stroke_displacement_target):
        actual: int = stroke_displacement_target._set_start_sequential_number(start_sequential_number=None, rawdata_count=10)
        assert actual == 0

    def test_normal_2(self, stroke_displacement_target):
        actual: int = stroke_displacement_target._set_start_sequential_number(start_sequential_number=3, rawdata_count=10)
        assert actual == 3

    def test_exception_1(self, stroke_displacement_target):
        with pytest.raises(SystemExit):
            stroke_displacement_target._set_start_sequential_number(start_sequential_number=10, rawdata_count=10)

    def test_exception_2(self, stroke_displacement_target):
        with pytest.raises(SystemExit):
            stroke_displacement_target._set_start_sequential_number(start_sequential_number=-1, rawdata_count=10)


class TestSetEndSequentialNumber:
    def test_normal_1(self, stroke_displacement_target):
        actual: int = stroke_displacement_target._set_end_sequential_number(
            start_sequential_number=0, end_sequential_number=None, rawdata_count=10
        )
        assert actual == 10

    def test_normal_2(self, stroke_displacement_target):
        actual: int = stroke_displacement_target._set_end_sequential_number(
            start_sequential_number=0, end_sequential_number=8, rawdata_count=10
        )
        assert actual == 8

    def test_exception_1(self, stroke_displacement_target):
        with pytest.raises(SystemExit):
            stroke_displacement_target._set_end_sequential_number(start_sequential_number=0, end_sequential_number=10, rawdata_count=10)

    def test_exception_2(self, stroke_displacement_target):
        with pytest.raises(SystemExit):
            stroke_displacement_target._set_end_sequential_number(start_sequential_number=0, end_sequential_number=0, rawdata_count=10)

    def test_exception_3(self, stroke_displacement_target):
        with pytest.raises(SystemExit):
            stroke_displacement_target._set_end_sequential_number(start_sequential_number=5, end_sequential_number=3, rawdata_count=10)


class TestExcludeNonTargetInterval:
    def test_normal_1(self, stroke_displacement_target, rawdata_df):
        actual_df = stroke_displacement_target._exclude_non_target_interval(rawdata_df, 3, 5)
        actual_df = actual_df.reset_index(drop=True)

        expected = [
            {
                "sequential_number": 3,
                "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
                "stroke_displacement": 47.1,
                "load01": 1.500,
                "load02": 1.200,
                "load03": 1.300,
                "load04": 1.400,
            },
            # 切り出し区間1-3
            {
                "sequential_number": 4,
                "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
                "stroke_displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
            },
            # 切り出し区間後1
            {
                "sequential_number": 5,
                "timestamp": datetime(2020, 12, 1, 10, 30, 15, 111111).timestamp(),
                "stroke_displacement": 30.599,
                "load01": -0.130,
                "load02": 0.020,
                "load03": 0.483,
                "load04": 0.419,
            },
        ]

        expected_df = pd.DataFrame(expected)

        assert_frame_equal(actual_df, expected_df)

    def test_normal_2(self, stroke_displacement_target, rawdata_df):
        actual_df = stroke_displacement_target._exclude_non_target_interval(rawdata_df, 0, 12)
        actual_df = actual_df.reset_index(drop=True)

        expected_df = rawdata_df

        assert_frame_equal(actual_df, expected_df)

    def test_exception(self, stroke_displacement_target, rawdata_df):
        """異常系：範囲外のsequential_number指定。通常はありえない"""

        actual_df = stroke_displacement_target._exclude_non_target_interval(rawdata_df, 0, 20)
        actual_df = actual_df.reset_index(drop=True)

        expected_df = rawdata_df

        assert_frame_equal(actual_df, expected_df)

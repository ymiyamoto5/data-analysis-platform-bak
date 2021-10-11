"""
 ==================================
  test_tag_manager.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd
import pytest  # type: ignore
from backend.event_manager.event_manager import EventManager
from backend.tag_manager.tag_manager import TagManager
from pandas.testing import assert_frame_equal


class TestGetTagEvent:
    """イベント情報を取得するテスト"""

    events_normal_1 = (
        [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
            {"event_type": "tag", "tag": "tag1", "end_time": "2020-12-01T00:17:00.123456"},
        ],
    )

    @pytest.mark.parametrize("events", events_normal_1)
    def test_normal_single_tag_event(self, events):
        actual = EventManager.get_tag_events(events)

        expected_start_time = datetime(2020, 12, 1, 0, 15, 0, 123456).timestamp()
        expected_end_time = datetime(2020, 12, 1, 0, 17, 0, 123456).timestamp()

        expected = [
            {"event_type": "tag", "tag": "tag1", "start_time": expected_start_time, "end_time": expected_end_time},
        ]

        assert actual == expected

    events_normal_2 = (
        [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
            {"event_type": "tag", "tag": "tag1", "end_time": "2020-12-01T00:17:00.123456"},
            {"event_type": "tag", "tag": "tag2", "end_time": "2020-12-01T00:18:00.123456"},
        ],
    )

    @pytest.mark.parametrize("events", events_normal_2)
    def test_normal_multi_tag_event(self, events):
        actual = EventManager.get_tag_events(events)

        expected_tag1_start_time = datetime(2020, 12, 1, 0, 15, 0, 123456).timestamp()
        expected_tag1_end_time = datetime(2020, 12, 1, 0, 17, 0, 123456).timestamp()
        expected_tag2_start_time = datetime(2020, 12, 1, 0, 16, 0, 123456).timestamp()
        expected_tag2_end_time = datetime(2020, 12, 1, 0, 18, 0, 123456).timestamp()

        expected = [
            {
                "event_type": "tag",
                "tag": "tag1",
                "start_time": expected_tag1_start_time,
                "end_time": expected_tag1_end_time,
            },
            {
                "event_type": "tag",
                "tag": "tag2",
                "start_time": expected_tag2_start_time,
                "end_time": expected_tag2_end_time,
            },
        ]

        assert actual == expected

    events_none: Tuple[List[Dict[str, str]], List[Any]] = (
        [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
            {"event_type": "stop", "occurred_time": "2020-12-01T00:20:00.123456"},
        ],
        [],
    )

    @pytest.mark.parametrize("events", events_none)
    def test_no_tag_event(self, events):
        actual = EventManager.get_tag_events(events)

        expected = []

        assert actual == expected

    events_exception = (
        [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
            {
                "event_type": "pause",
                "start_time": "2020-12-01T00:15:00.123456",
                "end_time": "2020-12-01T00:16:00.123456",
            },
            {"event_type": "tag", "tag": "tag1"},
            {"event_type": "stop", "occurred_time": "2020-12-01T00:20:00.123456"},
        ],
    )

    @pytest.mark.parametrize("events", events_exception)
    def test_no_end_time(self, events):
        with pytest.raises(KeyError):
            EventManager.get_tag_events(events)


class TestAddTagsFromEvents:
    def test_normal_no_tags_in_range(self, shots_df, events_not_range):
        tm = TagManager()
        tag_events = EventManager.get_tag_events(events_not_range)
        actual_df = tm._add_tags_from_events(shots_df, tag_events)

        expected = [
            # 切り出し区間1-1
            {
                "shot_number": 1,
                "sequential_number": 0,
                "sequential_number_by_shot": 0,
                "rawdata_sequential_number": 2,
                "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
                "stroke_displacement": 47.0,
                "load01": 1.574,
                "load02": 1.308,
                "load03": 1.363,
                "load04": 1.432,
                "tags": [],
            },
            # 切り出し区間1-2
            {
                "shot_number": 1,
                "sequential_number": 1,
                "sequential_number_by_shot": 1,
                "rawdata_sequential_number": 3,
                "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
                "stroke_displacement": 47.1,
                "load01": 1.500,
                "load02": 1.200,
                "load03": 1.300,
                "load04": 1.400,
                "tags": [],
            },
            # 切り出し区間1-3
            {
                "shot_number": 1,
                "sequential_number": 2,
                "sequential_number_by_shot": 2,
                "rawdata_sequential_number": 4,
                "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
                "stroke_displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
                "tags": [],
            },
            # 切り出し区間2-1
            {
                "shot_number": 2,
                "sequential_number": 3,
                "sequential_number_by_shot": 0,
                "rawdata_sequential_number": 9,
                "timestamp": datetime(2020, 12, 1, 10, 30, 19, 111111).timestamp(),
                "stroke_displacement": 47.0,
                "load01": 1.574,
                "load02": 1.308,
                "load03": 1.363,
                "load04": 1.432,
                "tags": [],
            },
            # 切り出し区間2-2
            {
                "shot_number": 2,
                "sequential_number": 4,
                "sequential_number_by_shot": 1,
                "rawdata_sequential_number": 10,
                "timestamp": datetime(2020, 12, 1, 10, 30, 20, 111111).timestamp(),
                "stroke_displacement": 47.1,
                "load01": 1.500,
                "load02": 1.200,
                "load03": 1.300,
                "load04": 1.400,
                "tags": [],
            },
            # 切り出し区間2-3
            {
                "shot_number": 2,
                "sequential_number": 5,
                "sequential_number_by_shot": 2,
                "rawdata_sequential_number": 11,
                "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
                "stroke_displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
                "tags": [],
            },
        ]

        expected_df = pd.DataFrame(expected)

        assert_frame_equal(actual_df, expected_df)

    def test_normal_one_tags_in_range(self, shots_df, events_in_range_1):
        """最初の2サンプルに対し1つのtagを付与する"""

        tm = TagManager()
        tag_events = EventManager.get_tag_events(events_in_range_1)
        actual_df = tm._add_tags_from_events(shots_df, tag_events)

        expected = [
            # 切り出し区間1-1
            {
                "shot_number": 1,
                "sequential_number": 0,
                "sequential_number_by_shot": 0,
                "rawdata_sequential_number": 2,
                "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
                "stroke_displacement": 47.0,
                "load01": 1.574,
                "load02": 1.308,
                "load03": 1.363,
                "load04": 1.432,
                "tags": ["tag1"],
            },
            # 切り出し区間1-2
            {
                "shot_number": 1,
                "sequential_number": 1,
                "sequential_number_by_shot": 1,
                "rawdata_sequential_number": 3,
                "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
                "stroke_displacement": 47.1,
                "load01": 1.500,
                "load02": 1.200,
                "load03": 1.300,
                "load04": 1.400,
                "tags": ["tag1"],
            },
            # 切り出し区間1-3
            {
                "shot_number": 1,
                "sequential_number": 2,
                "sequential_number_by_shot": 2,
                "rawdata_sequential_number": 4,
                "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
                "stroke_displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
                "tags": [],
            },
            # 切り出し区間2-1
            {
                "shot_number": 2,
                "sequential_number": 3,
                "sequential_number_by_shot": 0,
                "rawdata_sequential_number": 9,
                "timestamp": datetime(2020, 12, 1, 10, 30, 19, 111111).timestamp(),
                "stroke_displacement": 47.0,
                "load01": 1.574,
                "load02": 1.308,
                "load03": 1.363,
                "load04": 1.432,
                "tags": [],
            },
            # 切り出し区間2-2
            {
                "shot_number": 2,
                "sequential_number": 4,
                "sequential_number_by_shot": 1,
                "rawdata_sequential_number": 10,
                "timestamp": datetime(2020, 12, 1, 10, 30, 20, 111111).timestamp(),
                "stroke_displacement": 47.1,
                "load01": 1.500,
                "load02": 1.200,
                "load03": 1.300,
                "load04": 1.400,
                "tags": [],
            },
            # 切り出し区間2-3
            {
                "shot_number": 2,
                "sequential_number": 5,
                "sequential_number_by_shot": 2,
                "rawdata_sequential_number": 11,
                "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
                "stroke_displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
                "tags": [],
            },
        ]

        expected_df = pd.DataFrame(expected)

        assert_frame_equal(actual_df, expected_df)

    def test_normal_two_tags_in_range(self, shots_df, events_in_range_2):
        """最初の2サンプルに対し1つのtagを付与する"""

        tm = TagManager()
        tag_events = EventManager.get_tag_events(events_in_range_2)
        actual_df = tm._add_tags_from_events(shots_df, tag_events)

        expected = [
            # 切り出し区間1-1
            {
                "shot_number": 1,
                "sequential_number": 0,
                "sequential_number_by_shot": 0,
                "rawdata_sequential_number": 2,
                "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
                "stroke_displacement": 47.0,
                "load01": 1.574,
                "load02": 1.308,
                "load03": 1.363,
                "load04": 1.432,
                "tags": ["tag1", "tag2"],
            },
            # 切り出し区間1-2
            {
                "shot_number": 1,
                "sequential_number": 1,
                "sequential_number_by_shot": 1,
                "rawdata_sequential_number": 3,
                "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
                "stroke_displacement": 47.1,
                "load01": 1.500,
                "load02": 1.200,
                "load03": 1.300,
                "load04": 1.400,
                "tags": ["tag1", "tag2"],
            },
            # 切り出し区間1-3
            {
                "shot_number": 1,
                "sequential_number": 2,
                "sequential_number_by_shot": 2,
                "rawdata_sequential_number": 4,
                "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
                "stroke_displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
                "tags": ["tag2"],
            },
            # 切り出し区間2-1
            {
                "shot_number": 2,
                "sequential_number": 3,
                "sequential_number_by_shot": 0,
                "rawdata_sequential_number": 9,
                "timestamp": datetime(2020, 12, 1, 10, 30, 19, 111111).timestamp(),
                "stroke_displacement": 47.0,
                "load01": 1.574,
                "load02": 1.308,
                "load03": 1.363,
                "load04": 1.432,
                "tags": ["tag2"],
            },
            # 切り出し区間2-2
            {
                "shot_number": 2,
                "sequential_number": 4,
                "sequential_number_by_shot": 1,
                "rawdata_sequential_number": 10,
                "timestamp": datetime(2020, 12, 1, 10, 30, 20, 111111).timestamp(),
                "stroke_displacement": 47.1,
                "load01": 1.500,
                "load02": 1.200,
                "load03": 1.300,
                "load04": 1.400,
                "tags": ["tag2"],
            },
            # 切り出し区間2-3
            {
                "shot_number": 2,
                "sequential_number": 5,
                "sequential_number_by_shot": 2,
                "rawdata_sequential_number": 11,
                "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
                "stroke_displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
                "tags": [],
            },
        ]

        expected_df = pd.DataFrame(expected)

        assert_frame_equal(actual_df, expected_df)

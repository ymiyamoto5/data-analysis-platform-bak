"""
 ==================================
  test_tag_manager.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import pytest
import pandas as pd
from datetime import datetime
from typing import List
from pandas.core.frame import DataFrame
from pandas.testing import assert_frame_equal
import numpy as np

from tag_manager.tag_manager import TagManager


class TestGetTagEvent:

    events_normal_1 = (
        [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
            {
                "event_type": "pause",
                "start_time": "2020-12-01T00:15:00.123456",
                "end_time": "2020-12-01T00:16:00.123456",
            },
            {"event_type": "tag", "tags": "tag1", "end_time": "2020-12-01T00:17:00.123456"},
            {"event_type": "stop", "occurred_time": "2020-12-01T00:20:00.123456"},
        ],
    )

    @pytest.mark.parametrize("events", events_normal_1)
    def test_normal_single_tag_event(self, target, events):
        target.back_seconds_for_tagging = 120
        actual = target._get_tag_events(events)

        expected_start_time = datetime(2020, 12, 1, 0, 15, 0, 123456)
        expected_end_time = datetime(2020, 12, 1, 0, 17, 0, 123456)

        expected = [
            {"event_type": "tag", "tags": "tag1", "start_time": expected_start_time, "end_time": expected_end_time},
        ]

        assert actual == expected

    events_normal_2 = (
        [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
            {"event_type": "tag", "tags": "tag1", "end_time": "2020-12-01T00:17:00.123456"},
            {"event_type": "tag", "tags": "tag2", "end_time": "2020-12-01T00:18:00.123456"},
        ],
    )

    @pytest.mark.parametrize("events", events_normal_2)
    def test_normal_multi_tag_event(self, target, events):
        target.back_seconds_for_tagging = 120
        actual = target._get_tag_events(events)

        expected_tag1_start_time = datetime(2020, 12, 1, 0, 15, 0, 123456)
        expected_tag1_end_time = datetime(2020, 12, 1, 0, 17, 0, 123456)
        expected_tag2_start_time = datetime(2020, 12, 1, 0, 16, 0, 123456)
        expected_tag2_end_time = datetime(2020, 12, 1, 0, 18, 0, 123456)

        expected = [
            {
                "event_type": "tag",
                "tags": "tag1",
                "start_time": expected_tag1_start_time,
                "end_time": expected_tag1_end_time,
            },
            {
                "event_type": "tag",
                "tags": "tag2",
                "start_time": expected_tag2_start_time,
                "end_time": expected_tag2_end_time,
            },
        ]

        assert actual == expected

    events_none = (
        [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
            {"event_type": "stop", "occurred_time": "2020-12-01T00:20:00.123456"},
        ],
        [],
    )

    @pytest.mark.parametrize("events", events_none)
    def test_no_tag_event(self, target, events):
        target.back_seconds_for_tagging = 120
        actual = target._get_tag_events(events)

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
            {"event_type": "tag", "tags": "tag1"},
            {"event_type": "stop", "occurred_time": "2020-12-01T00:20:00.123456"},
        ],
    )

    @pytest.mark.parametrize("events", events_exception)
    def test_no_end_time(self, target, events):
        target.back_seconds_for_tagging = 120
        with pytest.raises(KeyError):
            target._get_tag_events(events)


class TestGetTags:
    def test_normal_one_tag_event(self, target):
        """ 正常系：事象記録が1回あり、対象サンプルがその事象区間に含まれる """

        rawdata_timestamp: float = datetime(2020, 12, 1, 10, 30, 10, 000000).timestamp()
        start_time: float = datetime(2020, 12, 1, 10, 28, 11, 111111).timestamp()
        end_time: float = datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp()

        tag_events = [
            {"event_type": "tag", "tag": "異常A", "start_time": start_time, "end_time": end_time},
        ]

        actual: List[str] = target._get_tags(rawdata_timestamp, tag_events)

        expected: List[str] = ["異常A"]

        assert actual == expected

    def test_normal_two_tag_events(self, target):
        """ 正常系：事象記録が2回あり、対象サンプルが両方の事象区間に含まれる """

        rawdata_timestamp: float = datetime(2020, 12, 1, 10, 30, 10, 000000).timestamp()

        start_time_1: float = datetime(2020, 12, 1, 10, 28, 10, 111111).timestamp()
        end_time_1: float = datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp()
        start_time_2: float = datetime(2020, 12, 1, 10, 28, 11, 111111).timestamp()
        end_time_2: float = datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp()

        tag_events = [
            {"event_type": "tag", "tag": "異常A", "start_time": start_time_1, "end_time": end_time_1},
            {"event_type": "tag", "tag": "異常B", "start_time": start_time_2, "end_time": end_time_2},
        ]

        actual: List[str] = target._get_tags(rawdata_timestamp, tag_events)

        expected: List[str] = ["異常A", "異常B"]

        assert actual == expected

    def test_normal_not_include_tag_range(self, target):
        """ 正常系：事象記録が1回あり、対象サンプルがその事象区間に含まれない """

        rawdata_timestamp: float = datetime(2020, 12, 1, 10, 35, 10, 000000).timestamp()
        start_time: float = datetime(2020, 12, 1, 10, 28, 11, 111111).timestamp()
        end_time: float = datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp()

        tag_events = [
            {"event_type": "tag", "tag": "異常A", "start_time": start_time, "end_time": end_time},
        ]

        actual: List[str] = target._get_tags(rawdata_timestamp, tag_events)

        expected: List[str] = []

        assert actual == expected


class TestAddTags:
    def test_normal_one_target(self, target, mocker):
        """ 正常系： cut_out_target 1件に対してタグ付け """

        timestamp: float = datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp()
        target.cut_out_targets = [
            {"timestamp": timestamp, "tags": []},
        ]

        tags: List[str] = ["異常A", "異常B"]

        mocker.patch.object(CutOutShot, "_get_tags", return_value=tags)

        # mockするので実際は使われない。
        start_time_1: float = datetime(2020, 12, 1, 10, 28, 10, 111111).timestamp()
        end_time_1: float = datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp()
        start_time_2: float = datetime(2020, 12, 1, 10, 28, 11, 111111).timestamp()
        end_time_2: float = datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp()
        tag_events = [
            {"event_type": "tag", "tag": "異常A", "start_time": start_time_1, "end_time": end_time_1},
            {"event_type": "tag", "tag": "異常B", "start_time": start_time_2, "end_time": end_time_2},
        ]

        target._add_tags(tag_events)
        actual = target.cut_out_targets

        expected = [
            {"timestamp": timestamp, "tags": ["異常A", "異常B"]},
        ]

        assert actual == expected

    def test_normal_two_targets(self, target, mocker):
        """ 正常系： cut_out_target 2件に対してタグ付け """

        timestamp_1: float = datetime(2020, 12, 1, 10, 30, 11, 000000).timestamp()
        timestamp_2: float = datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp()
        target.cut_out_targets = [
            {"timestamp": timestamp_1, "tags": []},
            {"timestamp": timestamp_2, "tags": []},
        ]

        tags: List[str] = ["異常A", "異常B"]

        mocker.patch.object(CutOutShot, "_get_tags", return_value=tags)

        # mockするので実際は使われない。
        start_time_1: float = datetime(2020, 12, 1, 10, 28, 10, 111111).timestamp()
        end_time_1: float = datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp()
        start_time_2: float = datetime(2020, 12, 1, 10, 28, 11, 111111).timestamp()
        end_time_2: float = datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp()
        tag_events = [
            {"event_type": "tag", "tag": "異常A", "start_time": start_time_1, "end_time": end_time_1},
            {"event_type": "tag", "tag": "異常B", "start_time": start_time_2, "end_time": end_time_2},
        ]

        target._add_tags(tag_events)
        actual = target.cut_out_targets

        expected = [
            {"timestamp": timestamp_1, "tags": ["異常A", "異常B"]},
            {"timestamp": timestamp_2, "tags": ["異常A", "異常B"]},
        ]

        assert actual == expected

"""
 ==================================
  test_event_manager.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import pytest  # type: ignore
from datetime import datetime
from event_manager.event_manager import EventManager  # type: ignore


class TestGetCollectStartTime:
    events_normal = (
        [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
            {"event_type": "stop", "occurred_time": "2020-12-01T00:20:00.123456"},
        ],
        [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
        ],
    )

    events_normal_ids = [f"events-{x}" for x in events_normal]

    @pytest.mark.parametrize("events", events_normal, ids=events_normal_ids)
    def test_normal(self, events):
        actual = EventManager.get_collect_start_time(events)

        expected = datetime(2020, 12, 1, 0, 10, 0, 123456).timestamp()

        assert actual == expected

    events_exception = ([{"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"}],)

    @pytest.mark.parametrize("events", events_exception)
    def test_no_start_event(self, events):
        with pytest.raises(SystemExit):
            EventManager.get_collect_start_time(events)


class TestGetPauseEvents:
    events_normal_1 = (
        [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
            {
                "event_type": "pause",
                "start_time": "2020-12-01T00:15:00.123456",
                "end_time": "2020-12-01T00:16:00.123456",
            },
            {"event_type": "stop", "occurred_time": "2020-12-01T00:20:00.123456"},
        ],
        [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
            {
                "event_type": "pause",
                "start_time": "2020-12-01T00:15:00.123456",
                "end_time": "2020-12-01T00:16:00.123456",
            },
        ],
    )

    @pytest.mark.parametrize("events", events_normal_1)
    def test_normal(self, events):
        actual = EventManager.get_pause_events(events)

        expected_start_time = datetime(2020, 12, 1, 0, 15, 0, 123456).timestamp()
        expected_end_time = datetime(2020, 12, 1, 0, 16, 0, 123456).timestamp()

        expected = [
            {"event_type": "pause", "start_time": expected_start_time, "end_time": expected_end_time},
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
    def test_no_pause_event(self, events):
        actual = EventManager.get_pause_events(events)

        expected = []

        assert actual == expected

    events_exception_1 = ([{"event_type": "pause", "start_time": "2020-12-01T00:15:00.123456"}],)

    @pytest.mark.parametrize("events", events_exception_1)
    def test_not_end(self, events):
        with pytest.raises(KeyError):
            EventManager.get_pause_events(events)

    events_exception_2 = ([{"event_type": "pause", "end_time": "2020-12-01T00:16:00.123456"}],)

    @pytest.mark.parametrize("events", events_exception_2)
    def test_not_start(self, events):
        with pytest.raises(KeyError):
            EventManager.get_pause_events(events)


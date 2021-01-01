import pytest
import os
import sys
import pytest_mock
from datetime import datetime

from .. import cut_out_shot


class TestGetEvents:
    def test_normal(self, mocker):
        expected = [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.000"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.000"},
            {"event_type": "stop", "occurred_time": "2020-12-01T00:20:00.000"},
        ]
        mocker.patch("elastic_manager.ElasticManager.get_all_doc", return_value=expected)

        target = cut_out_shot.CutOutShot()
        actual = target._get_events(suffix="20201201000000")

        assert actual == expected


class TestGetCollectStartTime:
    events_normal = (
        [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.000"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.000"},
            {"event_type": "stop", "occurred_time": "2020-12-01T00:20:00.000"},
        ],
        [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.000"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.000"},
        ],
    )

    events_exception = ([{"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.000"}],)

    @pytest.mark.parametrize("events", events_normal)
    def test_normal(self, events):
        target = cut_out_shot.CutOutShot()
        actual = target._get_collect_start_time(events)

        expected = datetime(2020, 12, 1, 0, 10, 0, 0).timestamp()

        assert actual == expected

    @pytest.mark.parametrize("events", events_exception)
    def test_no_start_event(self, events):
        target = cut_out_shot.CutOutShot()
        with pytest.raises(ValueError):
            target._get_collect_start_time(events)


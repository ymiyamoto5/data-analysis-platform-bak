import pytest
from datetime import datetime

import utils.common as common


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
        actual = common.get_collect_start_time(events)

        expected = datetime(2020, 12, 1, 0, 10, 0, 123456).timestamp()

        assert actual == expected

    events_exception = ([{"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"}],)

    @pytest.mark.parametrize("events", events_exception)
    def test_no_start_event(self, events):
        actual = common.get_collect_start_time(events)

        assert actual == None

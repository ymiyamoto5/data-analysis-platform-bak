import pytest
import pandas as pd
from datetime import datetime
from pandas.core.frame import DataFrame
from pandas.util.testing import assert_frame_equal

from elastic_manager.elastic_manager import ElasticManager
from cut_out_shot import cut_out_shot


class TestGetEvents:
    def test_normal(self, mocker):
        expected = [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
            {"event_type": "stop", "occurred_time": "2020-12-01T00:20:00.123456"},
        ]

        mocker.patch.object(ElasticManager, "get_all_doc", return_value=expected)

        target = cut_out_shot.CutOutShot()
        actual = target._get_events(suffix="20201201000000")

        assert actual == expected


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

    @pytest.mark.parametrize("events", events_normal)
    def test_normal(self, events):
        target = cut_out_shot.CutOutShot()
        actual = target._get_collect_start_time(events)

        expected = datetime(2020, 12, 1, 0, 10, 0, 123456).timestamp()

        assert actual == expected

    events_exception = ([{"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"}],)

    @pytest.mark.parametrize("events", events_exception)
    def test_no_start_event(self, events):
        target = cut_out_shot.CutOutShot()
        with pytest.raises(ValueError):
            target._get_collect_start_time(events)


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
        target = cut_out_shot.CutOutShot()
        actual = target._get_pause_events(events)

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
        target = cut_out_shot.CutOutShot()
        actual = target._get_pause_events(events)

        expected = []

        assert actual == expected

    events_exception_1 = ([{"event_type": "pause", "start_time": "2020-12-01T00:15:00.123456"}],)

    @pytest.mark.parametrize("events", events_exception_1)
    def test_not_end(self, events):
        target = cut_out_shot.CutOutShot()
        with pytest.raises(KeyError):
            target._get_pause_events(events)

    events_exception_2 = ([{"event_type": "pause", "end_time": "2020-12-01T00:16:00.123456"}],)

    @pytest.mark.parametrize("events", events_exception_2)
    def test_not_start(self, events):
        target = cut_out_shot.CutOutShot()
        with pytest.raises(KeyError):
            target._get_pause_events(events)


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
    def test_normal_single_tag_event(self, events):
        target = cut_out_shot.CutOutShot()
        actual = target._get_tag_events(events, back_seconds_for_tagging=120)

        expected_start_time = datetime(2020, 12, 1, 0, 15, 0, 123456).timestamp()
        expected_end_time = datetime(2020, 12, 1, 0, 17, 0, 123456).timestamp()

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
    def test_normal_multi_tag_event(self, events):
        target = cut_out_shot.CutOutShot()
        actual = target._get_tag_events(events, back_seconds_for_tagging=120)

        expected_tag1_start_time = datetime(2020, 12, 1, 0, 15, 0, 123456).timestamp()
        expected_tag1_end_time = datetime(2020, 12, 1, 0, 17, 0, 123456).timestamp()
        expected_tag2_start_time = datetime(2020, 12, 1, 0, 16, 0, 123456).timestamp()
        expected_tag2_end_time = datetime(2020, 12, 1, 0, 18, 0, 123456).timestamp()

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
    def test_no_tag_event(self, events):
        target = cut_out_shot.CutOutShot()
        actual = target._get_tag_events(events, back_seconds_for_tagging=120)

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
    def test_no_end_time(self, events):
        target = cut_out_shot.CutOutShot()
        with pytest.raises(KeyError):
            target._get_tag_events(events, back_seconds_for_tagging=120)


class TestGetPickleList:
    def test_normal_1(self, tmp_path):
        tmp_file_1 = tmp_path / "AD-00_20201216-080001.853297.pkl"
        tmp_file_2 = tmp_path / "AD-00_20201216-080000.280213.pkl"
        tmp_file_3 = tmp_path / "AD-00_20201216-075958.708968.pkl"

        tmp_file_1.write_text("")
        tmp_file_2.write_text("")
        tmp_file_3.write_text("")

        target = cut_out_shot.CutOutShot()
        actual = target._get_pickle_list(tmp_path)

        expected = [
            tmp_file_3._str,
            tmp_file_2._str,
            tmp_file_1._str,
        ]

        assert actual == expected

    def test_normal_2(self, tmp_path):
        tmp_file_1 = tmp_path / "AD-00_20201216-075958.708968.pkl"
        tmp_file_2 = tmp_path / "AD-00_20201216-075958.708968.dat"
        tmp_file_3 = tmp_path / "AD-00_20201216-080000.280213.pkl"
        tmp_file_4 = tmp_path / "AD-00_20201216-080001.853297.pkl"

        tmp_file_1.write_text("")
        tmp_file_2.write_text("")
        tmp_file_3.write_text("")
        tmp_file_4.write_text("")

        target = cut_out_shot.CutOutShot()
        actual = target._get_pickle_list(tmp_path)

        expected = [
            tmp_file_1._str,
            tmp_file_3._str,
            tmp_file_4._str,
        ]

        assert actual == expected

    def test_no_file(self, tmp_path):
        target = cut_out_shot.CutOutShot()
        actual = target._get_pickle_list(tmp_path)

        expected = []

        assert actual == expected


class TestExcludeSetupInterval:
    def test_normal_exclude(self, rawdata_df):
        """ 正常系：段取区間除外 """

        target = cut_out_shot.CutOutShot()
        collect_start_time: float = datetime(2020, 12, 1, 10, 30, 23, 0).timestamp()
        actual: DataFrame = target._exclude_setup_interval(rawdata_df, collect_start_time)

        expected: DataFrame = rawdata_df.drop(index=rawdata_df.index[:])

        assert_frame_equal(actual, expected)

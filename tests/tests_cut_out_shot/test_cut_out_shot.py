import pytest
import pandas as pd
from datetime import datetime
from typing import List
from pandas.core.frame import DataFrame
from pandas.testing import assert_frame_equal
import numpy as np

from elastic_manager.elastic_manager import ElasticManager
from cut_out_shot.cut_out_shot import CutOutShot


class TestInit:
    def test_displacement_func_is_none_exception(self):
        with pytest.raises(SystemExit):
            cut_out_shot = CutOutShot(
                load01_func=lambda x: x + 1.0,
                load02_func=lambda x: x + 1.0,
                load03_func=lambda x: x + 1.0,
                load04_func=lambda x: x + 1.0,
            )

    def test_load01_func_is_none_exception(self):
        with pytest.raises(SystemExit):
            cut_out_shot = CutOutShot(
                displacement_func=lambda x: x + 1.0,
                load02_func=lambda x: x + 1.0,
                load03_func=lambda x: x + 1.0,
                load04_func=lambda x: x + 1.0,
            )

    def test_load02_func_is_none_exception(self):
        with pytest.raises(SystemExit):
            cut_out_shot = CutOutShot(
                displacement_func=lambda x: x + 1.0,
                load01_func=lambda x: x + 1.0,
                load03_func=lambda x: x + 1.0,
                load04_func=lambda x: x + 1.0,
            )

    def test_load03_func_is_none_exception(self):
        with pytest.raises(SystemExit):
            cut_out_shot = CutOutShot(
                displacement_func=lambda x: x + 1.0,
                load01_func=lambda x: x + 1.0,
                load02_func=lambda x: x + 1.0,
                load04_func=lambda x: x + 1.0,
            )

    def test_load04_func_is_none_exception(self):
        with pytest.raises(SystemExit):
            cut_out_shot = CutOutShot(
                displacement_func=lambda x: x + 1.0,
                load01_func=lambda x: x + 1.0,
                load02_func=lambda x: x + 1.0,
                load03_func=lambda x: x + 1.0,
            )


class TestGetEvents:
    def test_normal(self, target, mocker):
        expected = [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.123456"},
            {"event_type": "stop", "occurred_time": "2020-12-01T00:20:00.123456"},
        ]

        mocker.patch.object(ElasticManager, "get_all_doc", return_value=expected)

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

    events_normal_ids = [f"events-{x}" for x in events_normal]

    @pytest.mark.parametrize("events", events_normal, ids=events_normal_ids)
    def test_normal(self, target, events):
        actual = target._get_collect_start_time(events)

        expected = datetime(2020, 12, 1, 0, 10, 0, 123456).timestamp()

        assert actual == expected

    events_exception = ([{"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.123456"}],)

    @pytest.mark.parametrize("events", events_exception)
    def test_no_start_event(self, target, events):
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
    def test_normal(self, target, events):
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
    def test_no_pause_event(self, target, events):
        actual = target._get_pause_events(events)

        expected = []

        assert actual == expected

    events_exception_1 = ([{"event_type": "pause", "start_time": "2020-12-01T00:15:00.123456"}],)

    @pytest.mark.parametrize("events", events_exception_1)
    def test_not_end(self, target, events):
        with pytest.raises(KeyError):
            target._get_pause_events(events)

    events_exception_2 = ([{"event_type": "pause", "end_time": "2020-12-01T00:16:00.123456"}],)

    @pytest.mark.parametrize("events", events_exception_2)
    def test_not_start(self, target, events):
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
    def test_normal_single_tag_event(self, target, events):
        target.back_seconds_for_tagging = 120
        actual = target._get_tag_events(events)

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
    def test_normal_multi_tag_event(self, target, events):
        target.back_seconds_for_tagging = 120
        actual = target._get_tag_events(events)

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


class TestGetPickleList:
    def test_normal_1(self, target, tmp_path):
        tmp_file_1 = tmp_path / "AD-00_20201216-080001.853297.pkl"
        tmp_file_2 = tmp_path / "AD-00_20201216-080000.280213.pkl"
        tmp_file_3 = tmp_path / "AD-00_20201216-075958.708968.pkl"

        tmp_file_1.write_text("")
        tmp_file_2.write_text("")
        tmp_file_3.write_text("")

        actual = target._get_pickle_list(tmp_path)

        expected = [
            tmp_file_3._str,
            tmp_file_2._str,
            tmp_file_1._str,
        ]

        assert actual == expected

    def test_normal_2(self, target, tmp_path):
        tmp_file_1 = tmp_path / "AD-00_20201216-075958.708968.pkl"
        tmp_file_2 = tmp_path / "AD-00_20201216-075958.708968.dat"
        tmp_file_3 = tmp_path / "AD-00_20201216-080000.280213.pkl"
        tmp_file_4 = tmp_path / "AD-00_20201216-080001.853297.pkl"

        tmp_file_1.write_text("")
        tmp_file_2.write_text("")
        tmp_file_3.write_text("")
        tmp_file_4.write_text("")

        actual = target._get_pickle_list(tmp_path)

        expected = [
            tmp_file_1._str,
            tmp_file_3._str,
            tmp_file_4._str,
        ]

        assert actual == expected

    def test_no_file(self, target, tmp_path):
        actual = target._get_pickle_list(tmp_path)

        expected = []

        assert actual == expected


class TestExcludeSetupInterval:
    def test_normal_exclude_all(self, target, rawdata_df):
        """ 正常系：段取区間除外（全データ） """

        collect_start_time: float = datetime(2020, 12, 1, 10, 30, 22, 111112).timestamp()
        actual: DataFrame = target._exclude_setup_interval(rawdata_df, collect_start_time)

        expected: DataFrame = rawdata_df.drop(index=rawdata_df.index[:])

        assert_frame_equal(actual, expected)

    def test_normal_exclude_some_data(self, target, rawdata_df):
        """ 正常系：段取区間除外（部分データ） """

        collect_start_time: float = datetime(2020, 12, 1, 10, 30, 20, 0).timestamp()
        actual: DataFrame = target._exclude_setup_interval(rawdata_df, collect_start_time)

        expected: DataFrame = rawdata_df.drop(index=rawdata_df.index[:-3])

        assert_frame_equal(actual, expected)

    def test_normal_not_exclude(self, target, rawdata_df):
        """ 正常系：段取区間除外（除外対象なし） """

        # rawdata_dfの最初のサンプルと同時刻
        collect_start_time: float = datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp()
        actual: DataFrame = target._exclude_setup_interval(rawdata_df, collect_start_time)

        expected: DataFrame = rawdata_df

        assert_frame_equal(actual, expected)


class TestExcludePauseInterval:
    def test_normal_exclude_one_interval(self, target, rawdata_df):
        """ 正常系：中断区間(1回)除外 """

        start_time: float = datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp()
        end_time: float = datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp()

        pause_events = [{"event_type": "pause", "start_time": start_time, "end_time": end_time}]

        actual: DataFrame = target._exclude_pause_interval(rawdata_df, pause_events)

        # 最初と最後のサンプルを以外すべて除去される。
        expected: DataFrame = pd.concat([rawdata_df[:1], rawdata_df[-1:]], axis=0)

        assert_frame_equal(actual, expected)

    def test_normal_exclude_two_interval(self, target, rawdata_df):
        """ 正常系：中断区間(2回)除外 """

        start_time_1: float = datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp()
        end_time_1: float = datetime(2020, 12, 1, 10, 30, 15, 111111).timestamp()
        start_time_2: float = datetime(2020, 12, 1, 10, 30, 16, 111111).timestamp()
        end_time_2: float = datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp()

        pause_events = [
            {"event_type": "pause", "start_time": start_time_1, "end_time": end_time_1},
            {"event_type": "pause", "start_time": start_time_2, "end_time": end_time_2},
        ]

        actual: DataFrame = target._exclude_pause_interval(rawdata_df, pause_events)

        # 最初と最後のサンプルを以外すべて除去される。
        expected: DataFrame = pd.concat([rawdata_df[:1], rawdata_df[-1:]], axis=0)

        assert_frame_equal(actual, expected)


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


class TestDetectShotStart:
    def test_normal_shot_detect(self, target):
        """ 正常系：ショット開始検知 """

        target.is_shot_section = False
        displacemnet = 45.0
        start_displacement = 45.0

        actual: bool = target._detect_shot_start(displacemnet, start_displacement)

        expected = True

        assert actual == expected

    def test_normal_shot_already_started(self, target):
        """ 正常系：ショットがすでに開始されているため検知対象外 """

        target.is_shot_section = True
        displacemnet = 45.0
        start_displacement = 45.0

        actual: bool = target._detect_shot_start(displacemnet, start_displacement)

        expected = False

        assert actual == expected

    def test_normal_displacement_has_not_reached_threshold(self, target):
        """ 正常系：ショット開始となる変位値まで到達していない """

        target.is_shot_section = False
        displacemnet = 45.1
        start_displacement = 45.0

        actual: bool = target._detect_shot_start(displacemnet, start_displacement)

        expected = False

        assert actual == expected


class TestDetectShotEnd:
    def test_normal_detect_shot_end(self, target):
        """ 正常系：ショット終了検知 """

        target.is_shot_section = True
        target.margin = 0.1
        displacemnet = 45.2
        start_displacement = 45.0

        actual: bool = target._detect_shot_end(displacemnet, start_displacement)

        expected = True

        assert actual == expected

    def test_normal_shot_has_not_started_yet(self, target):
        """ 正常系：ショット未開始のため終了検知しない """

        target.is_shot_section = False
        target.margin = 0.1
        displacemnet = 45.2
        start_displacement = 45.0

        actual: bool = target._detect_shot_end(displacemnet, start_displacement)

        expected = False

        assert actual == expected

    def test_normal_not_detect_by_maring(self, target):
        """ 正常系：マージンを加味するとショット終了検知されない """

        target.is_shot_section = True
        target.margin = 0.1
        displacemnet = 45.1
        start_displacement = 45.0

        actual: bool = target._detect_shot_end(displacemnet, start_displacement)

        expected = False

        assert actual == expected


class TestDetectCutOutEnd:
    def test_normal_detect_cut_out_end(self, target):
        """ 正常系：切り出し終了検知 """

        target.is_target_of_cut_out = True
        displacement = 30.0
        end_displacement = 30.0

        actual: bool = target._detect_cut_out_end(displacement, end_displacement)

        expected = True

        assert actual == expected

    def test_normal_cut_out_has_not_started_yet(self, target):
        """ 正常系：切り出しが開始されていないため終了検知せず """

        target.is_target_of_cut_out = False
        displacement = 30.0
        end_displacement = 30.0

        actual: bool = target._detect_cut_out_end(displacement, end_displacement)

        expected = False

        assert actual == expected

    def test_normal_displacement_has_not_reached_threshold(self, target):
        """ 正常系：切り出しが終了しきい値に到達していない """

        target.is_target_of_cut_out = True
        displacement = 30.1
        end_displacement = 30.0

        actual: bool = target._detect_cut_out_end(displacement, end_displacement)

        expected = False

        assert actual == expected


class TestBackupDfTail:
    def test_normal(self, target, rawdata_df):
        target.previous_size = 3
        target._backup_df_tail(rawdata_df)
        actual: DataFrame = target.previous_df_tail

        expected = rawdata_df.tail(target.previous_size)

        assert_frame_equal(actual, expected)

    def test_normal_over_size_backup(self, target, rawdata_df):
        """ 正常系：バックアップするサイズがDataFrameのサイズを超えている場合、全件取得 """

        target.previous_size = 100
        target._backup_df_tail(rawdata_df)
        actual: DataFrame = target.previous_df_tail

        expected = rawdata_df

        assert_frame_equal(actual, expected)

    def test_normal_empty_dataframe(self, target, rawdata_df):
        """ 正常系：DataFrameが空の場合、空のDataFrameが返る """

        rawdata_df: DataFrame = rawdata_df.drop(index=rawdata_df.index[:])

        target.previous_size = 3
        target._backup_df_tail(rawdata_df)
        actual: DataFrame = target.previous_df_tail

        expected: DataFrame = rawdata_df.drop(index=rawdata_df.index[:])

        assert_frame_equal(actual, expected)


class TestGetPrecedingDf:
    def test_normal_data_included_in_current_df(self, target, rawdata_df):
        """ 正常系：遡るデータが現在のDataFrameに含まれる（つまりファイルを跨がない）場合、
            現在のDataFrameからデータを取得すればよい
        """

        target.previous_size = 3
        row_number = 4

        actual: DataFrame = target._get_preceding_df(row_number, rawdata_df)

        expected: DataFrame = rawdata_df[(row_number - target.previous_size) : row_number]

        assert_frame_equal(actual, expected)

    def test_normal_data_included_in_previous_df(self, target, rawdata_df):
        """ 正常系：遡るデータが過去のDataFrameに含まれる（つまりファイルを跨ぐ）場合、
            過去のDataFrameと現在のDataFrameからデータを取得する必要がある
        """

        # 5件遡るが、3つ目のサンプルでショットを検知したため、過去分に遡る必要がある
        target.previous_size = 5
        row_number = 3

        # rawdata_dfを過去と現在に2分割
        target.previous_df_tail = rawdata_df[: target.previous_size]
        current_df = rawdata_df[target.previous_size :]

        actual: DataFrame = target._get_preceding_df(row_number, current_df)
        # assertのためindexはresetしておく
        actual = actual.reset_index(drop=True)

        expected = [
            # 切り出し区間1-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
                "displacement": 47.1,
                "load01": 1.500,
                "load02": 1.200,
                "load03": 1.300,
                "load04": 1.400,
            },
            # 切り出し区間1-3
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
                "displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
            },
            # 切り出し区間後1
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 15, 111111).timestamp(),
                "displacement": 30.599,
                "load01": -0.130,
                "load02": 0.020,
                "load03": 0.483,
                "load04": 0.419,
            },
            # 切り出し区間後2
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 16, 111111).timestamp(),
                "displacement": 24.867,
                "load01": -0.052,
                "load02": 0.035,
                "load03": 0.402,
                "load04": 0.278,
            },
            # 切り出し区間後3(変位にmargin=0.1を加算した場合、ショットの終了と見做されない変位値)
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 17, 111111).timestamp(),
                "displacement": 47.100,
                "load01": 0.155,
                "load02": 0.171,
                "load03": 0.180,
                "load04": 0.146,
            },
        ]

        expected_df = pd.DataFrame(expected)
        assert_frame_equal(actual, expected_df)

    def test_normal_all_data_included_in_previous_df(self, target, rawdata_df):
        """ 正常系：現在のDataFrameの最初でショットを検知した場合、
            過去のDataFrameからデータを取得する必要がある
        """

        # 5件遡るが、最初のサンプルでショットを検知したため、過去分に遡る必要がある
        target.previous_size = 5
        row_number = 0

        # rawdata_dfを過去と現在に2分割
        target.previous_df_tail = rawdata_df[: target.previous_size]
        current_df = rawdata_df[target.previous_size :]

        actual: DataFrame = target._get_preceding_df(row_number, current_df)
        # assertのためindexはresetしておく
        actual = actual.reset_index(drop=True)

        expected = target.previous_df_tail

        assert_frame_equal(actual, expected)

    def test_normal_detect_shot_in_first_df(self, target, rawdata_df):
        """ 正常系：最初のDataFrame（最初のファイル）の序盤でショットを検知した場合、
            過去のDataFrameがないので、現在のDataFrameから遡れるだけ遡ってデータを取得する
        """

        target.previous_df_tail = pd.DataFrame()

        target.previous_size = 5
        row_number = 3

        actual: DataFrame = target._get_preceding_df(row_number, rawdata_df)
        # assertのためindexはresetしておく
        actual = actual.reset_index(drop=True)

        expected = rawdata_df[:row_number]

        assert_frame_equal(actual, expected)


class TestCalculateSpm:
    def test_normal(self, target):

        # 前回のショット検知時と今回のショット検知時が1秒差
        target.previous_shot_start_time = datetime(2020, 12, 1, 10, 29, 11, 111111).timestamp()
        timestamp: float = datetime(2020, 12, 1, 10, 29, 12, 111111).timestamp()

        actual: float = target._calculate_spm(timestamp)

        # 1ショットに1秒、つまり60spm
        expected = 60.0

        assert actual == expected

    def test_zero_divide_exception(self, target):
        """ 異常系：前回のショット検知時と今回のショット検知時の時差がないとき、0割り例外。
            通常は発生しえない。
        """

        target.previous_shot_start_time = datetime(2020, 12, 1, 10, 29, 11, 111111).timestamp()
        timestamp: float = datetime(2020, 12, 1, 10, 29, 11, 111111).timestamp()

        with pytest.raises(ZeroDivisionError):
            target._calculate_spm(timestamp)


class TestIncludePreviousData:
    def test_normal(self, target, rawdata_df):
        """ 正常系：2つのサンプルを追加 """

        target._include_previous_data(rawdata_df[:2])

        assert target.cut_out_targets[0]["timestamp"] == rawdata_df.iloc[0].timestamp
        assert target.cut_out_targets[0]["sequential_number"] == 0
        assert target.cut_out_targets[0]["sequential_number_by_shot"] == 0
        assert target.cut_out_targets[0]["displacement"] == rawdata_df.iloc[0].displacement
        assert target.cut_out_targets[0]["load01"] == rawdata_df.iloc[0].load01
        assert target.cut_out_targets[0]["load02"] == rawdata_df.iloc[0].load02
        assert target.cut_out_targets[0]["load03"] == rawdata_df.iloc[0].load03
        assert target.cut_out_targets[0]["load04"] == rawdata_df.iloc[0].load04
        assert target.cut_out_targets[0]["shot_number"] == 0
        assert target.cut_out_targets[0]["tags"] == []

        assert target.cut_out_targets[1]["timestamp"] == rawdata_df.iloc[1].timestamp
        assert target.cut_out_targets[1]["sequential_number"] == 1
        assert target.cut_out_targets[1]["sequential_number_by_shot"] == 1
        assert target.cut_out_targets[1]["displacement"] == rawdata_df.iloc[1].displacement
        assert target.cut_out_targets[1]["load01"] == rawdata_df.iloc[1].load01
        assert target.cut_out_targets[1]["load02"] == rawdata_df.iloc[1].load02
        assert target.cut_out_targets[1]["load03"] == rawdata_df.iloc[1].load03
        assert target.cut_out_targets[1]["load04"] == rawdata_df.iloc[1].load04
        assert target.cut_out_targets[1]["shot_number"] == 0
        assert target.cut_out_targets[1]["tags"] == []


class TestAddCutOutTarget:
    def test_normal(self, target, rawdata_df):
        """ 正常系：1レコード追加 """

        cut_out_target = rawdata_df.iloc[2]

        target._add_cut_out_target(cut_out_target)

        actual: List[dict] = target.cut_out_targets

        expected = {
            "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
            "sequential_number": 0,
            "sequential_number_by_shot": 0,
            "displacement": 47.0,
            "load01": 1.574,
            "load02": 1.308,
            "load03": 1.363,
            "load04": 1.432,
            "shot_number": 0,
            "tags": [],
        }

        assert actual[0] == expected


class TestSetToNoneForLowSpm:
    def test_normal(self, target, shots_meta_df):
        """ 最低spm (15spm) を下回る spm は None に設定する """

        target.shots_meta_df = shots_meta_df
        target._set_to_none_for_low_spm()

        actual_df: DataFrame = target.shots_meta_df

        expected = [
            {"shot_number": 1, "spm": None, "num_of_samples_in_cut_out": 400000},
            {"shot_number": 2, "spm": 80.0, "num_of_samples_in_cut_out": 3000},
            {"shot_number": 3, "spm": 40.0, "num_of_samples_in_cut_out": 6000},
            {"shot_number": 4, "spm": 60.0, "num_of_samples_in_cut_out": 4000},
        ]

        expected_df = pd.DataFrame(expected).replace({np.nan: None})

        assert_frame_equal(actual_df, expected_df)


class TestExcludeOverSample:
    def test_normal_exclude_one_shot(self, target, rawdata_df, shots_meta_df):
        """ 最大サンプル数（60/15*100k=400,000）を超えるショットを除外する。
            shots_meta_df fixtureのshot_number:1は400,001サンプルとしているため除外される。
        """

        target.shots_meta_df = shots_meta_df

        # 6サンプル切り出し
        target.previous_size = 0
        target._cut_out_shot(rawdata_df, 47.0, 34.0)
        cut_out_targets_df = pd.DataFrame(target.cut_out_targets)

        actual: DataFrame = target._exclude_over_sample(cut_out_targets_df)

        expected: DataFrame = cut_out_targets_df[cut_out_targets_df.shot_number == 2]

        assert_frame_equal(actual, expected)

    def test_normal_not_exists_over_sample(self, target, rawdata_df, shots_meta_df):
        """ 最大サンプル数を超えるショットがなかった場合、何も除外されずに元のDataFrameが返る """

        # 全ショットが最大サンプル以下になるようデータ書き換え
        shots_meta_df.at[0, "num_of_samples_in_cut_out"] = 5000
        target.shots_meta_df = shots_meta_df

        # 6サンプル切り出し
        target.previous_size = 0
        target._cut_out_shot(rawdata_df, 47.0, 34.0)
        cut_out_targets_df = pd.DataFrame(target.cut_out_targets)

        actual: DataFrame = target._exclude_over_sample(cut_out_targets_df)

        expected: DataFrame = cut_out_targets_df

        assert_frame_equal(actual, expected)


class TestApplyExprDisplacment:
    def test_normal(self, rawdata_df):
        """ 正常系：lambda式適用"""

        cut_out_shot = CutOutShot(
            displacement_func=lambda x: x + 1.0,
            load01_func=lambda x: x * 1.0,
            load02_func=lambda x: x * 1.0,
            load03_func=lambda x: x * 1.0,
            load04_func=lambda x: x * 1.0,
        )

        # 全データを見る必要はないので一部スライス
        target_df: DataFrame = rawdata_df[:3]

        actual_df: DataFrame = cut_out_shot._apply_expr_displacement(target_df)

        expected = [
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp(),
                "displacement": 50.284,
                "load01": 0.223,
                "load02": 0.211,
                "load03": 0.200,
                "load04": 0.218,
            },
            # 切り出し区間前2
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp(),
                "displacement": 48.534,
                "load01": 0.155,
                "load02": 0.171,
                "load03": 0.180,
                "load04": 0.146,
            },
            # 切り出し区間1-1
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
                "displacement": 48.0,
                "load01": 1.574,
                "load02": 1.308,
                "load03": 1.363,
                "load04": 1.432,
            },
        ]

        expected_df = pd.DataFrame(expected)

        assert_frame_equal(actual_df, expected_df)


class TestApplyExprLoad:
    def test_normal(self, rawdata_df):
        """ 正常系：lambda式適用"""

        cut_out_shot = CutOutShot(
            displacement_func=lambda x: x + 1.0,
            load01_func=lambda x: x + 2.0,
            load02_func=lambda x: x + 3.0,
            load03_func=lambda x: x + 4.0,
            load04_func=lambda x: x + 5.0,
        )

        # 全データを見る必要はないので一部スライス
        target_df: DataFrame = rawdata_df[:3]

        actual_df: DataFrame = cut_out_shot._apply_expr_load(target_df)

        expected = [
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp(),
                "displacement": 49.284,
                "load01": 2.223,
                "load02": 3.211,
                "load03": 4.200,
                "load04": 5.218,
            },
            # 切り出し区間前2
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp(),
                "displacement": 47.534,
                "load01": 2.155,
                "load02": 3.171,
                "load03": 4.180,
                "load04": 5.146,
            },
            # 切り出し区間1-1
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
                "displacement": 47.0,
                "load01": 3.574,
                "load02": 4.308,
                "load03": 5.363,
                "load04": 6.432,
            },
        ]

        expected_df = pd.DataFrame(expected)

        assert_frame_equal(actual_df, expected_df)


class TestCutOutShot:
    def test_normal_1(self, target, rawdata_df):
        """ 正常系：遡り件数1件, start_displacememt: 47.0, end_displacememt: 34.0。
            全13サンプル中8サンプルが切り出される。
        """

        target.previous_size = 1
        target._cut_out_shot(rawdata_df, 47.0, 34.0)

        actual: List[dict] = target.cut_out_targets
        actual_df = pd.DataFrame(actual)

        expected = [
            # 切り出し区間前2（遡りにより切り出し区間に含まれる）
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp(),
                "sequential_number": 0,
                "sequential_number_by_shot": 0,
                "displacement": 47.534,
                "load01": 0.155,
                "load02": 0.171,
                "load03": 0.180,
                "load04": 0.146,
                "shot_number": 1,
                "tags": [],
            },
            # 切り出し区間1-1
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
                "sequential_number": 1,
                "sequential_number_by_shot": 1,
                "displacement": 47.0,
                "load01": 1.574,
                "load02": 1.308,
                "load03": 1.363,
                "load04": 1.432,
                "shot_number": 1,
                "tags": [],
            },
            # 切り出し区間1-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
                "sequential_number": 2,
                "sequential_number_by_shot": 2,
                "displacement": 47.1,
                "load01": 1.500,
                "load02": 1.200,
                "load03": 1.300,
                "load04": 1.400,
                "shot_number": 1,
                "tags": [],
            },
            # 切り出し区間1-3
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
                "sequential_number": 3,
                "sequential_number_by_shot": 3,
                "displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
                "shot_number": 1,
                "tags": [],
            },
            # 切り出し区間後4(ショット区間終了）（遡りにより切り出し区間に含まれる）
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 18, 111111).timestamp(),
                "sequential_number": 4,
                "sequential_number_by_shot": 0,
                "displacement": 47.150,
                "load01": 0.156,
                "load02": 0.172,
                "load03": 0.181,
                "load04": 0.147,
                "shot_number": 2,
                "tags": [],
            },
            # 切り出し区間2-1
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 19, 111111).timestamp(),
                "sequential_number": 5,
                "sequential_number_by_shot": 1,
                "displacement": 47.0,
                "load01": 1.574,
                "load02": 1.308,
                "load03": 1.363,
                "load04": 1.432,
                "shot_number": 2,
                "tags": [],
            },
            # 切り出し区間2-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 20, 111111).timestamp(),
                "sequential_number": 6,
                "sequential_number_by_shot": 2,
                "displacement": 47.1,
                "load01": 1.500,
                "load02": 1.200,
                "load03": 1.300,
                "load04": 1.400,
                "shot_number": 2,
                "tags": [],
            },
            # 切り出し区間2-3
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
                "sequential_number": 7,
                "sequential_number_by_shot": 3,
                "displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
                "shot_number": 2,
                "tags": [],
            },
        ]

        expected_df = pd.DataFrame(expected)

        assert_frame_equal(actual_df, expected_df)

        # shots_meta_dfの確認
        actual_shots_meta_df: DataFrame = target.shots_meta_df

        # 最後のショットの情報は得られないので記録されない。
        expected_shots_meta = [
            {"shot_number": 1.0, "spm": 8.571429, "num_of_samples_in_cut_out": 4.0},
        ]
        expected_shots_meta_df = pd.DataFrame(expected_shots_meta)

        assert_frame_equal(actual_shots_meta_df, expected_shots_meta_df)

    def test_normal_2(self, target, rawdata_df):
        """ 正常系：遡りなし, start_displacememt: 46.9, end_displacememt: 34.0。
            全13サンプル中2サンプルが切り出される。
        """

        target.previous_size = 0
        target._cut_out_shot(rawdata_df, 46.9, 34.0)

        actual: List[dict] = target.cut_out_targets
        actual_df = pd.DataFrame(actual)

        expected = [
            # 切り出し区間1-3
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
                "sequential_number": 0,
                "sequential_number_by_shot": 0,
                "displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
                "shot_number": 1,
                "tags": [],
            },
            # 切り出し区間2-3
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
                "sequential_number": 1,
                "sequential_number_by_shot": 0,
                "displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
                "shot_number": 2,
                "tags": [],
            },
        ]

        expected_df = pd.DataFrame(expected)

        assert_frame_equal(actual_df, expected_df)

        # shots_meta_dfの確認
        actual_shots_meta_df: DataFrame = target.shots_meta_df

        # 最後のショットの情報は得られないので記録されない。
        expected_shots_meta = [
            {"shot_number": 1.0, "spm": 8.571429, "num_of_samples_in_cut_out": 1.0},
        ]
        expected_shots_meta_df = pd.DataFrame(expected_shots_meta)

        assert_frame_equal(actual_shots_meta_df, expected_shots_meta_df)

import pytest
import pathlib
from datetime import datetime, timedelta, timezone

from data_recorder import data_recorder
from elastic_manager.elastic_manager import ElasticManager

from utils.common import TIMESTAMP_MAX


class TestCreateFileTimestamp:
    def test_normal(self):
        """ ファイル名からdatetime型のタイムスタンプを生成出来ること """

        filepath = "tmp00/AD-00_20201216-080058.620753.dat"

        actual = data_recorder._create_file_timestamp(filepath)
        expected = datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()

        assert actual == expected


class TestGetTargetInterval:
    def test_setup_end_are_set(self):
        """ start_timeとend_timeの設定が正しく行われること """

        setup_time: datetime = datetime.now()
        setup_time_str: str = datetime.isoformat(setup_time)
        end_time: datetime = setup_time + timedelta(seconds=30)
        end_time_str: str = datetime.isoformat(end_time)

        events = [
            {"event_type": "setup", "occurred_time": setup_time_str},
            {"event_type": "stop", "occurred_time": end_time_str},
        ]

        actual = data_recorder._get_target_interval(events)

        expected = (setup_time.timestamp(), end_time.timestamp())

        assert actual == expected

    def test_end_is_not_set(self):
        """ setup_timeのみが設定されている場合、end_timeはmaxとして設定される """

        setup_time: datetime = datetime.now()
        setup_time_str: str = datetime.isoformat(setup_time)

        events = [
            {"event_type": "setup", "occurred_time": setup_time_str},
        ]

        actual = data_recorder._get_target_interval(events)

        expected = (setup_time.timestamp(), TIMESTAMP_MAX)

        assert actual == expected

    def test_is_not_setuped(self):
        """ setup_time, end_timeが設定されていないときは、対象区間は (None, None) となる。"""

        events = []

        with pytest.raises(SystemExit):
            data_recorder._get_target_interval(events)


class TestCreateFilesInfo:
    def test_normal_file_exists(self, dat_files):
        """ 正常系：ファイルが存在する """

        actual = data_recorder._create_files_info(dat_files.tmp_path._str)

        expected = [
            data_recorder.FileInfo(dat_files.tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 59, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_3._str, datetime(2020, 12, 16, 8, 1, 0, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_4._str, datetime(2020, 12, 16, 8, 1, 1, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_5._str, datetime(2020, 12, 16, 8, 1, 2, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_file_exists_not_sorted(self, tmp_path):
        """ 正常系：ファイルが存在する。ファイルが名前の昇順にソートされること """

        tmp_dat_1: pathlib.Path = tmp_path / "AD-00_20201216-080058.620753.dat"
        tmp_dat_2: pathlib.Path = tmp_path / "AD-00_20201216-080040.620753.dat"
        tmp_dat_3: pathlib.Path = tmp_path / "AD-00_20201210-080100.620753.dat"

        tmp_dat_1.write_text("")
        tmp_dat_2.write_text("")
        tmp_dat_3.write_text("")

        actual = data_recorder._create_files_info(tmp_path._str)

        expected = [
            data_recorder.FileInfo(tmp_dat_3._str, datetime(2020, 12, 10, 8, 1, 0, 620753).timestamp()),
            data_recorder.FileInfo(tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 40, 620753).timestamp()),
            data_recorder.FileInfo(tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_file_not_exists(self):
        """ 正常系：ファイルが存在しない。 """

        actual = data_recorder._create_files_info("dummy_path")

        expected = None

        assert actual == expected


class TestGetTargetFiles:
    def test_normal_target_file_exists(self, dat_files):
        """ 正常系：5ファイル中3ファイルが対象範囲。以下2ファイルが対象外。
            1ファイル目：20201216-080058.620753
            5ファイル目：20201216-080102.620753
        """

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        setup_time = datetime(2020, 12, 16, 8, 0, 59, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 2, 0).timestamp()
        actual = data_recorder._get_target_files(file_infos, setup_time, end_time)

        expected = [
            data_recorder.FileInfo(dat_files.tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 59, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_3._str, datetime(2020, 12, 16, 8, 1, 0, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_4._str, datetime(2020, 12, 16, 8, 1, 1, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_no_target_file(self, dat_files):
        """ 正常系：対象ファイルなし """

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        setup_time = datetime(2020, 12, 16, 8, 1, 3, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 5, 0).timestamp()
        actual = data_recorder._get_target_files(file_infos, setup_time, end_time)

        expected = []

        assert actual == expected


class TestGetNotTargetFiles:
    def test_normal_not_target_file_exists(self, dat_files):
        """ 正常系：5ファイル中3ファイルが対象範囲外。以下2ファイルが対象外。
            1ファイル目：20201216-080058.620753
            5ファイル目：20201216-080102.620753
        """

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        setup_time = datetime(2020, 12, 16, 8, 0, 59, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 2, 0).timestamp()
        actual = data_recorder._get_not_target_files(file_infos, setup_time, end_time)

        expected = [
            data_recorder.FileInfo(dat_files.tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
            data_recorder.FileInfo(dat_files.tmp_dat_5._str, datetime(2020, 12, 16, 8, 1, 2, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_all_files_are_target(self, dat_files):
        """ 正常系：すべて対象ファイル（対象外ファイルなし） """

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)

        setup_time = datetime(2020, 12, 16, 8, 0, 58, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 10, 0).timestamp()
        actual = data_recorder._get_not_target_files(file_infos, setup_time, end_time)

        expected = []

        assert actual == expected


class TestIsNowRecording:
    def test_normal_event_is_recorded(self, mocker):
        """ 正常系：event_typeがrecorded """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "get_latest_events_index_doc", return_value={"event_type": "recorded"})

        actual: bool = data_recorder._is_now_recording()
        expected: bool = False

        assert actual == expected

    def test_normal_event_is_not_recorded(self, mocker):
        """ 正常系：event_typeがrecorded """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "get_latest_events_index_doc", return_value={"event_type": "stop"})

        actual: bool = data_recorder._is_now_recording()
        expected: bool = True

        assert actual == expected

    def test_events_index_not_exists_exception(self, mocker):
        """ 異常系：events_indexが存在しない """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value=None)

        actual: bool = data_recorder._is_now_recording()
        expected: bool = True

        assert actual == expected

    def test_events_index_doc_not_exists_exception(self, mocker):
        """ 異常系：events_indexのドキュメントがない """

        mocker.patch.object(ElasticManager, "get_latest_events_index", return_value="tmp_events_index")
        mocker.patch.object(ElasticManager, "get_latest_events_index_doc", return_value=None)

        actual: bool = data_recorder._is_now_recording()
        expected: bool = True

        assert actual == expected


class TestReadBinaryFiles:
    def test_normal(self, dat_files):
        """ 正常系：バイナリファイルが正常に読めること """

        file_infos = data_recorder._create_files_info(dat_files.tmp_path._str)
        file = file_infos[0]

        actual = data_recorder._read_binary_files(file=file, sequential_number=0)

        expected = (
            [
                {
                    "sequential_number": 0,
                    "timestamp": file.timestamp,
                    "displacement": 10.0,
                    "load01": 1.1,
                    "load02": 2.2,
                    "load03": 3.3,
                    "load04": 4.4,
                },
                {
                    "sequential_number": 1,
                    "timestamp": file.timestamp + 0.000010,
                    "displacement": 9.0,
                    "load01": 1.2,
                    "load02": 2.3,
                    "load03": 3.4,
                    "load04": 4.5,
                },
            ],
            2,
        )

        assert actual == expected


class TestManualRecord:
    def test_not_exits_file(self, mocker):
        """ 対象ファイルがない場合、何もしない """

        mocker.patch.object(data_recorder, "_create_files_info", return_value=None)

        with pytest.raises(SystemExit):
            data_recorder.manual_record("tmp_target_dir")

    def test_is_now_recording(self, dat_files, mocker):
        """ 現在データ収集中の場合、何もしない """

        data_recorder._create_files_info(dat_files.tmp_path._str)
        mocker.patch.object(data_recorder, "_is_now_recording", return_value=True)

        with pytest.raises(SystemExit):
            data_recorder.manual_record(dat_files.tmp_path._str)

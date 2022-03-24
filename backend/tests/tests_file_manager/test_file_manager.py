import pathlib
from datetime import datetime

from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
from backend.file_manager.file_manager import FileInfo, FileManager


class TestCreateFileTimestamp:
    def test_normal(self):
        """ファイル名からdatetime型のタイムスタンプを生成出来ること"""

        filepath = "tmp00/AD-00_20201216-080058.620753_1.dat"

        actual = FileManager._create_file_timestamp(filepath)
        expected = datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()

        assert actual == expected


class TestCreateFilesInfo:
    def test_normal_file_exists(self, dat_files_single_handler):
        """正常系：ファイルが存在する"""

        machine_id = "test-machine-01"
        gateway_id = "test-gateway-01"
        handler_id = "test-handler-01"

        actual = FileManager.create_files_info(dat_files_single_handler.tmp_path._str, machine_id, gateway_id, handler_id, "dat")

        expected = [
            FileInfo(dat_files_single_handler.tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
            FileInfo(dat_files_single_handler.tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 59, 620753).timestamp()),
            FileInfo(dat_files_single_handler.tmp_dat_3._str, datetime(2020, 12, 16, 8, 1, 0, 620753).timestamp()),
            FileInfo(dat_files_single_handler.tmp_dat_4._str, datetime(2020, 12, 16, 8, 1, 1, 620753).timestamp()),
            FileInfo(dat_files_single_handler.tmp_dat_5._str, datetime(2020, 12, 16, 8, 1, 2, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_file_exists_two_handler(self, dat_files_two_handler):
        """正常系：ファイルが存在する(2つのハンドラー)"""

        machine_id = "test-machine-01"
        gateway_id = "test-gateway-01"
        handlers = ["test-handler-01-1", "test-handler-01-2"]

        actual_1 = FileManager.create_files_info(dat_files_two_handler.tmp_path._str, machine_id, gateway_id, handlers[0], "dat")

        expected_1 = [
            FileInfo(dat_files_two_handler.tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
            FileInfo(dat_files_two_handler.tmp_dat_3._str, datetime(2020, 12, 16, 8, 1, 0, 620753).timestamp()),
        ]

        actual_2 = FileManager.create_files_info(dat_files_two_handler.tmp_path._str, machine_id, gateway_id, handlers[1], "dat")

        expected_2 = [
            FileInfo(dat_files_two_handler.tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 59, 620753).timestamp()),
            FileInfo(dat_files_two_handler.tmp_dat_4._str, datetime(2020, 12, 16, 8, 1, 1, 620753).timestamp()),
        ]

        assert actual_1 == expected_1
        assert actual_2 == expected_2

    def test_normal_file_exists_not_sorted(self, tmp_path):
        """正常系：ファイルが存在する。ファイルが名前の昇順にソートされること"""

        machine_id = "test-machine-01"
        gateway_id = "test-gateway-01"
        handler_id = "test-handler-01"

        tmp_dat_1: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-080058.620753_3.dat"
        tmp_dat_2: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-080040.620753_2.dat"
        tmp_dat_3: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201210-080100.620753_1.dat"

        tmp_dat_1.write_text("")
        tmp_dat_2.write_text("")
        tmp_dat_3.write_text("")

        actual = FileManager.create_files_info(tmp_path._str, machine_id, gateway_id, handler_id, "dat")

        expected = [
            FileInfo(tmp_dat_3._str, datetime(2020, 12, 10, 8, 1, 0, 620753).timestamp()),
            FileInfo(tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 40, 620753).timestamp()),
            FileInfo(tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_file_not_exists(self):
        """正常系：ファイルが存在しない。"""

        machine_id = "test-machine-01"
        gateway_id = "test-gateway-01"
        handler_id = "test-handler-01"

        actual = FileManager.create_files_info("dummy_path", machine_id, gateway_id, handler_id, "dat")

        expected = []

        assert actual == expected


class TestGetTargetFiles:
    def test_normal_target_file_exists(self, dat_files_single_handler):
        """正常系：5ファイル中3ファイルが対象範囲。以下2ファイルが対象外。
        1ファイル目：20201216-080058.620753
        5ファイル目：20201216-080102.620753
        """

        machine_id = "test-machine-01"
        gateway_id = "test-gateway-01"
        handler_id = "test-handler-01"

        file_infos = FileManager.create_files_info(dat_files_single_handler.tmp_path._str, machine_id, gateway_id, handler_id, "dat")

        setup_time = datetime(2020, 12, 16, 8, 0, 59, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 2, 0).timestamp()
        actual = FileManager.get_target_files(file_infos, setup_time, end_time)

        expected = [
            FileInfo(dat_files_single_handler.tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 59, 620753).timestamp()),
            FileInfo(dat_files_single_handler.tmp_dat_3._str, datetime(2020, 12, 16, 8, 1, 0, 620753).timestamp()),
            FileInfo(dat_files_single_handler.tmp_dat_4._str, datetime(2020, 12, 16, 8, 1, 1, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_no_target_file(self, dat_files_single_handler):
        """正常系：対象ファイルなし"""

        machine_id = "test-machine-01"
        gateway_id = "test-gateway-01"
        handler_id = "test-handler-01"

        file_infos = FileManager.create_files_info(dat_files_single_handler.tmp_path._str, machine_id, gateway_id, handler_id, "dat")

        setup_time = datetime(2020, 12, 16, 8, 1, 3, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 5, 0).timestamp()
        actual = FileManager.get_target_files(file_infos, setup_time, end_time)

        expected = []

        assert actual == expected


class TestGetNotTargetFiles:
    def test_normal_not_target_file_exists(self, dat_files_single_handler):
        """正常系：5ファイル中3ファイルが対象範囲外。以下2ファイルが対象外。
        1ファイル目：20201216-080058.620753
        5ファイル目：20201216-080102.620753
        """

        machine_id = "test-machine-01"
        gateway_id = "test-gateway-01"
        handler_id = "test-handler-01"

        file_infos = FileManager.create_files_info(dat_files_single_handler.tmp_path._str, machine_id, gateway_id, handler_id, "dat")

        setup_time = datetime(2020, 12, 16, 8, 0, 59, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 2, 0).timestamp()
        actual = FileManager.get_not_target_files(file_infos, setup_time, end_time)

        expected = [
            FileInfo(dat_files_single_handler.tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
            FileInfo(dat_files_single_handler.tmp_dat_5._str, datetime(2020, 12, 16, 8, 1, 2, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_all_files_are_target(self, dat_files_single_handler):
        """正常系：すべて対象ファイル（対象外ファイルなし）"""

        machine_id = "test-machine-01"
        gateway_id = "test-gateway-01"
        handler_id = "test-handler-01"

        file_infos = FileManager.create_files_info(dat_files_single_handler.tmp_path._str, machine_id, gateway_id, handler_id, "dat")

        setup_time = datetime(2020, 12, 16, 8, 0, 58, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 10, 0).timestamp()
        actual = FileManager.get_not_target_files(file_infos, setup_time, end_time)

        expected = []

        assert actual == expected


class TestGetFiles:
    def test_normal_1(self, tmp_path):

        machine_id = "test-machine-01"
        gateway_id = "test-gateway-01"
        handler_id = "test-handler-01"

        tmp_file_1 = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-080001.853297_1.pkl"
        tmp_file_2 = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-080000.280213_2.pkl"
        tmp_file_3 = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-075958.708968_3.pkl"

        tmp_file_1.write_text("")
        tmp_file_2.write_text("")
        tmp_file_3.write_text("")

        actual = FileManager.get_files(tmp_path, pattern=f"{machine_id}_{gateway_id}_{handler_id}_*.pkl")

        expected = [
            tmp_file_3._str,
            tmp_file_2._str,
            tmp_file_1._str,
        ]

        assert actual == expected

    def test_normal_2(self, tmp_path):

        machine_id = "test-machine-01"
        gateway_id = "test-gateway-01"
        handler_id = "test-handler-01"

        tmp_file_1 = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-075958.708968_1.pkl"
        tmp_file_2 = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-075958.708968_1.dat"
        tmp_file_3 = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-080000.280213_2.pkl"
        tmp_file_4 = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-080001.853297_3.pkl"

        tmp_file_1.write_text("")
        tmp_file_2.write_text("")
        tmp_file_3.write_text("")
        tmp_file_4.write_text("")

        actual = FileManager.get_files(tmp_path, pattern=f"{machine_id}_{gateway_id}_{handler_id}_*.pkl")

        expected = [
            tmp_file_1._str,
            tmp_file_3._str,
            tmp_file_4._str,
        ]

        assert actual == expected


# class TestGetPickleFileList:
#     def test_normal_two_handler(self, tmp_path):
#         machine_id = "test-machine-01"
#         gateway_id = "test-gateway-01"
#         handler_01_id = "test-handler-01"
#         handler_02_id = "test-handler-02"
#         handlers = [
#             DataCollectHistoryHandler(handler_id=handler_01_id),
#             DataCollectHistoryHandler(handler_id=handler_02_id),
#         ]

#         tmp_file_1 = tmp_path / f"{machine_id}_{gateway_id}_{handler_01_id}_20201216-075958.708968_1.pkl"
#         tmp_file_2 = tmp_path / f"{machine_id}_{gateway_id}_{handler_01_id}_20201216-080000.280213_2.pkl"
#         tmp_file_3 = tmp_path / f"{machine_id}_{gateway_id}_{handler_01_id}_20201216-080001.853297_3.pkl"
#         tmp_file_4 = tmp_path / f"{machine_id}_{gateway_id}_{handler_02_id}_20201216-075958.708969_1.pkl"
#         tmp_file_5 = tmp_path / f"{machine_id}_{gateway_id}_{handler_02_id}_20201216-080000.280214_2.pkl"
#         tmp_file_6 = tmp_path / f"{machine_id}_{gateway_id}_{handler_02_id}_20201216-080001.853298_3.pkl"

#         tmp_file_1.write_text("")
#         tmp_file_2.write_text("")
#         tmp_file_3.write_text("")
#         tmp_file_4.write_text("")
#         tmp_file_5.write_text("")
#         tmp_file_6.write_text("")

#         actual = FileManager.get_pickle_file_list(machine_id, tmp_path, handlers=handlers)

#         expected = [
#             [tmp_file_1._str, tmp_file_4._str],
#             [tmp_file_2._str, tmp_file_5._str],
#             [tmp_file_3._str, tmp_file_6._str],
#         ]

#         assert actual == expected

#     def test_normal_three_handler(self, tmp_path):
#         machine_id = "test-machine-01"
#         gateway_id = "test-gateway-01"
#         handler_01_id = "test-handler-01"
#         handler_02_id = "test-handler-02"
#         handler_03_id = "test-handler-03"
#         handlers = [
#             DataCollectHistoryHandler(handler_id=handler_01_id),
#             DataCollectHistoryHandler(handler_id=handler_02_id),
#             DataCollectHistoryHandler(handler_id=handler_03_id),
#         ]

#         tmp_file_1 = tmp_path / f"{machine_id}_{gateway_id}_{handler_01_id}_20201216-075958.708968_1.pkl"
#         tmp_file_2 = tmp_path / f"{machine_id}_{gateway_id}_{handler_01_id}_20201216-080000.280213_2.pkl"
#         tmp_file_3 = tmp_path / f"{machine_id}_{gateway_id}_{handler_01_id}_20201216-080001.853297_3.pkl"
#         tmp_file_4 = tmp_path / f"{machine_id}_{gateway_id}_{handler_02_id}_20201216-075958.708969_1.pkl"
#         tmp_file_5 = tmp_path / f"{machine_id}_{gateway_id}_{handler_02_id}_20201216-080000.280214_2.pkl"
#         tmp_file_6 = tmp_path / f"{machine_id}_{gateway_id}_{handler_02_id}_20201216-080001.853298_3.pkl"
#         tmp_file_7 = tmp_path / f"{machine_id}_{gateway_id}_{handler_03_id}_20201216-075958.708970_1.pkl"
#         tmp_file_8 = tmp_path / f"{machine_id}_{gateway_id}_{handler_03_id}_20201216-080000.280215_2.pkl"
#         tmp_file_9 = tmp_path / f"{machine_id}_{gateway_id}_{handler_03_id}_20201216-080001.853299_3.pkl"

#         tmp_file_1.write_text("")
#         tmp_file_2.write_text("")
#         tmp_file_3.write_text("")
#         tmp_file_4.write_text("")
#         tmp_file_5.write_text("")
#         tmp_file_6.write_text("")
#         tmp_file_7.write_text("")
#         tmp_file_8.write_text("")
#         tmp_file_9.write_text("")

#         actual = FileManager.get_pickle_file_list(machine_id, tmp_path, handlers=handlers)

#         expected = [
#             [tmp_file_1._str, tmp_file_4._str, tmp_file_7._str],
#             [tmp_file_2._str, tmp_file_5._str, tmp_file_8._str],
#             [tmp_file_3._str, tmp_file_6._str, tmp_file_9._str],
#         ]

#         assert actual == expected

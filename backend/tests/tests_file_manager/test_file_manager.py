import pathlib
from datetime import datetime, timedelta
from backend.elastic_manager.elastic_manager import ElasticManager
from backend.file_manager.file_manager import FileManager, FileInfo


class TestCreateFileTimestamp:
    def test_normal(self):
        """ファイル名からdatetime型のタイムスタンプを生成出来ること"""

        filepath = "tmp00/AD-00_20201216-080058.620753.dat"

        actual = FileManager._create_file_timestamp(filepath)
        expected = datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()

        assert actual == expected


class TestCreateFilesInfo:
    def test_normal_file_exists(self, dat_files):
        """正常系：ファイルが存在する"""

        machine_id = "machine-01"

        actual = FileManager.create_files_info(dat_files.tmp_path._str, machine_id, "dat")

        expected = [
            FileInfo(dat_files.tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
            FileInfo(dat_files.tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 59, 620753).timestamp()),
            FileInfo(dat_files.tmp_dat_3._str, datetime(2020, 12, 16, 8, 1, 0, 620753).timestamp()),
            FileInfo(dat_files.tmp_dat_4._str, datetime(2020, 12, 16, 8, 1, 1, 620753).timestamp()),
            FileInfo(dat_files.tmp_dat_5._str, datetime(2020, 12, 16, 8, 1, 2, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_file_exists_not_sorted(self, tmp_path):
        """正常系：ファイルが存在する。ファイルが名前の昇順にソートされること"""

        machine_id: str = "machine-01"

        tmp_dat_1: pathlib.Path = tmp_path / f"{machine_id}_AD-00_20201216-080058.620753.dat"
        tmp_dat_2: pathlib.Path = tmp_path / f"{machine_id}_AD-00_20201216-080040.620753.dat"
        tmp_dat_3: pathlib.Path = tmp_path / f"{machine_id}_AD-00_20201210-080100.620753.dat"

        tmp_dat_1.write_text("")
        tmp_dat_2.write_text("")
        tmp_dat_3.write_text("")

        actual = FileManager.create_files_info(tmp_path._str, machine_id, "dat")

        expected = [
            FileInfo(tmp_dat_3._str, datetime(2020, 12, 10, 8, 1, 0, 620753).timestamp()),
            FileInfo(tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 40, 620753).timestamp()),
            FileInfo(tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_file_not_exists(self):
        """正常系：ファイルが存在しない。"""

        machine_id: str = "machine-01"

        actual = FileManager.create_files_info("dummy_path", machine_id, "dat")

        expected = None

        assert actual == expected


class TestGetTargetFiles:
    def test_normal_target_file_exists(self, dat_files):
        """正常系：5ファイル中3ファイルが対象範囲。以下2ファイルが対象外。
        1ファイル目：20201216-080058.620753
        5ファイル目：20201216-080102.620753
        """

        machine_id: str = "machine-01"

        file_infos = FileManager.create_files_info(dat_files.tmp_path._str, machine_id, "dat")

        setup_time = datetime(2020, 12, 16, 8, 0, 59, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 2, 0).timestamp()
        actual = FileManager.get_target_files(file_infos, setup_time, end_time)

        expected = [
            FileInfo(dat_files.tmp_dat_2._str, datetime(2020, 12, 16, 8, 0, 59, 620753).timestamp()),
            FileInfo(dat_files.tmp_dat_3._str, datetime(2020, 12, 16, 8, 1, 0, 620753).timestamp()),
            FileInfo(dat_files.tmp_dat_4._str, datetime(2020, 12, 16, 8, 1, 1, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_no_target_file(self, dat_files):
        """正常系：対象ファイルなし"""

        machine_id: str = "machine-01"

        file_infos = FileManager.create_files_info(dat_files.tmp_path._str, machine_id, "dat")

        setup_time = datetime(2020, 12, 16, 8, 1, 3, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 5, 0).timestamp()
        actual = FileManager.get_target_files(file_infos, setup_time, end_time)

        expected = []

        assert actual == expected


class TestGetNotTargetFiles:
    def test_normal_not_target_file_exists(self, dat_files):
        """正常系：5ファイル中3ファイルが対象範囲外。以下2ファイルが対象外。
        1ファイル目：20201216-080058.620753
        5ファイル目：20201216-080102.620753
        """

        machine_id: str = "machine-01"

        file_infos = FileManager.create_files_info(dat_files.tmp_path._str, machine_id, "dat")

        setup_time = datetime(2020, 12, 16, 8, 0, 59, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 2, 0).timestamp()
        actual = FileManager.get_not_target_files(file_infos, setup_time, end_time)

        expected = [
            FileInfo(dat_files.tmp_dat_1._str, datetime(2020, 12, 16, 8, 0, 58, 620753).timestamp()),
            FileInfo(dat_files.tmp_dat_5._str, datetime(2020, 12, 16, 8, 1, 2, 620753).timestamp()),
        ]

        assert actual == expected

    def test_normal_all_files_are_target(self, dat_files):
        """正常系：すべて対象ファイル（対象外ファイルなし）"""

        machine_id: str = "machine-01"

        file_infos = FileManager.create_files_info(dat_files.tmp_path._str, machine_id, "dat")

        setup_time = datetime(2020, 12, 16, 8, 0, 58, 0).timestamp()
        end_time = datetime(2020, 12, 16, 8, 1, 10, 0).timestamp()
        actual = FileManager.get_not_target_files(file_infos, setup_time, end_time)

        expected = []

        assert actual == expected

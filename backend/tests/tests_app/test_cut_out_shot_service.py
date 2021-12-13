from typing import List

import pytest
from backend.app.services.cut_out_shot_service import CutOutShotService
from backend.common import common
from backend.file_manager.file_manager import FileManager


class TestAutoCutOutShot:
    @pytest.fixture
    def init(self):
        self.machine_id = "test-machine-01"

    def test_no_files_in_dir(self, db, mocker, init):
        """データ収集完了済みで、pklファイルが存在しない場合"""

        get_files_info_mock = mocker.patch.object(FileManager, "get_files", return_value=[])
        get_collect_status_mock = mocker.patch.object(
            CutOutShotService, "get_collect_status", return_value=common.COLLECT_STATUS.RECORDED.value
        )

        CutOutShotService.auto_cut_out_shot(db, self.machine_id)

        get_files_info_mock.assert_called_once()
        get_collect_status_mock.assert_called_once_with(self.machine_id)


class TestGetTargetFiles:
    def test_no_target_files(self, pkl_files):
        """pklファイルが存在するがすでに処理済みの場合"""

        all_files: List[str] = [
            pkl_files.tmp_pkl_1._str,
            pkl_files.tmp_pkl_2._str,
            pkl_files.tmp_pkl_3._str,
            pkl_files.tmp_pkl_4._str,
            pkl_files.tmp_pkl_5._str,
        ]

        has_been_processed: List[str] = [
            pkl_files.tmp_pkl_1._str,
            pkl_files.tmp_pkl_2._str,
            pkl_files.tmp_pkl_3._str,
            pkl_files.tmp_pkl_4._str,
            pkl_files.tmp_pkl_5._str,
        ]

        target_files = CutOutShotService.get_target_files(all_files, has_been_processed)

        assert target_files == []

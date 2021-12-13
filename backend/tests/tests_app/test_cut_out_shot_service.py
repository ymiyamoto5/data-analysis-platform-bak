import pytest
from backend.app.services.cut_out_shot_service import CutOutShotService


class TestAutoCutOutShot:
    @pytest.fixture
    def init(self):
        self.machine_id = "test-machine-01"

    def test_no_files_in_dir(self, db, mocker, init):
        mocker.patch.object(CutOutShotService, "get_files_info", return_value=[])
        CutOutShotService.auto_cut_out_shot(db, self.machine_id)

        assert True

    def test_no_target_files(self):
        pass

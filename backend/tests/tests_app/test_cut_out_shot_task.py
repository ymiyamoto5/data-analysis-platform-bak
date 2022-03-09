import pytest
from backend.app.worker.tasks import cut_out_shot
from backend.common import common


class TestAutoCutOutShotTask:
    @pytest.mark.skip(reason="ジョブ実行のみ（デバッグ用）")
    def test_normal_multi_handler(self, db, mocker):
        machine_id = "test-machine-01"
        sensor_type = common.CUT_OUT_SHOT_SENSOR_TYPES[0]
        mocker.patch.object(cut_out_shot, "create_shots_index_set")
        cut_out_shot.auto_cut_out_shot_task(machine_id=machine_id, sensor_type=sensor_type, debug_mode=True)


class TestGetTargetFiles:
    def test_normal_single_handler(self):
        all_files = [["/mnt/datadrive/a.pkl"], ["/mnt/datadrive/b.pkl"], ["/mnt/datadrive/c.pkl"]]
        has_been_processed = [["/mnt/datadrive/a.pkl"], ["/mnt/datadrive/b.pkl"]]

        actual = cut_out_shot.get_target_files(all_files, has_been_processed)
        expected = [["/mnt/datadrive/c.pkl"]]

        assert actual == expected

    def test_normal_multi_handler(self):
        all_files = [
            ["/mnt/datadrive/a_1.pkl", "/mnt/datadrive/a_2.pkl"],
            ["/mnt/datadrive/b_1.pkl", "/mnt/datadrive/b_2.pkl"],
            ["/mnt/datadrive/c_1.pkl", "/mnt/datadrive/c_2.pkl"],
            ["/mnt/datadrive/d_1.pkl", "/mnt/datadrive/d_2.pkl"],
        ]
        has_been_processed = [
            ["/mnt/datadrive/a_1.pkl", "/mnt/datadrive/a_2.pkl"],
            ["/mnt/datadrive/b_1.pkl", "/mnt/datadrive/b_2.pkl"],
        ]

        actual = cut_out_shot.get_target_files(all_files, has_been_processed)
        expected = [
            ["/mnt/datadrive/c_1.pkl", "/mnt/datadrive/c_2.pkl"],
            ["/mnt/datadrive/d_1.pkl", "/mnt/datadrive/d_2.pkl"],
        ]

        assert actual == expected

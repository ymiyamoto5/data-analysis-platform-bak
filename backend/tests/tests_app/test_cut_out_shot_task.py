from backend.app.worker.tasks.cut_out_shot import get_target_files


class TestGetTargetFiles:
    def test_normal_single_handler(self):
        all_files = [["/mnt/datadrive/a.pkl"], ["/mnt/datadrive/b.pkl"], ["/mnt/datadrive/c.pkl"]]
        has_been_processed = [["/mnt/datadrive/a.pkl"], ["/mnt/datadrive/b.pkl"]]

        actual = get_target_files(all_files, has_been_processed)
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

        actual = get_target_files(all_files, has_been_processed)
        expected = [
            ["/mnt/datadrive/c_1.pkl", "/mnt/datadrive/c_2.pkl"],
            ["/mnt/datadrive/d_1.pkl", "/mnt/datadrive/d_2.pkl"],
        ]

        assert actual == expected

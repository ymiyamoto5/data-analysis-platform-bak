from backend.app.worker.tasks.cut_out_shot import get_target_files


class TestGetTargetFiles:
    def test_normal(self):
        all_files = ["/mnt/datadrive/a.pkl", "/mnt/datadrive/b.pkl", "/mnt/datadrive/c.pkl"]
        has_been_processed = ["/mnt/datadrive/a.pkl", "/mnt/datadrive/b.pkl"]

        actual = get_target_files(all_files, has_been_processed)
        expected = ["/mnt/datadrive/c.pkl"]

        assert actual == expected

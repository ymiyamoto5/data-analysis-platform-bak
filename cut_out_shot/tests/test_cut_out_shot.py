import pytest
import os
import sys
import pytest_mock

from .. import cut_out_shot


class TestGetEvents:
    def test_normal(self, mocker):
        expected = [
            {"event_type": "setup", "occurred_time": "2020-12-01T00:00:00.000"},
            {"event_type": "start", "occurred_time": "2020-12-01T00:10:00.000"},
            {"event_type": "stop", "occurred_time": "2020-12-01T00:20:00.000"},
        ]
        mocker.patch("elastic_manager.ElasticManager.get_all_doc", return_value=expected)

        cos = cut_out_shot.CutOutShot()
        actual = cos._get_events(suffix="20201201000000")

        assert expected == actual


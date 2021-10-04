from datetime import datetime
from typing import List

import pandas as pd
from backend.cut_out_shot.cut_out_shot import CutOutShot
from pandas.testing import assert_frame_equal


class TestCutOutShotByPulse:
    """パルス信号からの切り出しテスト。物理変換後データでのテストとなっている。"""

    def test_normal_1(self, rawdata_pulse_df, db):

        cut_out_shot = CutOutShot(machine_id="machine-02", target="20201201103011", previous_size=0, margin=0, db=db)
        cut_out_shot._cut_out_shot_by_pulse(rawdata_pulse_df, 1.0)

        actual: List[dict] = cut_out_shot.cut_out_targets
        actual_df = pd.DataFrame(actual)

        expected = [
            # 切り出し区間1-1
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp(),
                "sequential_number": 0,
                "sequential_number_by_shot": 0,
                "rawdata_sequential_number": 1,
                "shot_number": 1,
                "tags": [],
                "pulse": 1,
                "load01": 0.155,
                "load02": 0.171,
                "load03": 0.180,
                "load04": 0.146,
            },
            # 切り出し区間1-2
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
                "sequential_number": 1,
                "sequential_number_by_shot": 1,
                "rawdata_sequential_number": 2,
                "shot_number": 1,
                "tags": [],
                "pulse": 1,
                "load01": 1.574,
                "load02": 1.308,
                "load03": 1.363,
                "load04": 1.432,
            },
            # 切り出し区間2-1
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
                "sequential_number": 2,
                "sequential_number_by_shot": 0,
                "rawdata_sequential_number": 4,
                "shot_number": 2,
                "tags": [],
                "pulse": 1,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
            },
        ]

        expected_df = pd.DataFrame(expected)

        assert_frame_equal(actual_df, expected_df, check_like=True)

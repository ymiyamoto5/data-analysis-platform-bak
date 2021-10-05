from datetime import datetime
from typing import List

import pandas as pd
from backend.cut_out_shot.displacement_cutter import DisplacementCutter
from pandas.testing import assert_frame_equal


class TestCutOutShot:
    """切り出しテスト。物理変換後データでのテストとなっている。"""

    def test_normal_1(self, rawdata_df, displacement_sensors):
        """正常系：start_displacememt: 47.0, end_displacememt: 34.0。
        全13サンプル中8サンプルが切り出される。
        """

        displacement_cutter = DisplacementCutter(start_displacement=47.0, end_displacement=34.0, margin=0.1)
        displacement_cutter.set_sensors(displacement_sensors)

        displacement_cutter.cut_out_shot(rawdata_df)
        actual: List[dict] = displacement_cutter.cut_out_targets
        actual_df = pd.DataFrame(actual)

        expected = [
            # 切り出し区間1-1
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
                "sequential_number": 0,
                "sequential_number_by_shot": 0,
                "rawdata_sequential_number": 2,
                "shot_number": 1,
                "tags": [],
                "displacement": 47.0,
                "load01": 1.574,
                "load02": 1.308,
                "load03": 1.363,
                "load04": 1.432,
            },
            # 切り出し区間1-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
                "sequential_number": 1,
                "sequential_number_by_shot": 1,
                "rawdata_sequential_number": 3,
                "shot_number": 1,
                "tags": [],
                "displacement": 47.1,
                "load01": 1.500,
                "load02": 1.200,
                "load03": 1.300,
                "load04": 1.400,
            },
            # 切り出し区間1-3
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
                "sequential_number": 2,
                "sequential_number_by_shot": 2,
                "rawdata_sequential_number": 4,
                "shot_number": 1,
                "tags": [],
                "displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
            },
            # 切り出し区間2-1
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 19, 111111).timestamp(),
                "sequential_number": 3,
                "sequential_number_by_shot": 0,
                "rawdata_sequential_number": 9,
                "shot_number": 2,
                "tags": [],
                "displacement": 47.0,
                "load01": 1.574,
                "load02": 1.308,
                "load03": 1.363,
                "load04": 1.432,
            },
            # 切り出し区間2-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 20, 111111).timestamp(),
                "sequential_number": 4,
                "sequential_number_by_shot": 1,
                "rawdata_sequential_number": 10,
                "shot_number": 2,
                "tags": [],
                "displacement": 47.1,
                "load01": 1.500,
                "load02": 1.200,
                "load03": 1.300,
                "load04": 1.400,
            },
            # 切り出し区間2-3
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
                "sequential_number": 5,
                "sequential_number_by_shot": 2,
                "rawdata_sequential_number": 11,
                "shot_number": 2,
                "tags": [],
                "displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
            },
        ]

        expected_df = pd.DataFrame(expected)

        assert_frame_equal(actual_df, expected_df, check_like=True)

    def test_normal_2(self, rawdata_df, displacement_sensors):
        """正常系：start_displacememt: 46.9, end_displacememt: 34.0。
        全13サンプル中2サンプルが切り出される。
        """

        displacement_cutter = DisplacementCutter(start_displacement=46.9, end_displacement=34.0, margin=0.1)
        displacement_cutter.set_sensors(displacement_sensors)

        displacement_cutter.cut_out_shot(rawdata_df)
        actual: List[dict] = displacement_cutter.cut_out_targets
        actual_df = pd.DataFrame(actual)

        expected = [
            # 切り出し区間1-3
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
                "sequential_number": 0,
                "sequential_number_by_shot": 0,
                "rawdata_sequential_number": 4,
                "shot_number": 1,
                "tags": [],
                "displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
            },
            # 切り出し区間2-3
            {
                "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
                "sequential_number": 1,
                "sequential_number_by_shot": 0,
                "rawdata_sequential_number": 11,
                "shot_number": 2,
                "tags": [],
                "displacement": 34.961,
                "load01": -0.256,
                "load02": -0.078,
                "load03": 0.881,
                "load04": 0.454,
            },
        ]

        expected_df = pd.DataFrame(expected)

        assert_frame_equal(actual_df, expected_df, check_like=True)

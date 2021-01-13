import pytest
import pandas as pd
from datetime import datetime
from pandas.core.frame import DataFrame
from typing import List

from cut_out_shot import cut_out_shot


@pytest.fixture
def target():
    """ 変換式のみ定義したCutOutShotインスタンス fixture"""

    displacement_func = lambda x: x * 1.0
    load01_func = lambda x: x * 1.0
    load02_func = lambda x: x * 1.0
    load03_func = lambda x: x * 1.0
    load04_func = lambda x: x * 1.0

    instance = cut_out_shot.CutOutShot(
        displacement_func=displacement_func,
        load01_func=load01_func,
        load02_func=load02_func,
        load03_func=load03_func,
        load04_func=load04_func,
    )

    yield instance

    del instance


@pytest.fixture
def rawdata_df():
    """ 生データのDataFrame fixture。
        切り出しの開始変位値 47.0, 終了変位値 34.0 を想定したデータ。
    """

    rawdata: List[dict] = [
        # 切り出し区間前1
        {
            "timestamp": datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp(),
            "displacement": 49.284,
            "load01": 0.223,
            "load02": 0.211,
            "load03": 0.200,
            "load04": 0.218,
        },
        # 切り出し区間前2
        {
            "timestamp": datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp(),
            "displacement": 47.534,
            "load01": 0.155,
            "load02": 0.171,
            "load03": 0.180,
            "load04": 0.146,
        },
        # 切り出し区間1-1
        {
            "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
            "displacement": 47.0,
            "load01": 1.574,
            "load02": 1.308,
            "load03": 1.363,
            "load04": 1.432,
        },
        # 切り出し区間1-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
        {
            "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
            "displacement": 47.1,
            "load01": 1.500,
            "load02": 1.200,
            "load03": 1.300,
            "load04": 1.400,
        },
        # 切り出し区間1-3
        {
            "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
            "displacement": 34.961,
            "load01": -0.256,
            "load02": -0.078,
            "load03": 0.881,
            "load04": 0.454,
        },
        # 切り出し区間後1
        {
            "timestamp": datetime(2020, 12, 1, 10, 30, 15, 111111).timestamp(),
            "displacement": 30.599,
            "load01": -0.130,
            "load02": 0.020,
            "load03": 0.483,
            "load04": 0.419,
        },
        # 切り出し区間後2
        {
            "timestamp": datetime(2020, 12, 1, 10, 30, 16, 111111).timestamp(),
            "displacement": 24.867,
            "load01": -0.052,
            "load02": 0.035,
            "load03": 0.402,
            "load04": 0.278,
        },
        # 切り出し区間後3(変位にmargin=0.1を加算した場合、ショットの終了と見做されない変位値)
        {
            "timestamp": datetime(2020, 12, 1, 10, 30, 17, 111111).timestamp(),
            "displacement": 47.100,
            "load01": 0.155,
            "load02": 0.171,
            "load03": 0.180,
            "load04": 0.146,
        },
        # 切り出し区間後4(ショット区間終了）
        {
            "timestamp": datetime(2020, 12, 1, 10, 30, 18, 111111).timestamp(),
            "displacement": 47.150,
            "load01": 0.156,
            "load02": 0.172,
            "load03": 0.181,
            "load04": 0.147,
        },
        # 切り出し区間2-1
        {
            "timestamp": datetime(2020, 12, 1, 10, 30, 19, 111111).timestamp(),
            "displacement": 47.0,
            "load01": 1.574,
            "load02": 1.308,
            "load03": 1.363,
            "load04": 1.432,
        },
        # 切り出し区間2-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
        {
            "timestamp": datetime(2020, 12, 1, 10, 30, 20, 111111).timestamp(),
            "displacement": 47.1,
            "load01": 1.500,
            "load02": 1.200,
            "load03": 1.300,
            "load04": 1.400,
        },
        # 切り出し区間2-3
        {
            "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
            "displacement": 34.961,
            "load01": -0.256,
            "load02": -0.078,
            "load03": 0.881,
            "load04": 0.454,
        },
        # 切り出し区間後
        {
            "timestamp": datetime(2020, 12, 1, 10, 30, 22, 111111).timestamp(),
            "displacement": 30.599,
            "load01": -0.130,
            "load02": 0.020,
            "load03": 0.483,
            "load04": 0.419,
        },
    ]

    rawdata_df: DataFrame = pd.DataFrame(rawdata)
    yield rawdata_df


@pytest.fixture
def events_list():
    """ events_indexのデータfixture。
        本fixtureはsetup->start->stopの基本ケースのみを用意する。
        また、rawdata_df fixtureの全データがstart-end区間に含まれる。
        pauseやtag等の特殊イベントは各テストケースで用意すること。
    """

    events: List[dict] = [
        {"event_type": "setup", "occrred_time": datetime(2020, 12, 1, 10, 30, 0, 111111).timestamp()},
        {"event_type": "start", "occrred_time": datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp()},
        {"event_type": "end", "occrred_time": datetime(2020, 12, 1, 10, 30, 30, 111111).timestamp()},
    ]

    yield events

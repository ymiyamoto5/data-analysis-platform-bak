"""
 ==================================
  conftest.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import os
import pathlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

import pandas as pd
import pytest
from backend.app.db.session import SessionLocal
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_event import DataCollectHistoryEvent
from backend.app.models.data_collect_history_gateway import DataCollectHistoryGateway
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
from backend.app.models.data_collect_history_sensor import DataCollectHistorySensor
from backend.app.models.sensor import Sensor
from backend.common import common
from backend.cut_out_shot.cut_out_shot import CutOutShot
from backend.cut_out_shot.stroke_displacement_cutter import StrokeDisplacementCutter
from pandas.core.frame import DataFrame


@pytest.fixture()
def stroke_displacement_target():
    """CutOutShotインスタンス fixture"""

    machine_id = "machine-01"
    target_date_str = "20201201103011"

    sensors = create_stroke_displacement_sensors()
    data_collect_history = create_data_collect_history()
    cutter = StrokeDisplacementCutter(start_stroke_displacement=47.0, end_stroke_displacement=34.0, margin=0.1, sensors=sensors)  # dummy

    instance = CutOutShot(
        cutter=cutter,
        data_collect_history=data_collect_history,
        handlers=data_collect_history.data_collect_history_gateways[0].data_collect_history_handlers,
        sensors=sensors,
        machine_id=machine_id,
        target=target_date_str,
    )

    yield instance

    del instance


@pytest.fixture()
def pulse_target():
    """CutOutShotインスタンス fixture"""

    machine_id = "machine-01"
    target_date_str = "20201201103011"

    sensors = create_pulse_sensors()

    cutter = StrokeDisplacementCutter(start_stroke_displacement=0, end_stroke_displacement=0, margin=0, sensors=sensors)  # dummy
    instance = CutOutShot(cutter=cutter, machine_id=machine_id, target=target_date_str, sampling_frequency=100_000, sensors=sensors)

    yield instance

    del instance


@pytest.fixture(scope="module", autouse=True)
def db():
    db = SessionLocal()
    yield db


@pytest.fixture
def rawdata_df():
    """生データ（物理変換後）のDataFrame fixture。
    切り出しの開始ストローク変位値 47.0, 終了ストローク変位値 34.0 を想定したデータ。
    """

    rawdata: List[dict] = [
        # 切り出し区間前1
        {
            "sequential_number": 0,
            "timestamp": datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp(),
            "stroke_displacement": 49.284,
            "load01": 0.223,
            "load02": 0.211,
            "load03": 0.200,
            "load04": 0.218,
        },
        # 切り出し区間前2
        {
            "sequential_number": 1,
            "timestamp": datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp(),
            "stroke_displacement": 47.534,
            "load01": 0.155,
            "load02": 0.171,
            "load03": 0.180,
            "load04": 0.146,
        },
        # 切り出し区間1-1
        {
            "sequential_number": 2,
            "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
            "stroke_displacement": 47.0,
            "load01": 1.574,
            "load02": 1.308,
            "load03": 1.363,
            "load04": 1.432,
        },
        # 切り出し区間1-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
        {
            "sequential_number": 3,
            "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
            "stroke_displacement": 47.1,
            "load01": 1.500,
            "load02": 1.200,
            "load03": 1.300,
            "load04": 1.400,
        },
        # 切り出し区間1-3
        {
            "sequential_number": 4,
            "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
            "stroke_displacement": 34.961,
            "load01": -0.256,
            "load02": -0.078,
            "load03": 0.881,
            "load04": 0.454,
        },
        # 切り出し区間後1
        {
            "sequential_number": 5,
            "timestamp": datetime(2020, 12, 1, 10, 30, 15, 111111).timestamp(),
            "stroke_displacement": 30.599,
            "load01": -0.130,
            "load02": 0.020,
            "load03": 0.483,
            "load04": 0.419,
        },
        # 切り出し区間後2
        {
            "sequential_number": 6,
            "timestamp": datetime(2020, 12, 1, 10, 30, 16, 111111).timestamp(),
            "stroke_displacement": 24.867,
            "load01": -0.052,
            "load02": 0.035,
            "load03": 0.402,
            "load04": 0.278,
        },
        # 切り出し区間後3(ストローク変位にmargin=0.1を加算した場合、ショットの終了と見做されないストローク変位値)
        {
            "sequential_number": 7,
            "timestamp": datetime(2020, 12, 1, 10, 30, 17, 111111).timestamp(),
            "stroke_displacement": 47.100,
            "load01": 0.155,
            "load02": 0.171,
            "load03": 0.180,
            "load04": 0.146,
        },
        # 切り出し区間後4(ショット区間終了）
        {
            "sequential_number": 8,
            "timestamp": datetime(2020, 12, 1, 10, 30, 18, 111111).timestamp(),
            "stroke_displacement": 47.150,
            "load01": 0.156,
            "load02": 0.172,
            "load03": 0.181,
            "load04": 0.147,
        },
        # 切り出し区間2-1
        {
            "sequential_number": 9,
            "timestamp": datetime(2020, 12, 1, 10, 30, 19, 111111).timestamp(),
            "stroke_displacement": 47.0,
            "load01": 1.574,
            "load02": 1.308,
            "load03": 1.363,
            "load04": 1.432,
        },
        # 切り出し区間2-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
        {
            "sequential_number": 10,
            "timestamp": datetime(2020, 12, 1, 10, 30, 20, 111111).timestamp(),
            "stroke_displacement": 47.1,
            "load01": 1.500,
            "load02": 1.200,
            "load03": 1.300,
            "load04": 1.400,
        },
        # 切り出し区間2-3
        {
            "sequential_number": 11,
            "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
            "stroke_displacement": 34.961,
            "load01": -0.256,
            "load02": -0.078,
            "load03": 0.881,
            "load04": 0.454,
        },
        # 切り出し区間後
        {
            "sequential_number": 12,
            "timestamp": datetime(2020, 12, 1, 10, 30, 22, 111111).timestamp(),
            "stroke_displacement": 30.599,
            "load01": -0.130,
            "load02": 0.020,
            "load03": 0.483,
            "load04": 0.419,
        },
    ]

    rawdata_df: DataFrame = pd.DataFrame(rawdata)
    yield rawdata_df

    del rawdata_df


@pytest.fixture
def shots_meta_df():
    """ショットメタデータのfixture"""

    shots_meta = [
        {"shot_number": 1, "spm": 10.0, "num_of_samples_in_cut_out": 400001},
        {"shot_number": 2, "spm": 80.0, "num_of_samples_in_cut_out": 3000},
        {"shot_number": 3, "spm": 40.0, "num_of_samples_in_cut_out": 6000},
        {"shot_number": 4, "spm": 60.0, "num_of_samples_in_cut_out": 4000},
    ]

    shots_meta_df: DataFrame = pd.DataFrame(shots_meta)

    yield shots_meta_df

    del shots_meta_df


@pytest.fixture
def rawdata_pulse_df():
    """パルス信号生データ（物理変換後）のDataFrame fixture。
    sequential_number: 1, 2, 4が切り出し対象
    """

    rawdata_pulse: List[dict] = [
        # 切り出し区間前1
        {
            "sequential_number": 0,
            "timestamp": datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp(),
            "pulse": 0,
            "load01": 0.223,
            "load02": 0.211,
            "load03": 0.200,
            "load04": 0.218,
        },
        # 切り出し区間1-1
        {
            "sequential_number": 1,
            "timestamp": datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp(),
            "pulse": 1,
            "load01": 0.155,
            "load02": 0.171,
            "load03": 0.180,
            "load04": 0.146,
        },
        # 切り出し区間1-2
        {
            "sequential_number": 2,
            "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
            "pulse": 1,
            "load01": 1.574,
            "load02": 1.308,
            "load03": 1.363,
            "load04": 1.432,
        },
        # 切り出し範囲外
        {
            "sequential_number": 3,
            "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
            "pulse": 0,
            "load01": 1.500,
            "load02": 1.200,
            "load03": 1.300,
            "load04": 1.400,
        },
        # 切り出し区間2-1
        {
            "sequential_number": 4,
            "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
            "pulse": 1,
            "load01": -0.256,
            "load02": -0.078,
            "load03": 0.881,
            "load04": 0.454,
        },
        # 切り出し範囲外
        {
            "sequential_number": 5,
            "timestamp": datetime(2020, 12, 1, 10, 30, 15, 111111).timestamp(),
            "pulse": 0,
            "load01": -0.130,
            "load02": 0.020,
            "load03": 0.483,
            "load04": 0.419,
        },
    ]

    rawdata_pulse_df: DataFrame = pd.DataFrame(rawdata_pulse)
    yield rawdata_pulse_df

    del rawdata_pulse_df


@pytest.fixture
def stroke_displacement_sensors():
    stroke_displacement_sensors: List[Sensor] = create_stroke_displacement_sensors()

    yield stroke_displacement_sensors


def create_stroke_displacement_sensors():
    return [
        Sensor(
            machine_id="machine-01",
            sensor_id="stroke_displacement",
            sensor_name="stroke_displacement",
            sensor_type_id="stroke_displacement",
            slope=1.0,
            intercept=0.0,
        ),
        Sensor(
            machine_id="machine-01",
            sensor_id="load01",
            sensor_name="load01",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
        Sensor(
            machine_id="machine-01",
            sensor_id="load02",
            sensor_name="load02",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
        Sensor(
            machine_id="machine-01",
            sensor_id="load03",
            sensor_name="load03",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
        Sensor(
            machine_id="machine-01",
            sensor_id="load04",
            sensor_name="load04",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
    ]


@pytest.fixture
def pulse_sensors():
    pulse_sensors: List[Sensor] = create_pulse_sensors()

    yield pulse_sensors


def create_pulse_sensors():
    return [
        Sensor(
            machine_id="machine-02",
            sensor_id="pulse",
            sensor_name="pulse",
            sensor_type_id="pulse",
            slope=1.0,
            intercept=0.0,
        ),
        Sensor(
            machine_id="machine-02",
            sensor_id="load01",
            sensor_name="load01",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
        Sensor(
            machine_id="machine-02",
            sensor_id="load02",
            sensor_name="load02",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
        Sensor(
            machine_id="machine-02",
            sensor_id="load03",
            sensor_name="load03",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
        Sensor(
            machine_id="machine-02",
            sensor_id="load04",
            sensor_name="load04",
            sensor_type_id="load",
            slope=1.0,
            intercept=0.0,
        ),
    ]


def create_data_collect_history():
    started_at = datetime(2020, 12, 1, 10, 30, 10, 111111)

    return DataCollectHistory(
        machine_id="machine-01",
        machine_name="プレス機",
        machine_type_id=1,
        started_at=started_at + timedelta(hours=-9),
        ended_at=started_at + timedelta(hours=-9) + timedelta(hours=1),
        data_collect_history_events=[
            DataCollectHistoryEvent(
                event_id=0,
                event_name=common.COLLECT_STATUS.SETUP.value,
                occurred_at=started_at + timedelta(hours=-9),
            ),
            DataCollectHistoryEvent(
                event_id=1,
                event_name=common.COLLECT_STATUS.START.value,
                occurred_at=started_at + timedelta(hours=-9),
            ),
            DataCollectHistoryEvent(
                event_id=2,
                event_name=common.COLLECT_STATUS.STOP.value,
                occurred_at=started_at + timedelta(hours=-9) + timedelta(minutes=120),
            ),
            DataCollectHistoryEvent(
                event_id=3,
                event_name=common.COLLECT_STATUS.RECORDED.value,
                occurred_at=started_at + timedelta(hours=-9) + timedelta(minutes=121),
            ),
        ],
        data_collect_history_gateways=[
            DataCollectHistoryGateway(
                data_collect_history_id=1,
                gateway_id="gateway-01",
                log_level=5,
                data_collect_history_handlers=[
                    DataCollectHistoryHandler(
                        data_collect_history_id=1,
                        handler_id="handler-01",
                        handler_type="USB_1608HS",
                        adc_serial_num="999999",
                        sampling_frequency=100000,
                        sampling_ch_num=3,
                        filewrite_time=1,
                        is_primary=True,
                        is_cut_out_target=True,
                        is_multi=True,
                        data_collect_history_sensors=[
                            DataCollectHistorySensor(
                                sensor_id="stroke_displacement",
                                sensor_name="ストローク変位",
                                sensor_type_id="stroke_displacement",
                                slope=1.0,
                                intercept=0.0,
                            ),
                            DataCollectHistorySensor(
                                sensor_id="load01",
                                sensor_name="load01",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                            ),
                            DataCollectHistorySensor(
                                sensor_id="load02",
                                sensor_name="load02",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                            ),
                        ],
                    ),
                    DataCollectHistoryHandler(
                        data_collect_history_id=1,
                        handler_id="handler-02",
                        handler_type="USB_1608HS",
                        adc_serial_num="999990",
                        sampling_frequency=100000,
                        sampling_ch_num=2,
                        filewrite_time=1,
                        is_primary=False,
                        is_cut_out_target=True,
                        is_multi=True,
                        data_collect_history_sensors=[
                            DataCollectHistorySensor(
                                sensor_id="load03",
                                sensor_name="load03",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                            ),
                            DataCollectHistorySensor(
                                sensor_id="load04",
                                sensor_name="load04",
                                sensor_type_id="load",
                                slope=1.0,
                                intercept=0.0,
                            ),
                        ],
                    ),
                ],
            )
        ],
    )


@dataclass
class PklFiles:
    tmp_path: pathlib.Path
    tmp_pkl_1: pathlib.Path
    tmp_pkl_2: pathlib.Path
    tmp_pkl_3: pathlib.Path
    tmp_pkl_4: pathlib.Path
    # tmp_pkl_5: pathlib.Path


@pytest.fixture
def pkl_files_single_handler(tmp_path):
    """pklファイルのfixture"""

    processed_dir: str = "20211111110000"
    machine_id: str = "machine-01"
    handler_id_1: str = "handler-01"
    tmp_processed_dir = tmp_path / f"{processed_dir}"

    os.mkdir(tmp_processed_dir)

    tmp_pkl_1: pathlib.Path = tmp_processed_dir / f"{machine_id}_{handler_id_1}_20211111-110001.620753_1.pkl"
    tmp_pkl_2: pathlib.Path = tmp_processed_dir / f"{machine_id}_{handler_id_1}_20211111-110002.620753_2.pkl"

    rawdata_1 = [
        # 切り出し区間前1
        {
            "sequential_number": 0,
            "timestamp": datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp(),
            "stroke_displacement": 49.284,
            "load01": 0.223,
            "load02": 0.211,
            "load03": 0.200,
            "load04": 0.218,
        },
        # 切り出し区間前2
        {
            "sequential_number": 1,
            "timestamp": datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp(),
            "stroke_displacement": 47.534,
            "load01": 0.155,
            "load02": 0.171,
            "load03": 0.180,
            "load04": 0.146,
        },
        # 切り出し区間1-1
        {
            "sequential_number": 2,
            "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
            "stroke_displacement": 47.0,
            "load01": 1.574,
            "load02": 1.308,
            "load03": 1.363,
            "load04": 1.432,
        },
        # 切り出し区間1-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
        {
            "sequential_number": 3,
            "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
            "stroke_displacement": 47.1,
            "load01": 1.500,
            "load02": 1.200,
            "load03": 1.300,
            "load04": 1.400,
        },
    ]
    df_1 = pd.DataFrame(rawdata_1)
    df_1.to_pickle(tmp_pkl_1)

    rawdata_2 = [
        # 切り出し区間1-3
        {
            "sequential_number": 4,
            "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
            "stroke_displacement": 34.961,
            "load01": -0.256,
            "load02": -0.078,
            "load03": 0.881,
            "load04": 0.454,
        },
        # 切り出し区間後1
        {
            "sequential_number": 5,
            "timestamp": datetime(2020, 12, 1, 10, 30, 15, 111111).timestamp(),
            "stroke_displacement": 30.599,
            "load01": -0.130,
            "load02": 0.020,
            "load03": 0.483,
            "load04": 0.419,
        },
        # 切り出し区間後2
        {
            "sequential_number": 6,
            "timestamp": datetime(2020, 12, 1, 10, 30, 16, 111111).timestamp(),
            "stroke_displacement": 24.867,
            "load01": -0.052,
            "load02": 0.035,
            "load03": 0.402,
            "load04": 0.278,
        },
        # 切り出し区間後3(ストローク変位にmargin=0.1を加算した場合、ショットの終了と見做されないストローク変位値)
        {
            "sequential_number": 7,
            "timestamp": datetime(2020, 12, 1, 10, 30, 17, 111111).timestamp(),
            "stroke_displacement": 47.100,
            "load01": 0.155,
            "load02": 0.171,
            "load03": 0.180,
            "load04": 0.146,
        },
        # 切り出し区間後4(ショット区間終了）
        {
            "sequential_number": 8,
            "timestamp": datetime(2020, 12, 1, 10, 30, 18, 111111).timestamp(),
            "stroke_displacement": 47.150,
            "load01": 0.156,
            "load02": 0.172,
            "load03": 0.181,
            "load04": 0.147,
        },
        # 切り出し区間2-1
        {
            "sequential_number": 9,
            "timestamp": datetime(2020, 12, 1, 10, 30, 19, 111111).timestamp(),
            "stroke_displacement": 47.0,
            "load01": 1.574,
            "load02": 1.308,
            "load03": 1.363,
            "load04": 1.432,
        },
        # 切り出し区間2-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
        {
            "sequential_number": 10,
            "timestamp": datetime(2020, 12, 1, 10, 30, 20, 111111).timestamp(),
            "stroke_displacement": 47.1,
            "load01": 1.500,
            "load02": 1.200,
            "load03": 1.300,
            "load04": 1.400,
        },
        # 切り出し区間2-3
        {
            "sequential_number": 11,
            "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
            "stroke_displacement": 34.961,
            "load01": -0.256,
            "load02": -0.078,
            "load03": 0.881,
            "load04": 0.454,
        },
        # 切り出し区間後
        {
            "sequential_number": 12,
            "timestamp": datetime(2020, 12, 1, 10, 30, 22, 111111).timestamp(),
            "stroke_displacement": 30.599,
            "load01": -0.130,
            "load02": 0.020,
            "load03": 0.483,
            "load04": 0.419,
        },
    ]

    df_2 = pd.DataFrame(rawdata_2)
    df_2.to_pickle(tmp_pkl_2)

    pkl_files = PklFiles(tmp_processed_dir, tmp_pkl_1, tmp_pkl_2)

    yield pkl_files


@pytest.fixture
def pkl_files_multi_handler(tmp_path):
    """pklファイルのfixture"""

    processed_dir: str = "20211111110000"
    machine_id: str = "machine-01"
    handler_id_1: str = "handler-01"
    handler_id_2: str = "handler-02"
    tmp_processed_dir = tmp_path / f"{processed_dir}"

    os.mkdir(tmp_processed_dir)

    tmp_pkl_1: pathlib.Path = tmp_processed_dir / f"{machine_id}_{handler_id_1}_20211111-110001.620753_1.pkl"
    tmp_pkl_2: pathlib.Path = tmp_processed_dir / f"{machine_id}_{handler_id_1}_20211111-110002.620753_2.pkl"
    tmp_pkl_3: pathlib.Path = tmp_processed_dir / f"{machine_id}_{handler_id_2}_20211111-110003.620753_1.pkl"
    tmp_pkl_4: pathlib.Path = tmp_processed_dir / f"{machine_id}_{handler_id_2}_20211111-110004.620753_2.pkl"

    rawdata_1 = [
        # 切り出し区間前1
        {
            "sequential_number": 0,
            "timestamp": datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp(),
            "stroke_displacement": 49.284,
            "load01": 0.223,
            "load02": 0.211,
        },
        # 切り出し区間前2
        {
            "sequential_number": 1,
            "timestamp": datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp(),
            "stroke_displacement": 47.534,
            "load01": 0.155,
            "load02": 0.171,
        },
        # 切り出し区間1-1
        {
            "sequential_number": 2,
            "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
            "stroke_displacement": 47.0,
            "load01": 1.574,
            "load02": 1.308,
        },
        # 切り出し区間1-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
        {
            "sequential_number": 3,
            "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
            "stroke_displacement": 47.1,
            "load01": 1.500,
            "load02": 1.200,
        },
    ]
    df_1 = pd.DataFrame(rawdata_1)
    df_1.to_pickle(tmp_pkl_1)

    rawdata_2 = [
        # 切り出し区間1-3
        {
            "sequential_number": 4,
            "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
            "stroke_displacement": 34.961,
            "load01": -0.256,
            "load02": -0.078,
        },
        # 切り出し区間後1
        {
            "sequential_number": 5,
            "timestamp": datetime(2020, 12, 1, 10, 30, 15, 111111).timestamp(),
            "stroke_displacement": 30.599,
            "load01": -0.130,
            "load02": 0.020,
        },
        # 切り出し区間後2
        {
            "sequential_number": 6,
            "timestamp": datetime(2020, 12, 1, 10, 30, 16, 111111).timestamp(),
            "stroke_displacement": 24.867,
            "load01": -0.052,
            "load02": 0.035,
        },
        # 切り出し区間後3(ストローク変位にmargin=0.1を加算した場合、ショットの終了と見做されないストローク変位値)
        {
            "sequential_number": 7,
            "timestamp": datetime(2020, 12, 1, 10, 30, 17, 111111).timestamp(),
            "stroke_displacement": 47.100,
            "load01": 0.155,
            "load02": 0.171,
        },
        # 切り出し区間後4(ショット区間終了）
        {
            "sequential_number": 8,
            "timestamp": datetime(2020, 12, 1, 10, 30, 18, 111111).timestamp(),
            "stroke_displacement": 47.150,
            "load01": 0.156,
            "load02": 0.172,
        },
        # 切り出し区間2-1
        {
            "sequential_number": 9,
            "timestamp": datetime(2020, 12, 1, 10, 30, 19, 111111).timestamp(),
            "stroke_displacement": 47.0,
            "load01": 1.574,
            "load02": 1.308,
        },
        # 切り出し区間2-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
        {
            "sequential_number": 10,
            "timestamp": datetime(2020, 12, 1, 10, 30, 20, 111111).timestamp(),
            "stroke_displacement": 47.1,
            "load01": 1.500,
            "load02": 1.200,
        },
        # 切り出し区間2-3
        {
            "sequential_number": 11,
            "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
            "stroke_displacement": 34.961,
            "load01": -0.256,
            "load02": -0.078,
        },
        # 切り出し区間後
        {
            "sequential_number": 12,
            "timestamp": datetime(2020, 12, 1, 10, 30, 22, 111111).timestamp(),
            "stroke_displacement": 30.599,
            "load01": -0.130,
            "load02": 0.020,
        },
    ]

    df_2 = pd.DataFrame(rawdata_2)
    df_2.to_pickle(tmp_pkl_2)

    rawdata_3 = [
        # 切り出し区間前1
        {
            "sequential_number": 0,
            "timestamp": datetime(2020, 12, 1, 10, 30, 10, 111111).timestamp(),
            "load03": 0.200,
            "load04": 0.218,
        },
        # 切り出し区間前2
        {
            "sequential_number": 1,
            "timestamp": datetime(2020, 12, 1, 10, 30, 11, 111111).timestamp(),
            "load03": 0.180,
            "load04": 0.146,
        },
        # 切り出し区間1-1
        {
            "sequential_number": 2,
            "timestamp": datetime(2020, 12, 1, 10, 30, 12, 111111).timestamp(),
            "load03": 1.363,
            "load04": 1.432,
        },
        # 切り出し区間1-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
        {
            "sequential_number": 3,
            "timestamp": datetime(2020, 12, 1, 10, 30, 13, 111111).timestamp(),
            "load03": 1.300,
            "load04": 1.400,
        },
    ]
    df_3 = pd.DataFrame(rawdata_3)
    df_3.to_pickle(tmp_pkl_3)

    rawdata_4 = [
        # 切り出し区間1-3
        {
            "sequential_number": 4,
            "timestamp": datetime(2020, 12, 1, 10, 30, 14, 111111).timestamp(),
            "load03": 0.881,
            "load04": 0.454,
        },
        # 切り出し区間後1
        {
            "sequential_number": 5,
            "timestamp": datetime(2020, 12, 1, 10, 30, 15, 111111).timestamp(),
            "load03": 0.483,
            "load04": 0.419,
        },
        # 切り出し区間後2
        {
            "sequential_number": 6,
            "timestamp": datetime(2020, 12, 1, 10, 30, 16, 111111).timestamp(),
            "load03": 0.402,
            "load04": 0.278,
        },
        # 切り出し区間後3(ストローク変位にmargin=0.1を加算した場合、ショットの終了と見做されないストローク変位値)
        {
            "sequential_number": 7,
            "timestamp": datetime(2020, 12, 1, 10, 30, 17, 111111).timestamp(),
            "load03": 0.180,
            "load04": 0.146,
        },
        # 切り出し区間後4(ショット区間終了）
        {
            "sequential_number": 8,
            "timestamp": datetime(2020, 12, 1, 10, 30, 18, 111111).timestamp(),
            "load03": 0.181,
            "load04": 0.147,
        },
        # 切り出し区間2-1
        {
            "sequential_number": 9,
            "timestamp": datetime(2020, 12, 1, 10, 30, 19, 111111).timestamp(),
            "load03": 1.363,
            "load04": 1.432,
        },
        # 切り出し区間2-2（margin=0.1により、すぐに切り出し区間が終了しないことの確認用データ）
        {
            "sequential_number": 10,
            "timestamp": datetime(2020, 12, 1, 10, 30, 20, 111111).timestamp(),
            "load03": 1.300,
            "load04": 1.400,
        },
        # 切り出し区間2-3
        {
            "sequential_number": 11,
            "timestamp": datetime(2020, 12, 1, 10, 30, 21, 111111).timestamp(),
            "load03": 0.881,
            "load04": 0.454,
        },
        # 切り出し区間後
        {
            "sequential_number": 12,
            "timestamp": datetime(2020, 12, 1, 10, 30, 22, 111111).timestamp(),
            "load03": 0.483,
            "load04": 0.419,
        },
    ]

    df_4 = pd.DataFrame(rawdata_4)
    df_4.to_pickle(tmp_pkl_4)

    pkl_files = PklFiles(tmp_processed_dir, tmp_pkl_1, tmp_pkl_2, tmp_pkl_3, tmp_pkl_4)

    yield pkl_files

"""
 ==================================
  conftest.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import pytest
import pathlib
import dataclasses
import struct
from backend.data_collect_manager.models.handler import Handler
from backend.common.dao.handler_dao import HandlerDAO


@dataclasses.dataclass
class DatFiles:
    tmp_path: pathlib.Path
    tmp_dat_1: pathlib.Path
    tmp_dat_2: pathlib.Path
    tmp_dat_3: pathlib.Path
    tmp_dat_4: pathlib.Path
    tmp_dat_5: pathlib.Path


@pytest.fixture
def dat_files(tmp_path):
    """datファイルのfixture"""

    machine_id: str = "machine-01"

    tmp_dat_1: pathlib.Path = tmp_path / f"{machine_id}_AD-00_20201216-080058.620753.dat"
    tmp_dat_2: pathlib.Path = tmp_path / f"{machine_id}_AD-00_20201216-080059.620753.dat"
    tmp_dat_3: pathlib.Path = tmp_path / f"{machine_id}_AD-00_20201216-080100.620753.dat"
    tmp_dat_4: pathlib.Path = tmp_path / f"{machine_id}_AD-00_20201216-080101.620753.dat"
    tmp_dat_5: pathlib.Path = tmp_path / f"{machine_id}_AD-00_20201216-080102.620753.dat"

    binary = struct.pack("<ddddd", 10.0, 1.1, 2.2, 3.3, 4.4) + struct.pack("<ddddd", 9.0, 1.2, 2.3, 3.4, 4.5)

    tmp_dat_1.write_bytes(binary)
    tmp_dat_2.write_bytes(binary)
    tmp_dat_3.write_bytes(binary)
    tmp_dat_4.write_bytes(binary)
    tmp_dat_5.write_bytes(binary)

    dat_files = DatFiles(tmp_path, tmp_dat_1, tmp_dat_2, tmp_dat_3, tmp_dat_4, tmp_dat_5)

    yield dat_files


@pytest.fixture()
def handler():
    handler: Handler = Handler(handler_id="TEST-HANDLDER-001", sampling_ch_num=5, sampling_frequency=100000)

    yield handler

    del handler

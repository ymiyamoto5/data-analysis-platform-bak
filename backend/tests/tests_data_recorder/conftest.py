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
from backend.app.models.handler import Handler
from backend.app.crud.crud_machine import CRUDMachine


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


@pytest.fixture(scope="session", autouse=True)
def handler(session_mocker):
    """handlerオブジェクトのmock
    TODO: オブジェクト自体をmockして挿しこむのではなく、InmemoryDBまたはテンポラリのDBファイルを作成して挿しこむ。
    """

    handler: Handler = Handler(
        handler_id="test-handler", gateway_id="test-gw", sampling_frequency=100_000, sampling_ch_num=5
    )

    session_mocker.patch.object(CRUDMachine, "fetch_handler_from_machine_id", return_value=handler)

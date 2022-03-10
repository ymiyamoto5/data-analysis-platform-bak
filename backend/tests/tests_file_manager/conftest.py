"""
 ==================================
  conftest.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import dataclasses
import pathlib
import struct

import pytest


@dataclasses.dataclass
class DatFiles:
    tmp_path: pathlib.Path
    tmp_dat_1: pathlib.Path
    tmp_dat_2: pathlib.Path
    tmp_dat_3: pathlib.Path
    tmp_dat_4: pathlib.Path
    tmp_dat_5: pathlib.Path


@pytest.fixture
def dat_files_single_handler(tmp_path):
    """datファイルのfixture(単一ハンドラー)"""

    machine_id: str = "test-machine-01"
    gateway_id: str = "test-gateway-01"
    handler_id: str = "test-handler-01"

    tmp_dat_1: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-080058.620753_1.dat"
    tmp_dat_2: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-080059.620753_2.dat"
    tmp_dat_3: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-080100.620753_3.dat"
    tmp_dat_4: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-080101.620753_4.dat"
    tmp_dat_5: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handler_id}_20201216-080102.620753_5.dat"

    binary = struct.pack("<ddddd", 10.0, 1.1, 2.2, 3.3, 4.4) + struct.pack("<ddddd", 9.0, 1.2, 2.3, 3.4, 4.5)

    tmp_dat_1.write_bytes(binary)
    tmp_dat_2.write_bytes(binary)
    tmp_dat_3.write_bytes(binary)
    tmp_dat_4.write_bytes(binary)
    tmp_dat_5.write_bytes(binary)

    dat_files_single_handler = DatFiles(tmp_path, tmp_dat_1, tmp_dat_2, tmp_dat_3, tmp_dat_4, tmp_dat_5)

    yield dat_files_single_handler


@pytest.fixture
def dat_files_two_handler(tmp_path):
    """datファイルのfixture(2つのハンドラー, 1つ無関係のハンドラーを含む)"""

    machine_id: str = "test-machine-01"
    gateway_id: str = "test-gateway-01"
    handlers = ["test-handler-01-1", "test-handler-01-2"]

    tmp_dat_1: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handlers[0]}_20201216-080058.620753_1.dat"
    tmp_dat_2: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handlers[1]}_20201216-080059.620753_2.dat"
    tmp_dat_3: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handlers[0]}_20201216-080100.620753_1.dat"
    tmp_dat_4: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_{handlers[1]}_20201216-080101.620753_2.dat"
    tmp_dat_5: pathlib.Path = tmp_path / f"{machine_id}_{gateway_id}_other-handler_20201216-080101.620753_1.dat"

    binary_1 = struct.pack("<ddd", 10.0, 1.1, 2.2)
    binary_2 = struct.pack("<dd", 3.3, 4.4)
    binary_3 = struct.pack("<ddd", 9.0, 1.2, 2.3)
    binary_4 = struct.pack("<dd", 3.4, 4.5)
    binary_5 = struct.pack("<ddddd", 5.0, 1.0, 2.0, 3.0, 4.0)

    tmp_dat_1.write_bytes(binary_1)
    tmp_dat_2.write_bytes(binary_2)
    tmp_dat_3.write_bytes(binary_3)
    tmp_dat_4.write_bytes(binary_4)
    tmp_dat_5.write_bytes(binary_5)

    dat_files_two_handler = DatFiles(tmp_path, tmp_dat_1, tmp_dat_2, tmp_dat_3, tmp_dat_4, tmp_dat_5)

    yield dat_files_two_handler

"""
 ==================================
  test_data_recorder.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import os
from decimal import Decimal
from typing import Final

from backend.common import common
from backend.data_recorder.data_recorder import DataRecorder
from backend.file_manager.file_manager import FileManager

API_URL: Final[str] = os.getenv("API_URL", "http://localhost:8000/api/v1")


class TestReadBinaryFiles:
    def test_normal(self, dat_files, mocker, mocked_requests_get):
        """正常系：バイナリファイルが正常に読めること"""

        machine_id: str = "machine-01"
        mocker.patch("requests.get").return_value = mocked_requests_get

        dr = DataRecorder(machine_id=machine_id)

        file_infos = FileManager.create_files_info(
            dat_files.tmp_path._str, machine_id, "dat"
        )
        file = file_infos[0]

        actual = dr._read_binary_files(
            file=file, sequential_number=0, timestamp=Decimal(file.timestamp)
        )

        expected = (
            [
                {
                    "sequential_number": 0,
                    "timestamp": Decimal(file.timestamp),
                    "stroke_displacement": 10.0,
                    "load01": 1.1,
                    "load02": 2.2,
                    "load03": 3.3,
                    "load04": 4.4,
                },
                {
                    "sequential_number": 1,
                    "timestamp": Decimal(file.timestamp) + Decimal(0.00001),
                    "stroke_displacement": 9.0,
                    "load01": 1.2,
                    "load02": 2.3,
                    "load03": 3.4,
                    "load04": 4.5,
                },
            ],
            2,
            Decimal(file.timestamp) + Decimal(0.00001) + Decimal(0.00001),
        )

        assert actual == expected

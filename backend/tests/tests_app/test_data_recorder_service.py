# """
#  ==================================
#   test_data_recorder.py
#  ==================================

#   Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
#   CONFIDENTIAL
#   Author: UNIADEX, Ltd.

# """

# from decimal import Decimal

# from backend.app.services.data_recorder_service import DataRecorderService
# from backend.file_manager.file_manager import FileManager


# class TestReadBinaryFiles:
#     def test_normal(self, dat_files):
#         """正常系：バイナリファイルが正常に読めること"""

#         machine_id: str = "machine-01"

#         file_infos = FileManager.create_files_info(dat_files.tmp_path._str, machine_id, "dat")
#         file = file_infos[0]

#         actual = DataRecorderService.read_binary_files(
#             file=file,
#             sequential_number=0,
#             timestamp=Decimal(file.timestamp),
#             # latest_data_collect_history=
#         )
#         # latest_data_collect_history: DataCollectHistory,
#         # displacement_sensor_id: str,
#         # sensor_ids_other_than_displacement: List[str],
#         # sampling_interval: Decimal,
#         expected = (
#             [
#                 {
#                     "sequential_number": 0,
#                     "timestamp": Decimal(file.timestamp),
#                     "stroke_displacement": 10.0,
#                     "load01": 1.1,
#                     "load02": 2.2,
#                     "load03": 3.3,
#                     "load04": 4.4,
#                 },
#                 {
#                     "sequential_number": 1,
#                     "timestamp": Decimal(file.timestamp) + Decimal(0.00001),
#                     "stroke_displacement": 9.0,
#                     "load01": 1.2,
#                     "load02": 2.3,
#                     "load03": 3.4,
#                     "load04": 4.5,
#                 },
#             ],
#             2,
#             Decimal(file.timestamp) + Decimal(0.00001) + Decimal(0.00001),
#         )

#         assert actual == expected

# from ..data_reader import DataReader
# from helper_for_test import MockIndex
# import pytest
# import json


# @pytest.fixture()
# def mock_raw_index():
#     # setup
#     raw_index = MockIndex("test-raw-index")

#     raw_data = [
#         {"sequential_number": 1, "displacement": 1, "load01": 0.1, "load02": 0.2, "load03": 0.3, "load04": 0.4,},
#         {"sequential_number": 2, "load": 20},
#         {"sequential_number": 3, "load": 30},
#     ]
#     raw_index.bulk_insert(raw_data)

#     return raw_index


# def test_read_raw_data(mock_raw_index) -> None:
#     """ raw_data取得テスト """
#     reader = DataReader()
#     raw_data_generator = reader.read_raw_data(mock_raw_index.index)

#     raw_data_list = []
#     for d in raw_data_generator:
#         raw_data_list.append(d["_source"])

#     actual = json.dumps(raw_data_list)

#     expected_data = [
#         {"sequential_number": 1, "load": 10},
#         {"sequential_number": 2, "load": 20},
#         {"sequential_number": 3, "load": 30},
#     ]

#     expected = json.dumps(expected_data)

#     assert actual == expected

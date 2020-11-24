from data_importer import DataImporter
import helper_for_test
import json

def test_split_data_indivisible():
    """ """
    shots: list = helper_for_test.shots_data_create(7)

    data_importer = DataImporter()
    splitted_data = data_importer._split_data(shot_data=shots, num_of_split=2)
    target = json.dumps(splitted_data)

    expected_data = [
        [
            {
                "sequential_number": 0,
                "displacement": 0,
                "load01": 0,
                "load02": 0,
                "load03": 0,
                "load04": 0,
            },
            {
                "sequential_number": 1,
                "displacement": 1,
                "load01": 1,
                "load02": 2,
                "load03": 3,
                "load04": 4,
            },
            {
                "sequential_number": 2,
                "displacement": 2,
                "load01": 2,
                "load02": 4,
                "load03": 6,
                "load04": 8,
            },
        ],
        [
            {
                "sequential_number": 3,
                "displacement": 3,
                "load01": 3,
                "load02": 6,
                "load03": 9,
                "load04": 12,
            },
            {
                "sequential_number": 4,
                "displacement": 4,
                "load01": 4,
                "load02": 8,
                "load03": 12,
                "load04": 16,
            },
            {
                "sequential_number": 5,
                "displacement": 5,
                "load01": 5,
                "load02": 10,
                "load03": 15,
                "load04": 20,
            },
            {
                "sequential_number": 6,
                "displacement": 6,
                "load01": 6,
                "load02": 12,
                "load03": 18,
                "load04": 24,
            },
        ]
    ]

    expected = json.dumps(expected_data)

    assert target == expected


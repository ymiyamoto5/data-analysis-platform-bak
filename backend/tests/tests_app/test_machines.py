import pytest


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/machines"
        self.machine_id = "test-machine-01"

    def test_normal_db_select_all(self, client, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_normal_db_select_by_id(self, client, init):
        endpoint = f"{self.endpoint}/{self.machine_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200


class TestCreate:
    @pytest.fixture
    def init(self):
        # NOTE: 末尾スラッシュがないと307 redirectになってしまう。
        self.endpoint = "/api/v1/machines/"

    def test_normal(self, client, init):
        data = {
            "machine_id": "Test-Machine-001",
            "machine_name": "Test-Press",
            "machine_type_id": 1,
        }

        response = client.post(self.endpoint, json=data)

        assert response.status_code == 200

    test_invalid_machine_id_data = [
        (
            {
                "machine_id": "Machine_001",
                "machine_name": "Test-Press",
                "machine_type_id": 1,
            },
            422,
        ),
        (
            {
                "machine_id": "Machine@001",
                "machine_name": "Test-Press",
                "machine_type_id": 1,
            },
            422,
        ),
        (
            {
                "machine_id": "Machine001'",
                "machine_name": "Test-Press",
                "machine_type_id": 1,
            },
            422,
        ),
        (
            {"machine_id": "機器001", "machine_name": "Test-Press", "machine_type_id": 1},
            422,
        ),
        ({"machine_id": "", "machine_name": "Test-Press", "machine_type_id": 1}, 422),
    ]

    @pytest.mark.parametrize("data, expected_code", test_invalid_machine_id_data)
    def test_invalid_machine_id(self, client, init, data, expected_code):
        """利用不可文字が含まれるmachine_id"""

        response = client.post(self.endpoint, json=data)
        actual_code = response.status_code

        assert actual_code == expected_code


class TestUpdate:
    @pytest.fixture
    def init(self):
        self.machine_id = "test-machine-01"
        self.endpoint = "/api/v1/machines/" + self.machine_id

    def test_normal(self, client, init):
        data = {
            "machine_name": "test-update",
            "machine_type_id": 2,
        }
        response = client.put(self.endpoint, json=data)

        assert response.status_code == 200


# class TestDelete:
#     @pytest.fixture
#     def init(self):
#         # NOTE: 末尾スラッシュがないと307 redirectになってしまう。
#         self.machine_id = "test-machine-01"
#         self.endpoint = "/api/v1/machines/" + self.machine_id

#     def test_normal(self, client, init):

#         response = client.delete(self.endpoint)

#         assert response.status_code == 200

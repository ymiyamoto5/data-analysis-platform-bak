# import pytest
# from backend.app.crud.crud_machine_type import CRUDMachineType


# class TestRead:
#     @pytest.fixture
#     def init(self):
#         self.endpoint = "/api/v1/machine_types"

#     def test_normal_db_select_all(self, client, init):
#         response = client.get(self.endpoint)
#         actual_code = response.status_code

#         assert actual_code == 200

#     def test_db_select_all_failed(self, client, mocker, init):
#         mocker.patch.object(CRUDMachineType, "select_all", side_effect=Exception("some exception"))
#         response = client.get(self.endpoint)

#         assert response.status_code == 500

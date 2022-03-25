import pytest
from backend.app.crud.crud_handler import CRUDHandler


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/handlers"
        self.handler_id = "test-handler-01"
        self.gateway_id = "test-gw-01"

    def test_normal_db_select_all(self, client, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_all_failed(self, client, mocker, init):
        mocker.patch.object(CRUDHandler, "select_all", side_effect=Exception("some exception"))
        response = client.get(self.endpoint)

        assert response.status_code == 500

    def test_normal_db_select_by_id(self, client, init):
        endpoint = f"{self.endpoint}/{self.handler_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_by_id_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.handler_id}"
        mocker.patch.object(CRUDHandler, "select_by_id", side_effect=Exception("some exception"))
        response = client.get(endpoint)

        assert response.status_code == 500

    def test_normal_db_select_primary_by_gateway_id(self, client, init):
        endpoint = f"{self.endpoint}/primary/{self.gateway_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_primary_by_gateway_id_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/primary/{self.gateway_id}"
        mocker.patch.object(CRUDHandler, "select_primary_by_gateway_id", side_effect=Exception("some exception"))
        response = client.get(endpoint)

        assert response.status_code == 500


class TestCreate:
    @pytest.fixture
    def init(self):
        # NOTE: 末尾スラッシュがないと307 redirectになってしまう。
        self.endpoint = "/api/v1/handlers/"
        self.data = {
            "handler_id": "Test-Handler-001",
            "handler_type": "test-create",
            "adc_serial_num": "12345678",
            "sampling_frequency": 1,
            "filewrite_time": 1,
            "gateway_id": "test-gateway-01",
            "is_primary": True,
            "is_cut_out_target": True,
            "is_multi": True,
        }

    def test_normal(self, client, init):

        response = client.post(self.endpoint, json=self.data)

        assert response.status_code == 200

    def test_not_unique_handler_id(self, client, init):
        """重複しているhandler_id"""
        data = {
            "handler_id": "test-handler-01-1",
            "handler_type": "test-create",
            "adc_serial_num": "12345678",
            "sampling_frequency": 1,
            "filewrite_time": 1,
            "gateway_id": "test-gateway-01",
            "is_primary": True,
            "is_cut_out_target": True,
            "is_multi": True,
        }

        response = client.post(self.endpoint, json=data)

        assert response.status_code == 400

    # test_invalid_data = [
    #     # invalid handler_id
    #     (
    #         {
    #             "handler_id": "Handler_001",
    #             "handler_type": "test-create",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 1,
    #             "filewrite_time": 1,
    #             "gateway_id": "test-gateway-01",
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     (
    #         {
    #             "handler_id": "Handler@001",
    #             "handler_type": "test-create",
    #             "adc_serial_num": 1,
    #             "sampling_frequency": 1,
    #             "filewrite_time": 1,
    #             "gateway_id": "test-gateway-01",
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     (
    #         {
    #             "handler_id": "Handler001'",
    #             "handler_type": "test-create",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 1,
    #             "filewrite_time": 1,
    #             "gateway_id": "test-gateway-01",
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     (
    #         {
    #             "handler_id": "ハンドラー001",
    #             "handler_type": "test-create",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 1,
    #             "filewrite_time": 1,
    #             "gateway_id": "test-gateway-01",
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     (
    #         {
    #             "handler_id": "",
    #             "handler_type": "test-create",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 1,
    #             "filewrite_time": 1,
    #             "gateway_id": "test-gateway-01",
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     # invalid handler_type
    #     (
    #         {
    #             "handler_id": "Test-Handler-001",
    #             "handler_type": "test@create",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 1,
    #             "filewrite_time": 1,
    #             "gateway_id": "test-gateway-01",
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     (
    #         {
    #             "handler_id": "Test-Handler-001",
    #             "handler_type": "",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 1,
    #             "filewrite_time": 1,
    #             "gateway_id": "test-gateway-01",
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     # out of range sampling_frequency
    #     (
    #         {
    #             "handler_id": "Test-Handler-001",
    #             "handler_type": "test-create",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 0,
    #             "filewrite_time": 1,
    #             "gateway_id": "test-gateway-01",
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     (
    #         {
    #             "handler_id": "Test-Handler-001",
    #             "handler_type": "test-create",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 100_001,
    #             "filewrite_time": 1,
    #             "gateway_id": "test-gateway-01",
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     # out of range filewrite_time
    #     (
    #         {
    #             "handler_id": "Test-Handler-001",
    #             "handler_type": "test-create",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 1,
    #             "filewrite_time": 0,
    #             "gateway_id": "test-gateway-01",
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     (
    #         {
    #             "handler_id": "Test-Handler-001",
    #             "handler_type": "test-create",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 1,
    #             "filewrite_time": 361,
    #             "gateway_id": "test-gateway-01",
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    # ]

    # @pytest.mark.parametrize("data, expected_code", test_invalid_data)
    # def test_invalid_someting_data(self, client, init, data, expected_code):
    #     """無効なデータが含まれる"""

    #     response = client.post(self.endpoint, json=data)
    #     actual_code = response.status_code

    #     assert actual_code == expected_code

    def test_insert_failed(self, client, mocker, init):
        mocker.patch.object(CRUDHandler, "insert", side_effect=Exception("some exception"))
        response = client.post(self.endpoint, json=self.data)

        assert response.status_code == 500


class TestUpdate:
    @pytest.fixture
    def init(self):
        self.handler_id = "test-handler-01-1"
        self.endpoint = "/api/v1/handlers"
        self.data = {
            "handler_type": "test-update",
            "adc_serial_num": "12345678",
            "sampling_frequency": 1,
            "filewrite_time": 1,
            "is_primary": True,
            "is_cut_out_target": True,
            "is_multi": True,
        }

    def test_normal(self, client, init):
        endpoint = f"{self.endpoint}/{self.handler_id}"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 200

    def test_not_exist_handler_id(self, client, init):
        """存在しないhandler_id"""
        endpoint = f"{self.endpoint}/not-exist-handler-id"
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 404

    # test_invalid_data = [
    #     # invalid handler_type
    #     (
    #         {
    #             "handler_type": "test@update",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 1,
    #             "filewrite_time": 1,
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     (
    #         {
    #             "handler_type": "",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 1,
    #             "filewrite_time": 1,
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     # out of range sampling_frequency
    #     (
    #         {
    #             "handler_type": "test-update",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 0,
    #             "filewrite_time": 1,
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     (
    #         {
    #             "handler_type": "test-update",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 100_001,
    #             "filewrite_time": 1,
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     # out of range filewrite_time
    #     (
    #         {
    #             "handler_type": "test-update",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 1,
    #             "filewrite_time": 0,
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    #     (
    #         {
    #             "handler_type": "test-update",
    #             "adc_serial_num": "12345678",
    #             "sampling_frequency": 1,
    #             "filewrite_time": 361,
    #             "is_primary": True,
    #             "is_cut_out_target": True,
    #         },
    #         422,
    #     ),
    # ]

    # @pytest.mark.parametrize("data, expected_code", test_invalid_data)
    # def test_invalid_someting_data(self, client, init, data, expected_code):
    #     """無効なデータが含まれる"""
    #     endpoint = f"{self.endpoint}/{self.handler_id}"
    #     response = client.put(endpoint, json=data)
    #     actual_code = response.status_code

    #     assert actual_code == expected_code

    def test_update_failed(self, client, mocker, init):
        endpoint = f"{self.endpoint}/{self.handler_id}"
        mocker.patch.object(CRUDHandler, "update", side_effect=Exception("some exception"))
        response = client.put(endpoint, json=self.data)

        assert response.status_code == 500


class TestDelete:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/handlers"

    def test_normal(self, client, init):
        endpoint = f"{self.endpoint}/test-handler-no-child"
        response = client.delete(endpoint)

        assert response.status_code == 200

    def test_not_exist_handler_id(self, client, init):
        """存在しないhandler_id"""
        endpoint = f"{self.endpoint}/not-exist-handler-id"
        response = client.delete(endpoint)

        assert response.status_code == 404

    def test_foreign_key_error(self, client, init):
        """子が存在するhandler_id"""
        endpoint = f"{self.endpoint}/test-handler-01-1"
        response = client.delete(endpoint)

        assert response.status_code == 500

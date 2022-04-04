import pytest
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.services.data_collect_history_service import DataCollectHistoryService


class TestRead:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/data_collect_histories"

    machine_id_data = ["test-machine-01", "test-machine-02"]

    def test_normal_db_select_all(self, client, init):
        response = client.get(self.endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    def test_db_select_all_failed(self, client, mocker, init):
        mocker.patch.object(CRUDDataCollectHistory, "select_all", side_effect=Exception("some exception"))
        response = client.get(self.endpoint)

        assert response.status_code == 500

    @pytest.mark.parametrize("machine_id", machine_id_data)
    def test_normal_db_select_by_machine_id(self, client, init, machine_id):
        endpoint = f"{self.endpoint}/{machine_id}"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    @pytest.mark.parametrize("machine_id", machine_id_data)
    def test_db_select_by_machine_id_failed(self, client, mocker, init, machine_id):
        endpoint = f"{self.endpoint}/{machine_id}"
        mocker.patch.object(CRUDDataCollectHistory, "select_by_machine_id", side_effect=Exception("some exception"))
        response = client.get(endpoint)

        assert response.status_code == 500

    @pytest.mark.parametrize("machine_id", machine_id_data)
    def test_normal_db_select_latest_by_machine_id(self, client, init, machine_id):
        endpoint = f"{self.endpoint}/{machine_id}/latest"
        response = client.get(endpoint)
        actual_code = response.status_code

        assert actual_code == 200

    @pytest.mark.parametrize("machine_id", machine_id_data)
    def test_db_select_latest_by_machine_id_failed(self, client, mocker, init, machine_id):
        endpoint = f"{self.endpoint}/{machine_id}/latest"
        mocker.patch.object(CRUDDataCollectHistory, "select_latest_by_machine_id", side_effect=Exception("some exception"))
        response = client.get(endpoint)

        assert response.status_code == 500


class TestUpdate:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/data_collect_histories"

    test_update_data = [
        # 複数ハンドラー
        (
            1,
            {
                "data_collect_history_gateways": [
                    {
                        "data_collect_history_id": 1,
                        "gateway_id": "test-gateway-01",
                        "log_level": 5,
                        "data_collect_history_handlers": [
                            {
                                "data_collect_history_id": 1,
                                "is_cut_out_target": True,
                                "handler_id": "test-handler-01-1",
                                "handler_type": "USB-1608HS",
                                "adc_serial_num": "01ED23FA",
                                "sampling_frequency": 1000,
                                "sampling_ch_num": 3,
                                "filewrite_time": 1,
                                "gateway_id": "test-gateway-01",
                                "data_collect_history_sensors": [
                                    {
                                        "data_collect_history_id": 1,
                                        "sensor_id": "stroke_displacement",
                                        "handler_id": "test-handler-01-1",
                                        "gateway_id": "test-gateway-01",
                                        "sensor_name": "stroke_displacement",
                                        "sensor_type_id": "stroke_displacement",
                                        "slope": 0,
                                        "intercept": 0,
                                        "start_point_dsl": "",
                                        "max_point_dsl": "",
                                        "break_point_dsl": "",
                                    },
                                    {
                                        "data_collect_history_id": 1,
                                        "sensor_id": "load01",
                                        "handler_id": "test-handler-01-1",
                                        "gateway_id": "test-gateway-01",
                                        "sensor_name": "laod01",
                                        "sensor_type_id": "load",
                                        "slope": 0,
                                        "intercept": 0,
                                        "start_point_dsl": r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                        "max_point_dsl": r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                        "break_point_dsl": r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                                    },
                                    {
                                        "data_collect_history_id": 1,
                                        "sensor_id": "load02",
                                        "handler_id": "test-handler-01-1",
                                        "gateway_id": "test-gateway-01",
                                        "sensor_name": "laod02",
                                        "sensor_type_id": "load",
                                        "slope": 0,
                                        "intercept": 0,
                                        "start_point_dsl": r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                        "max_point_dsl": r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                        "break_point_dsl": r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                                    },
                                ],
                            },
                            {
                                "data_collect_history_id": 1,
                                "is_cut_out_target": True,
                                "handler_id": "test-handler-01-2",
                                "handler_type": "USB-1608HS",
                                "adc_serial_num": "01ED23FB",
                                "sampling_frequency": 1000,
                                "sampling_ch_num": 3,
                                "filewrite_time": 1,
                                "gateway_id": "test-gateway-01",
                                "data_collect_history_sensors": [
                                    {
                                        "data_collect_history_id": 1,
                                        "sensor_id": "load03",
                                        "handler_id": "test-handler-01-2",
                                        "gateway_id": "test-gateway-01",
                                        "sensor_name": "laod03",
                                        "sensor_type_id": "load",
                                        "slope": 0,
                                        "intercept": 0,
                                        "start_point_dsl": r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                        "max_point_dsl": r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                        "break_point_dsl": r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                                    },
                                    {
                                        "data_collect_history_id": 1,
                                        "sensor_id": "load04",
                                        "handler_id": "test-handler-01-2",
                                        "gateway_id": "test-gateway-01",
                                        "sensor_name": "laod04",
                                        "sensor_type_id": "load",
                                        "slope": 0,
                                        "intercept": 0,
                                        "start_point_dsl": r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                        "max_point_dsl": r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                        "break_point_dsl": r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                                    },
                                    {
                                        "data_collect_history_id": 1,
                                        "sensor_id": "dummy01",
                                        "handler_id": "test-handler-01-2",
                                        "gateway_id": "test-gateway-01",
                                        "sensor_name": "dummy01",
                                        "sensor_type_id": "dummy",
                                        "slope": 0,
                                        "intercept": 0,
                                        "start_point_dsl": "",
                                        "max_point_dsl": "",
                                        "break_point_dsl": "",
                                    },
                                ],
                            },
                        ],
                    }
                ]
            },
        ),
        # 単一ハンドラー
        (
            2,
            {
                "data_collect_history_gateways": [
                    {
                        "data_collect_history_id": 2,
                        "gateway_id": "test-gateway-02",
                        "log_level": 5,
                        "data_collect_history_handlers": [
                            {
                                "data_collect_history_id": 2,
                                "is_cut_out_target": True,
                                "handler_id": "test-handler-02",
                                "handler_type": "USB-1608HS",
                                "adc_serial_num": "01ED23FA",
                                "sampling_frequency": 1000,
                                "sampling_ch_num": 5,
                                "filewrite_time": 1,
                                "gateway_id": "test-gateway-02",
                                "data_collect_history_sensors": [
                                    {
                                        "data_collect_history_id": 2,
                                        "sensor_id": "stroke_displacement",
                                        "handler_id": "test-handler-02",
                                        "gateway_id": "test-gateway-02",
                                        "sensor_name": "stroke_displacement",
                                        "sensor_type_id": "stroke_displacement",
                                        "slope": 0,
                                        "intercept": 0,
                                        "start_point_dsl": "",
                                        "max_point_dsl": "",
                                        "break_point_dsl": "",
                                    },
                                    {
                                        "data_collect_history_id": 2,
                                        "sensor_id": "load01",
                                        "handler_id": "test-handler-02",
                                        "gateway_id": "test-gateway-02",
                                        "sensor_name": "laod01",
                                        "sensor_type_id": "load",
                                        "slope": 0,
                                        "intercept": 0,
                                        "start_point_dsl": r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                        "max_point_dsl": r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                        "break_point_dsl": r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                                    },
                                    {
                                        "data_collect_history_id": 2,
                                        "sensor_id": "load02",
                                        "handler_id": "test-handler-02",
                                        "gateway_id": "test-gateway-02",
                                        "sensor_name": "laod02",
                                        "sensor_type_id": "load",
                                        "slope": 0,
                                        "intercept": 0,
                                        "start_point_dsl": r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                        "max_point_dsl": r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                        "break_point_dsl": r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                                    },
                                    {
                                        "data_collect_history_id": 2,
                                        "sensor_id": "load03",
                                        "handler_id": "test-handler-02",
                                        "gateway_id": "test-gateway-02",
                                        "sensor_name": "laod03",
                                        "sensor_type_id": "load",
                                        "slope": 0,
                                        "intercept": 0,
                                        "start_point_dsl": r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                        "max_point_dsl": r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                        "break_point_dsl": r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                                    },
                                    {
                                        "data_collect_history_id": 2,
                                        "sensor_id": "load04",
                                        "handler_id": "test-handler-02",
                                        "gateway_id": "test-gateway-02",
                                        "sensor_name": "laod04",
                                        "sensor_type_id": "load",
                                        "slope": 0,
                                        "intercept": 0,
                                        "start_point_dsl": r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                        "max_point_dsl": r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                        "break_point_dsl": r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                                    },
                                ],
                            }
                        ],
                    }
                ]
            },
        ),
    ]

    @pytest.mark.parametrize("data_collect_history_id, data", test_update_data)
    def test_normal(self, client, init, data_collect_history_id, data):
        endpoint = f"{self.endpoint}/{data_collect_history_id}"
        response = client.put(endpoint, json=data)

        assert response.status_code == 200

    @pytest.mark.parametrize("data_collect_history_id, data", test_update_data)
    def test_not_exist_data_collect_history_id(self, client, init, data_collect_history_id, data):
        """存在しないdata_collect_history_id"""
        endpoint = f"{self.endpoint}/100"
        response = client.put(endpoint, json=data)

        assert response.status_code == 404

    @pytest.mark.parametrize("data_collect_history_id, data", test_update_data)
    def test_update_failed(self, client, mocker, init, data_collect_history_id, data):
        endpoint = f"{self.endpoint}/{data_collect_history_id}"
        mocker.patch.object(CRUDDataCollectHistory, "update", side_effect=Exception("some exception"))
        response = client.put(endpoint, json=data)

        assert response.status_code == 500


class TestDelete:
    @pytest.fixture
    def init(self):
        self.endpoint = "/api/v1/data_collect_histories"

    data_collect_history_id_data = [1, 2]

    @pytest.mark.parametrize("data_collect_history_id", data_collect_history_id_data)
    def test_normal(self, client, mocker, init, data_collect_history_id):
        """子が存在するdata_collect_history_id"""
        mocker.patch.object(DataCollectHistoryService, "delete_elastic_index")

        endpoint = f"{self.endpoint}/{data_collect_history_id}"
        response = client.delete(endpoint)

        assert response.status_code == 200

    def test_not_exist_data_collect_history_id(self, client, init):
        """存在しないdata_collect_history_id"""
        endpoint = f"{self.endpoint}/100"
        response = client.delete(endpoint)

        assert response.status_code == 404

    @pytest.mark.parametrize("data_collect_history_id", data_collect_history_id_data)
    def test_delete_failed(self, client, mocker, init, data_collect_history_id):
        endpoint = f"{self.endpoint}/{data_collect_history_id}"
        mocker.patch.object(CRUDDataCollectHistory, "delete", side_effect=Exception("some exception"))
        response = client.delete(endpoint)

        assert response.status_code == 500

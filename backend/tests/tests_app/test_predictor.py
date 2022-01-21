import pytest
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.gateway import Gateway
from backend.app.models.handler import Handler
from backend.app.models.machine import Machine
from backend.app.models.sensor import Sensor
from backend.app.worker.tasks import predictor
from backend.common import common
from backend.elastic_manager.elastic_manager import ElasticManager


class TestPredictorTask:
    @pytest.fixture
    def init(self) -> None:
        self.machine_id = "machine-01"

    @pytest.mark.skip(reason="デバッグ用にpredictedフィールド書き換え")
    def test_change_label(self, init):
        """
        shots-machine-01-20210709190000-meta の各ドキュメントのpredictedフィールドを書き換える。
        1-990はTrue, 991-1000はFalseとする。
        通常はスキップ
        """

        target = "20210709190000"
        meta_index = f"shots-{self.machine_id}-{target}-meta"

        query = {"sort": {"shot_number": {"order": "asc"}}}
        shots_meta = ElasticManager.get_docs_with_id(index=meta_index, query=query)

        for target_shot in range(1, 991):
            shot_ids = [meta["id"] for meta in shots_meta if meta["shot_number"] == target_shot]
            if shot_ids:
                ElasticManager.update_doc(meta_index, shot_ids[0], {"predicted": True})

        for target_shot in range(991, 1001):
            shot_ids = [meta["id"] for meta in shots_meta if meta["shot_number"] == target_shot]
            if shot_ids:
                ElasticManager.update_doc(meta_index, shot_ids[0], {"predicted": False})

    @pytest.mark.skip(reason="ジョブ実行のみ（デバッグ用）")
    def test_exec(self, init, mocker):
        """ジョブ実行のみ（デバッグ用）
        通常はスキップ
        """

        machine: Machine = Machine(
            machine_id=self.machine_id,
            collect_status=common.COLLECT_STATUS.START.value,
            auto_predict=True,
            # NOTE: 環境に応じて適宜変更すること
            predict_model="20220111_logreg",
            model_version=1,
            gateways=[
                Gateway(
                    gateway_id="gw-01",
                    sequence_number=1,
                    gateway_result=0,
                    status=common.STATUS.RUNNING.value,
                    log_level=5,
                    handlers=[
                        Handler(
                            handler_id="handler-01",
                            handler_type="USB_1608HS",
                            adc_serial_num="01ED23FA",
                            sampling_frequency=100000,
                            sampling_ch_num=5,
                            filewrite_time=10,
                            sensors=[
                                Sensor(
                                    machine_id="machine-01",
                                    sensor_id="stroke_displacement",
                                    sensor_name="stroke_displacement",
                                    sensor_type_id="stroke_displacement",
                                    slope=1.0,
                                    intercept=0.0,
                                ),
                                Sensor(
                                    machine_id="machine-01",
                                    sensor_id="load01",
                                    sensor_name="load01",
                                    sensor_type_id="load",
                                    slope=1.0,
                                    intercept=0.0,
                                    start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                    max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                    break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                                ),
                                Sensor(
                                    machine_id="machine-01",
                                    sensor_id="load02",
                                    sensor_name="load02",
                                    sensor_type_id="load",
                                    slope=1.0,
                                    intercept=0.0,
                                    start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                    max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                    break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                                ),
                                Sensor(
                                    machine_id="machine-01",
                                    sensor_id="load03",
                                    sensor_name="load03",
                                    sensor_type_id="load",
                                    slope=1.0,
                                    intercept=0.0,
                                    start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                    max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                    break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                                ),
                                Sensor(
                                    machine_id="machine-01",
                                    sensor_id="load04",
                                    sensor_name="load04",
                                    sensor_type_id="load",
                                    slope=1.0,
                                    intercept=0.0,
                                    start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                                    max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                                    break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                                ),
                            ],
                        )
                    ],
                )
            ],
            sensors=[
                Sensor(
                    machine_id="machine-01",
                    sensor_id="stroke_displacement",
                    sensor_name="stroke_displacement",
                    sensor_type_id="stroke_displacement",
                    slope=1.0,
                    intercept=0.0,
                ),
                Sensor(
                    machine_id="machine-01",
                    sensor_id="load01",
                    sensor_name="load01",
                    sensor_type_id="load",
                    slope=1.0,
                    intercept=0.0,
                    start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                    max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                    break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                ),
                Sensor(
                    machine_id="machine-01",
                    sensor_id="load02",
                    sensor_name="load02",
                    sensor_type_id="load",
                    slope=1.0,
                    intercept=0.0,
                    start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                    max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                    break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                ),
                Sensor(
                    machine_id="machine-01",
                    sensor_id="load03",
                    sensor_name="load03",
                    sensor_type_id="load",
                    slope=1.0,
                    intercept=0.0,
                    start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                    max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                    break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                ),
                Sensor(
                    machine_id="machine-01",
                    sensor_id="load04",
                    sensor_name="load04",
                    sensor_type_id="load",
                    slope=1.0,
                    intercept=0.0,
                    start_point_dsl=r"ROLLING_WINDOW = 9;HORIZONTAL_LIMIT = [1104.874008786576, 1172.3325853073954];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(ACC);",
                    max_point_dsl=r"ROLLING_WINDOW = 19;HORIZONTAL_LIMIT = [1264.4156514760432, 1465.621588396266];VERTICAL_LIMIT = [None, None];TARGET = IDXMIN(DST);",
                    break_point_dsl=r"ROLLING_WINDOW = 1;HORIZONTAL_LIMIT = [IDXMAX(VCT)-20, IDXMAX(VCT)];VERTICAL_LIMIT = [None, None];TARGET = IDXMAX(ACC);",
                ),
            ],
        )

        mocker.patch.object(
            CRUDMachine,
            "select_by_id",
            return_value=machine,
        )

        mocker.patch.object(
            CRUDDataCollectHistory,
            "select_latest_by_machine_id",
            return_value=DataCollectHistory(
                machine_id=self.machine_id,
                processed_dir_path="/mnt/datadrive/data/machine-01-20210709190000",
            ),
        )

        predictor.predictor_task(self.machine_id)

from typing import Callable
from backend.data_collect_manager.models.sensor import Sensor


class DataConverter:
    @classmethod
    def get_physical_conversion_formula(cls, sensor: Sensor) -> Callable[[float], float]:
        """センサー種別に応じた物理変換式を返却する"""

        if sensor.SensorType.sensor_type_id == "load":
            # TODO: VrをDBから取得
            Vr = 2.5
            return lambda v: 2.5 / Vr * v

        elif sensor.SensorType.sensor_type_id == "bolt":
            # TODO: base_pressure, v1, v2をDBから取得
            # return lambda x: sensor.base_pressure * (x - sensor.v1) / (sensor.v2 - sensor.v1)
            return lambda x: x

        else:
            return lambda x: x

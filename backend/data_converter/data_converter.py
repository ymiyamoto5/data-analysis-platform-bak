from typing import Callable
from backend.data_collect_manager.models.sensor import Sensor


class DataConverter:
    @classmethod
    def get_physical_conversion_formula(cls, sensor: Sensor) -> Callable[[float], float]:
        """センサー種別に応じた物理変換式を返却する"""

        if sensor.SensorType.sensor_type_id == "load":
            # return lambda x: sensor.base_pressure * (x - sensor.v1) / (sensor.v2 - sensor.v1)
            return lambda x: x + 1.0

        else:
            return lambda x: x

    # @classmethod
    # def get_physical_conversion_formula_for_cut_out(cls, sensor: Sensor) -> Callable[[float], float]:
    #     """切り出し対象（変位など）の物理変換式を返却する"""

    #     if sensor.SensorType.sensor_type_id == "displacement":
    #         # return lambda x: sensor.base_pressure * (x - sensor.v1) / (sensor.v2 - sensor.v1)
    #         return lambda x: x

    #     else:
    #         return None

from typing import Callable
from backend.data_collect_manager.models.sensor import Sensor


class DataConverter:
    @classmethod
    def get_physical_conversion_formula(cls, sensor: Sensor) -> Callable[[float], float]:
        """センサー種別に応じた物理変換式を返却する"""

        if sensor.SensorType.sensor_type_id == "load":
            base_volt: float = sensor.Sensor.base_volt
            base_load: float = sensor.Sensor.base_load

            return lambda v: base_load / base_volt * v

        elif sensor.SensorType.sensor_type_id == "bolt":
            base_volt = sensor.Sensor.base_volt
            base_load = sensor.Sensor.base_load
            initial_volt: float = sensor.Sensor.initial_volt

            return lambda v: base_load * (v - initial_volt) / (base_volt - initial_volt)

        elif sensor.SensorType.sensor_type_id == "displacement":
            return lambda v: 70.0 - (v - 2.0) * 70.0 / 8.0

        elif sensor.SensorType.sensor_type_id == "pulse":
            return lambda v: v

        else:
            return lambda v: v

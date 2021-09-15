from backend.app.db.session import Base
from sqlalchemy import Column, ForeignKey, Float, String
from sqlalchemy.orm import relationship


class Sensor(Base):
    __tablename__ = "sensors"

    # NOTE: 冗長なリレーションシップとなるが、複合主キー（機器ごとに一意のセンサー）とするため必要。
    machine_id = Column(String(255), ForeignKey("machines.machine_id"), primary_key=True, index=True)
    sensor_id = Column(String(255), primary_key=True, index=True)
    sensor_name = Column(String(255), nullable=False)
    sensor_type_id = Column(String(255), ForeignKey("sensor_types.sensor_type_id"), nullable=False)
    base_volt = Column(Float)
    base_load = Column(Float)
    initial_volt = Column(Float)
    handler_id = Column(String(255), ForeignKey("handlers.handler_id"), nullable=False)

    # NOTE: SensorとMachineはMany to One
    # machine = relationship("Machine", back_populates="machines")
    # NOTE: SensorとHandlerはMany to One
    handler = relationship("Handler", back_populates="sensors")
    # NOTE: SensorとSensorTypeはMany to One
    sensor_type = relationship("SensorType", back_populates="sensors")

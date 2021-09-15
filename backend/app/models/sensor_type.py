from backend.app.db.session import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class SensorType(Base):
    __tablename__ = "sensor_types"

    sensor_type_id = Column(String(255), primary_key=True)
    sensor_type_name = Column(String(255), unique=True, nullable=False)

    sensors = relationship("Sensor", back_populates="sensor_type")

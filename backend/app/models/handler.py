from backend.app.db.session import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Handler(Base):
    __tablename__ = "handlers"

    handler_id = Column(String(255), primary_key=True, index=True)
    handler_type = Column(String(255), nullable=False)
    adc_serial_num = Column(String(255), nullable=False)
    sampling_frequency = Column(Integer, nullable=False)
    sampling_ch_num = Column(Integer, nullable=False)
    filewrite_time = Column(Integer, nullable=False)
    gateway_id = Column(Integer, ForeignKey("gateways.gateway_id"), nullable=False)

    gateway = relationship("Gateway", back_populates="handlers")
    sensors = relationship("Sensor", back_populates="handler")

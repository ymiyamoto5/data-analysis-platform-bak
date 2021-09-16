from backend.app.db.session import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Handler(Base):
    __tablename__ = "handlers"

    handler_id = Column(String(255), primary_key=True, index=True)
    handler_type = Column(String(255))
    adc_serial_num = Column(String(255))
    sampling_frequency = Column(Integer)
    sampling_ch_num = Column(Integer)
    filewrite_time = Column(Integer)
    gateway_id = Column(Integer, ForeignKey("gateways.gateway_id"), nullable=False)

    gateway = relationship("Gateway", back_populates="handlers")
    sensors = relationship("Sensor", back_populates="handler")

from backend.app.db.session import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class DataCollectHistoryHandler(Base):
    __tablename__ = "data_collect_history_handlers"

    data_collect_history_id = Column(Integer, ForeignKey("data_collect_histories.id"), primary_key=True, index=True)
    gateway_id = Column(Integer, ForeignKey("data_collect_history_gateways.gateway_id"), primary_key=True, index=True)
    handler_id = Column(String(255), primary_key=True, index=True)
    handler_type = Column(String(255), nullable=False)
    adc_serial_num = Column(String(255), nullable=False)
    sampling_frequency = Column(Integer, nullable=False)
    sampling_ch_num = Column(Integer, nullable=False)
    filewrite_time = Column(Integer, nullable=False)
    is_primary = Column(Boolean, nullable=False, default=False)

    # Many To One
    data_collect_history = relationship("DataCollectHistory", back_populates="data_collect_history_handlers")
    data_collect_history_gateway = relationship("DataCollectHistoryGateway", back_populates="data_collect_history_handlers")

    # One to Many
    data_collect_history_sensors = relationship(
        "DataCollectHistorySensor", back_populates="data_collect_history_handler", cascade="all, delete"
    )

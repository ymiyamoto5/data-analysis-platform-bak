from backend.app.db.session import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


class DataCollectHistorySensor(Base):
    __tablename__ = "data_collect_history_sensors"

    data_collect_history_id = Column(Integer, ForeignKey("data_collect_histories.id"), primary_key=True, index=True)
    handler_id = Column(String(255), ForeignKey("data_collect_history_handlers.handler_id"), primary_key=True, index=True)
    sensor_id = Column(String(255), primary_key=True, index=True)
    sensor_name = Column(String(255), nullable=False)
    sensor_type_id = Column(String(255), nullable=False)
    slope = Column(Float, nullable=False)
    intercept = Column(Float, nullable=False)
    start_point_dsl = Column(Text)
    max_point_dsl = Column(Text)
    break_point_dsl = Column(Text)

    # Many To One
    data_collect_history = relationship("DataCollectHistory", back_populates="data_collect_history_sensors")
    data_collect_history_handler = relationship("DataCollectHistoryHandler", back_populates="data_collect_history_sensors")

from backend.app.db.session import Base
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
from sqlalchemy import Column, Float, ForeignKeyConstraint, Integer, String, Text
from sqlalchemy.orm import relationship


class DataCollectHistorySensor(Base):
    __tablename__ = "data_collect_history_sensors"

    data_collect_history_id = Column(Integer, primary_key=True, index=True)
    gateway_id = Column(String(255), primary_key=True, index=True)
    handler_id = Column(String(255), primary_key=True, index=True)
    sensor_id = Column(String(255), primary_key=True, index=True)
    sensor_name = Column(String(255), nullable=False)
    sensor_type_id = Column(String(255), nullable=False)
    slope = Column(Float, nullable=False)
    intercept = Column(Float, nullable=False)
    start_point_dsl = Column(Text)
    max_point_dsl = Column(Text)
    break_point_dsl = Column(Text)

    __table_args__ = (
        ForeignKeyConstraint(
            [data_collect_history_id, gateway_id, handler_id],
            [DataCollectHistoryHandler.data_collect_history_id, DataCollectHistoryHandler.gateway_id, DataCollectHistoryHandler.handler_id],
        ),
        {},
    )  # type: ignore

    # Many To One
    data_collect_history_handler = relationship("DataCollectHistoryHandler", back_populates="data_collect_history_sensors")

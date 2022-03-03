from backend.app.db.session import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class DataCollectHistory(Base):
    __tablename__ = "data_collect_histories"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    machine_id = Column(String(255), ForeignKey("machines.machine_id"), nullable=False)
    machine_name = Column(String(255), nullable=False)
    machine_type_id = Column(Integer, nullable=False)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)
    processed_dir_path = Column(String(255), nullable=False)

    # Many To One
    machine = relationship("Machine", back_populates="data_collect_histories")
    # One to Many
    data_collect_history_gateways = relationship("DataCollectHistoryGateway", back_populates="data_collect_history", cascade="all, delete")
    data_collect_history_handlers = relationship("DataCollectHistoryHandler", back_populates="data_collect_history", cascade="all, delete")
    data_collect_history_sensors = relationship("DataCollectHistorySensor", back_populates="data_collect_history", cascade="all, delete")
    # One to Many
    data_collect_history_events = relationship(
        "DataCollectHistoryEvent",
        back_populates="data_collect_history",
        cascade="all, delete",
        order_by="DataCollectHistoryEvent.occurred_at",
    )
    # One to Many
    celery_tasks = relationship("CeleryTask", back_populates="data_collect_history", cascade="all, delete")

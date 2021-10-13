from backend.app.db.session import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class DataCollectHistoryEvent(Base):
    __tablename__ = "data_collect_history_events"

    data_collect_history_id = Column(Integer, ForeignKey("data_collect_histories.id"), primary_key=True, index=True)
    event_id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(255), nullable=False)
    occurred_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)

    # Many To One
    data_collect_history = relationship("DataCollectHistory", back_populates="data_collect_history_events")

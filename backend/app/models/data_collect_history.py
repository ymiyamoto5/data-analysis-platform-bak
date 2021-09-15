from backend.app.db.session import Base
from sqlalchemy import Column, ForeignKey, DateTime, Integer, String
from sqlalchemy.orm import relationship


class DataCollectHistory(Base):
    __tablename__ = "data_collect_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(255), ForeignKey("machines.machine_id"), nullable=False)
    machine_name = Column(String(255), nullable=False)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)

    # Many To One
    machine = relationship("Machine", back_populates="data_collect_history")

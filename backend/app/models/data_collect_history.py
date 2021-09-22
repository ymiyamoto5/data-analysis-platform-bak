from backend.app.db.session import Base
from sqlalchemy import Column, ForeignKey, DateTime, Integer, String
from sqlalchemy.orm import relationship


class DataCollectHistory(Base):
    __tablename__ = "data_collect_histories"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    machine_id = Column(String(255), ForeignKey("machines.machine_id"), nullable=False)
    machine_name = Column(String(255), nullable=False)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)
    sampling_frequency = Column(Integer, nullable=False)
    sampling_ch_num = Column(Integer, nullable=False)

    # Many To One
    machine = relationship("Machine", back_populates="data_collect_histories")
    # One to Many
    data_collect_history_details = relationship(
        "DataCollectHistoryDetail", back_populates="data_collect_history", cascade="all, delete"
    )

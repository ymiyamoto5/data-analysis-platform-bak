from backend.app.db.session import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class DataCollectHistoryDetail(Base):
    __tablename__ = "data_collect_history_details"

    data_collect_history_id = Column(Integer, ForeignKey("data_collect_histories.id"), primary_key=True, index=True)
    sensor_id = Column(String(255), primary_key=True, index=True)
    sensor_name = Column(String(255), nullable=False)
    sensor_type_id = Column(String(255), nullable=False)
    base_volt = Column(Float)
    base_load = Column(Float)
    initial_volt = Column(Float)

    # Many To One
    data_collect_history = relationship("DataCollectHistory", back_populates="data_collect_history_details")

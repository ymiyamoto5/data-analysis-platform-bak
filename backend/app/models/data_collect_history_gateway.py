from backend.app.db.session import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class DataCollectHistoryGateway(Base):
    __tablename__ = "data_collect_history_gateways"

    data_collect_history_id = Column(Integer, ForeignKey("data_collect_histories.id"), primary_key=True, index=True)
    gateway_id = Column(String(255), primary_key=True, index=True)
    log_level = Column(Integer)

    # Many To One
    data_collect_history = relationship("DataCollectHistory", back_populates="data_collect_history_gateways")

    # One to Many
    data_collect_history_handlers = relationship(
        "DataCollectHistoryHandler", back_populates="data_collect_history_gateway", cascade="all, delete"
    )

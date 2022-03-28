from backend.app.db.session import Base
from sqlalchemy import Column, DateTime, Integer, String


class GatewayEvent(Base):
    __tablename__ = "gateway_events"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    severity = Column(String(255), nullable=False)
    gateway_id = Column(String(255), nullable=False)
    message = Column(String(255), nullable=False)

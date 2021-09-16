from sqlalchemy import Column, ForeignKey, Integer, String
from backend.app.db.session import Base
from sqlalchemy.orm import relationship


class Gateway(Base):
    __tablename__ = "gateways"

    gateway_id = Column(String(255), primary_key=True, index=True)
    sequence_number = Column(Integer)
    gateway_result = Column(Integer)
    status = Column(String(255))
    log_level = Column(Integer)
    machine_id = Column(Integer, ForeignKey("machines.machine_id"), nullable=False)

    machine = relationship("Machine", back_populates="gateways")
    handlers = relationship("Handler", back_populates="gateway")

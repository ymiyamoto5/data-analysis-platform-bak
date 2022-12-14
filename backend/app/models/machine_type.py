from backend.app.db.session import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class MachineType(Base):
    __tablename__ = "machine_types"

    machine_type_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    machine_type_name = Column(String(255), unique=True, nullable=False)

    machines = relationship("Machine", back_populates="machine_type")

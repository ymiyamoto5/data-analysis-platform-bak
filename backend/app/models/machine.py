from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from backend.app.db.session import Base


class Machine(Base):
    __tablename__ = "machines"

    machine_id = Column(String(255), primary_key=True, index=True)
    machine_name = Column(String(255), nullable=False)
    collect_status = Column(String(255))
    machine_type_id = Column(Integer, ForeignKey("machine_types.machine_type_id"), nullable=False)

    # NOTE: MachineとMachineTypeはMany to One
    machine_type = relationship("MachineType", back_populates="machines")
    # NOTE: MachineとGatewayはOne to Many
    gateways = relationship("Gateway", back_populates="machine")
    # NOTE: MachineとDataCollectHistoryはOne to Many
    data_collect_history = relationship("DataCollectHistory", back_populates="machine", cascade="all, delete")

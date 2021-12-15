from backend.app.db.session import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean


class Machine(Base):
    __tablename__ = "machines"

    machine_id = Column(String(255), primary_key=True, index=True)
    machine_name = Column(String(255), nullable=False)
    collect_status = Column(String(255))
    machine_type_id = Column(Integer, ForeignKey("machine_types.machine_type_id"), nullable=False)
    auto_cut_out_shot = Column(Boolean, nullable=False, default=False)
    start_displacement = Column(Float)
    end_displacement = Column(Float)
    margin = Column(Float)
    auto_predict = Column(Boolean, nullable=False, default=False)
    predict_model = Column(String(255))
    model_version = Column(String(255))
    start_point_dsl = Column(Text)
    max_point_dsl = Column(Text)
    break_point_dsl = Column(Text)

    # NOTE: MachineとMachineTypeはMany to One
    machine_type = relationship("MachineType", back_populates="machines")
    # NOTE: MachineとGatewayはOne to Many
    gateways = relationship("Gateway", back_populates="machine")
    # NOTE: MachineとDataCollectHistoryはOne to Many
    data_collect_histories = relationship("DataCollectHistory", back_populates="machine", cascade="all, delete")

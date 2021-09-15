from backend.app.db.session import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class MachineType(Base):
    __tablename__ = "machine_types"

    # NOTE: dataclassにして型定義をしておくと簡単にjsonシリアライズできる。
    # https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
    # id: int
    # machine_type_name: str

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_type_name = Column(String(255), unique=True, nullable=False)

    machines = relationship("Machine", back_populates="machine_type")

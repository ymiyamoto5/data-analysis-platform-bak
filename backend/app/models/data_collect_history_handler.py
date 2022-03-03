from backend.app.db.session import Base
from backend.app.models.data_collect_history_gateway import DataCollectHistoryGateway
from sqlalchemy import Boolean, Column, ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import relationship


class DataCollectHistoryHandler(Base):
    __tablename__ = "data_collect_history_handlers"

    data_collect_history_id = Column(Integer, primary_key=True, index=True)  # 複合主キーかつその参照先キーも外部キー(data_collect_history.id)
    gateway_id = Column(String(255), primary_key=True, index=True)  # 複合主キー
    handler_id = Column(String(255), primary_key=True, index=True)  # 複合主キー
    handler_type = Column(String(255), nullable=False)
    adc_serial_num = Column(String(255), nullable=False)
    sampling_frequency = Column(Integer, nullable=False)
    sampling_ch_num = Column(Integer, nullable=False)
    filewrite_time = Column(Integer, nullable=False)
    is_primary = Column(Boolean, nullable=False, default=False)

    # NOTE: 複合外部キーが含まれる場合、個別に外部キー設定するとINSERT時に外部キー参照エラーとなる。以下で設定が必要。
    # なお、直接の親を参照しないとダメなことにも注意。（この箇所の場合、DataCollectHistoryのdata_collect_history.idを参照するとエラー）
    # https://stackoverflow.com/questions/46160374/error-in-foreign-key-constraint-with-sqlalchemy
    __table_args__ = (
        ForeignKeyConstraint(
            [data_collect_history_id, gateway_id], [DataCollectHistoryGateway.data_collect_history_id, DataCollectHistoryGateway.gateway_id]
        ),
        {},
    )  # type: ignore

    # Many To One
    data_collect_history_gateway = relationship("DataCollectHistoryGateway", back_populates="data_collect_history_handlers")

    # One to Many
    data_collect_history_sensors = relationship(
        "DataCollectHistorySensor", back_populates="data_collect_history_handler", cascade="all, delete"
    )

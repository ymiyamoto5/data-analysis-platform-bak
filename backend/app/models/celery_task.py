from backend.app.db.session import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class CeleryTask(Base):
    __tablename__ = "celery_tasks"

    task_id = Column(String(255), primary_key=True, index=True)
    data_collect_history_id = Column(Integer, ForeignKey("data_collect_histories.id"), index=True)
    task_type = Column(String(255), nullable=False)

    # Many To One
    data_collect_history = relationship("DataCollectHistory", back_populates="celery_tasks")

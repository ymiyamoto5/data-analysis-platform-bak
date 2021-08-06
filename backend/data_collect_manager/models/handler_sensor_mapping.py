from dataclasses import dataclass
from backend.data_collect_manager.models.db import db


@dataclass
class HandlerSensorMapping(db.Model):
    __tablename__ = "handler_sensor_mapping"

    handler_id: str
    sensor_id: int

    handler_id = db.Column(db.String, db.ForeignKey("handlers.handler_id"), primary_key=True)
    sensor_id = db.Column(db.String, db.ForeignKey("sensors.id"), primary_key=True)

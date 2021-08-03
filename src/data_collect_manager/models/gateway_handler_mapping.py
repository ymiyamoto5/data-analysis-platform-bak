from dataclasses import dataclass
from data_collect_manager.models.db import db


@dataclass
class GatewayHandlerMapping(db.Model):
    __tablename__ = "gateway_handler_mapping"

    gateway_id: int
    handler_id: int

    gateway_id = db.Column(db.Integer, db.ForeignKey("gateways.id"), primary_key=True)
    handler_id = db.Column(db.Integer, db.ForeignKey("handlers.id"), primary_key=True)

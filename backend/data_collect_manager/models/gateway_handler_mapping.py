from dataclasses import dataclass
from backend.data_collect_manager.models.db import db


@dataclass
class GatewayHandlerMapping(db.Model):
    __tablename__ = "gateway_handler_mapping"

    gateway_id: str
    handler_id: str

    gateway_id = db.Column(db.String, db.ForeignKey("gateways.gateway_id"), primary_key=True)
    handler_id = db.Column(db.String, db.ForeignKey("handlers.handler_id"), primary_key=True)

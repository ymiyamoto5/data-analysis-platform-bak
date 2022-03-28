from datetime import datetime
from typing import List

from backend.app.models.gateway_event import GatewayEvent
from backend.app.schemas import notification
from backend.common import common
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session


class CRUDGatewayEvent:
    @staticmethod
    def select_all(db: Session) -> List[GatewayEvent]:
        event: List[GatewayEvent] = db.query(GatewayEvent).order_by(desc(GatewayEvent.timestamp)).all()

        return event

    @staticmethod
    def select_latest_error_by_machine_id(db: Session, id_list: List[str], started_at: datetime) -> GatewayEvent:
        event: GatewayEvent = (
            db.query(GatewayEvent)
            .filter(GatewayEvent.gateway_id.in_(id_list))
            .filter(or_(GatewayEvent.severity == common.Severity.ERROR, GatewayEvent.severity == common.Severity.CRITICAL))
            .filter(GatewayEvent.timestamp > started_at)
            .order_by(desc(GatewayEvent.timestamp))
            .first()
        )

        return event

    @staticmethod
    def insert(db: Session, obj_in: notification.NotificationCreate, utc_now: datetime) -> GatewayEvent:
        new_gateway_event = GatewayEvent(
            timestamp=utc_now,
            severity=obj_in.severity,
            gateway_id=obj_in.gateway_id,
            message=obj_in.message,
        )
        db.add(new_gateway_event)
        db.commit()
        db.refresh(new_gateway_event)
        return new_gateway_event

import traceback
from typing import List

from backend.app.api.deps import get_db
from backend.app.crud.crud_gateway import CRUDGateway
from backend.app.schemas import gateway
from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[gateway.Gateway])
def fetch_gateways(db: Session = Depends(get_db)):
    """Gatewayを起点に関連エンティティを全結合したデータを返す"""

    try:
        gateways = CRUDGateway.select_all(db)
        return gateways
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))


@router.get("/{gateway_id}", response_model=gateway.Gateway)
def fetch_gateway(gateway_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """指定gatewayの情報を取得"""

    try:
        gateway = CRUDGateway.select_by_id(db, gateway_id)
        return gateway
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))


@router.post("/", response_model=gateway.Gateway)
def create(gateway_in: gateway.GatewayCreate, db: Session = Depends(get_db)):
    """gatewayの作成"""

    gateway = CRUDGateway.select_by_id(db, gateway_id=gateway_in.gateway_id)
    if gateway:
        raise HTTPException(status_code=400, detail="ゲートウェイIDが重複しています")

    try:
        gateway = CRUDGateway.insert(db, obj_in=gateway_in)
        return gateway
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.CREATE_FAIL))


@router.put("/{gateway_id}", response_model=gateway.Gateway)
def update(
    gateway_in: gateway.GatewayUpdate,
    gateway_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """gatewayの更新。更新対象のフィールドをパラメータとして受け取る。"""

    gateway = CRUDGateway.select_by_id(db, gateway_id=gateway_id)
    if not gateway:
        raise HTTPException(status_code=404, detail="ゲートウェイが存在しません")

    try:
        gateway = CRUDGateway.update(db, db_obj=gateway, obj_in=gateway_in)
        return gateway
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL))


@router.put("/{gateway_id}/update", response_model=gateway.Gateway)
def update_from_gateway(
    gateway_in: gateway.GatewayUpdateFromGateway,
    gateway_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """GW側からの設定更新。更新対象のフィールドをパラメータとして受け取る。"""

    gateway = CRUDGateway.select_by_id(db, gateway_id=gateway_id)
    if not gateway:
        raise HTTPException(status_code=404, detail="ゲートウェイが存在しません")

    try:
        gateway = CRUDGateway.update_from_gateway(db, db_obj=gateway, obj_in=gateway_in)
        return gateway
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL))


@router.delete("/{gateway_id}", response_model=gateway.Gateway)
def delete(gateway_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """gatewayの削除"""

    gateway = CRUDGateway.select_by_id(db, gateway_id=gateway_id)
    if not gateway:
        raise HTTPException(status_code=404, detail="ゲートウェイが存在しません")

    try:
        gateway = CRUDGateway.delete(db, db_obj=gateway)
        return gateway
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.DELETE_FAIL))

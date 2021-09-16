from typing import List
from backend.app.crud.crud_gateway import CRUDGateway
from fastapi import Depends, APIRouter, HTTPException, Path
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db
from backend.app.schemas import gateway
from backend.common import common

router = APIRouter()


@router.get("/", response_model=List[gateway.Gateway])
def fetch_gateways(db: Session = Depends(get_db)):
    """Gatewayを起点に関連エンティティを全結合したデータを返す"""

    gateways = CRUDGateway.select_all(db)
    return gateways


@router.get("/{gateway_id}", response_model=gateway.Gateway)
def fetch_gateway(gateway_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """指定gatewayの情報を取得"""

    gateway = CRUDGateway.select_by_id(db, gateway_id)
    return gateway


@router.post("/", response_model=gateway.Gateway)
def create(gateway_in: gateway.GatewayCreate, db: Session = Depends(get_db)):
    """gatewayの作成"""

    gateway = CRUDGateway.select_by_id(db, gateway_id=gateway_in.gateway_id)
    if gateway:
        raise HTTPException(status_code=400, detail="ゲートウェイIDが重複しています")

    gateway = CRUDGateway.insert(db, obj_in=gateway_in)
    return gateway


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

    gateway = CRUDGateway.update(db, db_obj=gateway, obj_in=gateway_in)
    return gateway


@router.delete("/{gateway_id}", response_model=gateway.Gateway)
def delete(gateway_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """gatewayの削除"""

    gateway = CRUDGateway.select_by_id(db, gateway_id=gateway_id)
    if not gateway:
        raise HTTPException(status_code=404, detail="ゲートウェイが存在しません")

    gateway = CRUDGateway.delete(db, db_obj=gateway)
    return gateway

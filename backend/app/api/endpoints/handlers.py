import traceback
from typing import List

from backend.app.api.deps import get_db
from backend.app.crud.crud_handler import CRUDHandler
from backend.app.schemas import handler
from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[handler.Handler])
def fetch_handlers(db: Session = Depends(get_db)):
    """Handlerを起点に関連エンティティを全結合したデータを返す"""

    try:
        handlers = CRUDHandler.select_all(db)
        return handlers
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))


@router.get("/{handler_id}", response_model=handler.Handler)
def fetch_handler(handler_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """指定handlerの情報を取得"""

    try:
        handler = CRUDHandler.select_by_id(db, handler_id)
        return handler
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))


@router.post("/", response_model=handler.Handler)
def create(handler_in: handler.HandlerCreate, db: Session = Depends(get_db)):
    """handlerの作成"""

    handler = CRUDHandler.select_by_id(db, handler_id=handler_in.handler_id)
    if handler:
        raise HTTPException(status_code=400, detail="ハンドラーIDが重複しています")

    try:
        handler = CRUDHandler.insert(db, obj_in=handler_in)
        return handler
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.CREATE_FAIL))


@router.put("/{handler_id}", response_model=handler.Handler)
def update(
    handler_in: handler.HandlerUpdate,
    handler_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """handlerの更新。更新対象のフィールドをパラメータとして受け取る。"""

    handler = CRUDHandler.select_by_id(db, handler_id=handler_id)
    if not handler:
        raise HTTPException(status_code=404, detail="ハンドラーが存在しません")

    try:
        handler = CRUDHandler.update(db, db_obj=handler, obj_in=handler_in)
        return handler
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL))


@router.delete("/{handler_id}", response_model=handler.Handler)
def delete(handler_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """handlerの削除"""

    handler = CRUDHandler.select_by_id(db, handler_id=handler_id)
    if not handler:
        raise HTTPException(status_code=404, detail="ハンドラーが存在しません")

    try:
        handler = CRUDHandler.delete(db, db_obj=handler)
        return handler
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.DELETE_FAIL))

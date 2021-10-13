import traceback
from typing import List

from backend.app.api.deps import get_db
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.schemas import data_collect_history
from backend.app.services.data_collect_history_service import DataCollectHistoryService
from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[data_collect_history.DataCollectHistory])
def fetch_data_collect_histories(db: Session = Depends(get_db)):
    """データ収集履歴を返す"""

    try:
        history: List[DataCollectHistory] = CRUDDataCollectHistory.select_all(db)
        return history
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))


@router.get("/{machine_id}", response_model=List[data_collect_history.DataCollectHistory])
def fetch_data_collect_histories_by_machine(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)
):
    """特定機器のデータ収集履歴を返す"""

    try:
        history: List[DataCollectHistory] = CRUDDataCollectHistory.select_by_machine_id(db, machine_id)
        return history
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))


@router.get("/{machine_id}/latest", response_model=data_collect_history.DataCollectHistory)
def fetch_latest_data_collect_history_by_machine(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)
):
    """特定機器の最新のデータ収集履歴を返す"""

    try:
        history: DataCollectHistory = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)
        return history
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))


@router.put("/{id}", response_model=data_collect_history.DataCollectHistory)
def update_data_collect_history(
    id: int, data_collect_history_in: data_collect_history.DataCollectHistoryUpdate, db: Session = Depends(get_db)
):
    """履歴の更新"""

    history: DataCollectHistory = CRUDDataCollectHistory.select_by_id(db, id)
    if not history:
        raise HTTPException(status_code=404, detail="対象の履歴が存在しません")

    try:
        history = CRUDDataCollectHistory.update(db, history, data_collect_history_in)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL))

    return history


@router.delete("/{id}", response_model=data_collect_history.DataCollectHistory)
def delete_data_collect_history(id: int, db: Session = Depends(get_db)):
    """以下を削除する
    * データ収集履歴レコード
    * 削除対象の収集データディレクトリ
    * 削除対象のElasticsearchインデックス
    """

    history: DataCollectHistory = CRUDDataCollectHistory.select_by_id(db, id)
    if not history:
        raise HTTPException(status_code=404, detail="対象の履歴が存在しません")

    # 機器ID + 取得日時 文字列取得
    target: str = DataCollectHistoryService.get_target(history)

    try:
        # ディレクトリを削除
        DataCollectHistoryService.delete_data_directory(target)
        # Elasticsearchインデックスを削除
        DataCollectHistoryService.delete_elastic_index(target)
        # DBから履歴を削除
        deleted: DataCollectHistory = CRUDDataCollectHistory.delete(db, db_obj=history)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.DELETE_FAIL))

    return deleted

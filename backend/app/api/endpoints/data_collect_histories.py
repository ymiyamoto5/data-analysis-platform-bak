from backend.app.models.data_collect_history_detail import DataCollectHistoryDetail
from typing import List
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_data_collect_history_detail import CRUDDataCollectHistoryDetail
from backend.app.schemas import data_collect_history
from backend.app.services.data_collect_history_service import DataCollectHistoryService
from backend.common import common
from fastapi import Depends, APIRouter, Path, HTTPException
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db


router = APIRouter()


@router.get("/", response_model=List[data_collect_history.DataCollectHistory])
def fetch_data_collect_histories(db: Session = Depends(get_db)):
    """データ収集履歴を返す"""

    history: List[DataCollectHistory] = CRUDDataCollectHistory.select_all(db)
    return history


@router.get("/{machine_id}", response_model=List[data_collect_history.DataCollectHistory])
def fetch_data_collect_history_by_machine(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)
):
    """特定機器のデータ収集履歴を返す"""

    history: List[DataCollectHistory] = CRUDDataCollectHistory.select_by_machine_id(db, machine_id)
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

    # ディレクトリを削除
    DataCollectHistoryService.delete_data_directory(target)

    # Elasticsearchインデックスを削除
    DataCollectHistoryService.delete_elastic_index(target)

    # DBから履歴を削除
    deleted: DataCollectHistory = CRUDDataCollectHistory.delete(db, db_obj=history)

    return deleted


@router.get("/{id}")
def fetch_data_collect_history_details(id: int, db: Session = Depends(get_db)):
    history: DataCollectHistory = CRUDDataCollectHistory.select_by_id(db, id)
    if not history:
        raise HTTPException(status_code=404, detail="対象の履歴が存在しません")

    history_details: List[DataCollectHistoryDetail] = history.data_collect_history_details

    return history_details


@router.put("/{id}")
def update_data_collect_history_details(id: int, db: Session = Depends(get_db)):
    """データ収集履歴の詳細（センサー毎の設定値）を更新する"""

    history: DataCollectHistory = CRUDDataCollectHistory.select_by_id(db, id)
    if not history:
        raise HTTPException(status_code=404, detail="対象の履歴が存在しません")

    CRUDDataCollectHistoryDetail.update(db, history.history_details)

from typing import List
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.schemas import data_collect_history
from backend.common import common
from fastapi import Depends, APIRouter, Path
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db


router = APIRouter()


@router.get("/", response_model=List[data_collect_history.DataCollectHistory])
def fetch_data_collect_history(db: Session = Depends(get_db)):
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

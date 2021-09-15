from typing import List
from sqlalchemy.orm import Session
from backend.app.schemas import schemas
from fastapi import Depends, APIRouter
from backend.app.crud import crud
from backend.app.api.deps import get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

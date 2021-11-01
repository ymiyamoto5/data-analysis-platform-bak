import datetime
import traceback

from backend.app.schemas import tag
from backend.common.common_logger import uvicorn_logger as logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from backend.elastic_manager.elastic_manager import ElasticManager
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/")
def fetch_tags():
    """タグリストを返す"""

    query = {"sort": {"occurred_at": {"order": "desc"}}}

    try:
        tags = ElasticManager.get_docs_with_id("tags", query=query)
        return tags
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))


@router.post("/")
def create(tag_in: tag.Tag):
    """タグを記録する"""

    query = {"occurred_at": datetime.datetime.strptime(tag_in.occurred_at, "%Y/%m/%d %H:%M:%S"), "tag": tag_in.tag}

    try:
        tags = ElasticManager.create_doc("tags", doc_id="test-create", query=query)
        return tags
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.CREATE_FAIL))


@router.put("/{tag_id}")
def update(tag_id: str, tag_in: tag.Tag):
    """タグを更新する"""

    query = {"occurred_at": datetime.datetime.strptime(tag_in.occurred_at, "%Y/%m/%d %H:%M:%S"), "tag": tag_in.tag}

    # machine = CRUDMachine.select_by_id(db, machine_id=machine_id)
    # if not machine:
    #     raise HTTPException(status_code=404, detail="機器が存在しません")

    try:
        tags = ElasticManager.update_doc("tags", doc_id=tag_id, query=query)
        return tags
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL))


@router.delete("/{tag_id}")
def delete(tag_id: str):
    """タグを削除する"""

    # machine = CRUDMachine.select_by_id(db, machine_id=machine_id)
    # if not machine:
    #     raise HTTPException(status_code=404, detail="機器が存在しません")

    try:
        tags = ElasticManager.delete_doc("tags", doc_id=tag_id)
        return tags
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.DELETE_FAIL))

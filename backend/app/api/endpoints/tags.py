import datetime
import traceback
from typing import List

from backend.app.schemas import tag
from backend.common.common_logger import uvicorn_logger as logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from backend.elastic_manager.elastic_manager import ElasticManager
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/", response_model=List[tag.Tag])
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
def create(tag_in: tag.TagBase):
    """タグを記録する"""

    tags_index: str = "tags"

    if not ElasticManager.exists_index(index=tags_index):
        ElasticManager.create_index(tags_index)

    if tag_in.ended_at is None:
        ended_at = tag_in.ended_at
    else:
        ended_at = datetime.datetime.strptime(tag_in.ended_at, "%Y/%m/%d %H:%M:%S")

    body = {
        "occurred_at": datetime.datetime.strptime(tag_in.occurred_at, "%Y/%m/%d %H:%M:%S"),
        "ended_at": ended_at,
        "machine_id": tag_in.machine_id,
        "tag": tag_in.tag,
    }

    try:
        tags = ElasticManager.create_doc(tags_index, doc_id=None, query=body)
        return tags
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.CREATE_FAIL))


@router.put("/{tag_id}")
def update(tag_id: str, tag_in: tag.TagBase):
    """タグを更新する"""

    if tag_in.ended_at is None:
        ended_at = tag_in.ended_at
    else:
        ended_at = datetime.datetime.strptime(tag_in.ended_at, "%Y/%m/%d %H:%M:%S")

    body = {
        "occurred_at": datetime.datetime.strptime(tag_in.occurred_at, "%Y/%m/%d %H:%M:%S"),
        "ended_at": ended_at,
        "machine_id": tag_in.machine_id,
        "tag": tag_in.tag,
    }

    try:
        tags = ElasticManager.update_doc("tags", doc_id=tag_id, query=body)
        return tags
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL))


@router.delete("/{tag_id}")
def delete(tag_id: str):
    """タグを削除する"""

    try:
        tags = ElasticManager.delete_doc("tags", doc_id=tag_id)
        return tags
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.DELETE_FAIL))

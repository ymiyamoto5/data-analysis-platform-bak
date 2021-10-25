import traceback

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

import redis
from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/{task_id}")
def fetch_task_info(task_id: str):
    """タスクIDをもとにタスク情報を取得"""
    result = AsyncResult(task_id)
    info = {
        "task_id": result.task_id,
        "status": result.status,
        "result": result.result,
        "traceback": result.traceback,
        "children": result.children,
        "date_done": result.date_done,
    }
    return info


@router.get("/")
def fetch_task_info_all_by_redis():
    """keysをもとにタスク情報の一覧をredisから取得"""
    # host=localhostとするとエラーとなる
    conn = redis.StrictRedis(host="10.3.18.108", port=6379, db=0)
    result = conn.mget(conn.keys("celery-task-meta-*"))
    return result


@router.get("/redis/{task_id}")
def fetch_task_info_by_redis(task_id: str):
    """タスクIDをもとにタスク情報をredisから取得"""
    # host=localhostとするとエラーとなる
    conn = redis.StrictRedis(host="localhost", port=6379, db=0)
    result = conn.get("celery-task-meta-" + task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="タスクが存在しません")
    return result

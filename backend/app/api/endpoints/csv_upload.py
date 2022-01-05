import os
import shutil
from typing import List

from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from fastapi import APIRouter, File, Form, UploadFile

router = APIRouter()


@router.post("/")
def upload(
    machine_id: str = Form(..., max_length=255, regex=common.ID_PATTERN), datetime: int = Form(...), files: List[UploadFile] = File(...)
):
    """csvファイルのアップロード"""

    dir_name: str = machine_id + "-" + str(datetime)
    upload_dir_path: str = os.path.join(os.environ["data_dir"], dir_name)

    # アップロード用のディレクトリを作成
    if os.path.isdir(upload_dir_path):
        logger.debug(f"{upload_dir_path} is already exists")
    else:
        os.makedirs(upload_dir_path)
        logger.info(f"{upload_dir_path} created.")

    # fileをアップロード
    for file in files:
        with open(os.path.join(upload_dir_path, file.filename), "wb+") as f:
            shutil.copyfileobj(file.file, f)

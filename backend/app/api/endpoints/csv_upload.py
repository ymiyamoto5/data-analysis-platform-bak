import os
import shutil
from typing import List

from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from fastapi import APIRouter, File, UploadFile

# from fastapi.datastructures import File, UploadFile
from pydantic import BaseModel, Field

router = APIRouter()


class Item(BaseModel):
    files: List[UploadFile] = File(...)
    # files: List
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    datetime: str


@router.post("/")
def upload(postData: Item):
    """csvファイルのアップロード"""

    # アップロード用のディレクトリを作成
    dir_name: str = postData.machine_id + "-" + postData.datetime

    processed_dir_path: str = os.path.join(os.environ["data_dir"], dir_name)

    if os.path.isdir(processed_dir_path):
        logger.debug(f"{processed_dir_path} is already exists")
    else:
        os.makedirs(processed_dir_path)
        logger.info(f"{processed_dir_path} created.")

    # filesをアップロード
    # upload_path = os.environ["data_dir"] + dir_name
    for file in postData.files:
        with open(file.filename, "wb") as f:
            shutil.copyfileobj(file.file, f)

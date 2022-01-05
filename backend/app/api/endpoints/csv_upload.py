import os
import shutil
from typing import Any, Optional

from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from fastapi import APIRouter, File, Form, Path, UploadFile
from pydantic import BaseModel, Field

router = APIRouter()


class Item(BaseModel):
    file: UploadFile = File(...)
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    datetime: str

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


# class Item2(BaseModel):
#     files: Dict
#     # files: List
#     machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
#     datetime: str

#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate_to_json

#     @classmethod
#     def validate_to_json(cls, value):
#         if isinstance(value, str):
#             return cls(**json.loads(value))
#         return value


class file(BaseModel):
    name: str = Form(...)
    lastModified: int = Form(...)
    lastModifiedDate: Any = Form(...)
    webkitRelativePath: Optional[str] = Form(...)
    size: int = Form(...)


@router.post("/{machine_id}-{datetime}")
def upload(machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), datetime: str = Path(...), file: UploadFile = File(...)):
    """csvファイルのアップロード"""

    # アップロード用のディレクトリを作成
    dir_name: str = machine_id + "-" + datetime

    processed_dir_path: str = os.path.join(os.environ["data_dir"], dir_name)

    if os.path.isdir(processed_dir_path):
        logger.debug(f"{processed_dir_path} is already exists")
    else:
        os.makedirs(processed_dir_path)
        logger.info(f"{processed_dir_path} created.")

    # filesをアップロード実装中
    # upload_path = os.environ["data_dir"] + dir_name
    # for file in file:
    with open(file.filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

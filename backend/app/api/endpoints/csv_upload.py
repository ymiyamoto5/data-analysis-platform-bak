import os
import re
import shutil
from typing import List

from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from backend.data_reader.data_reader import DataReader
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

router = APIRouter()


@router.post("/")
def upload(
    machine_id: str = Form(..., max_length=255, regex=common.ID_PATTERN), date_time: int = Form(...), files: List[UploadFile] = File(...)
):
    """csvファイルのアップロード"""

    dir_name: str = machine_id + "-" + str(date_time)
    dir_path: str = os.path.join(os.environ["DATA_DIR"], dir_name)

    # アップロード用のディレクトリを作成
    if os.path.isdir(dir_path):
        logger.debug(f"{dir_path} is already exists")
    else:
        os.makedirs(dir_path)
        logger.info(f"{dir_path} created.")

    # fileをアップロード
    for file in files:
        file_path: str = os.path.join(dir_path, file.filename)

        # 既にファイルがアップロード済みの場合はスキップ
        if os.path.isfile(file_path):
            logger.debug(f"{file_path} is already exists")
            continue

        if re.search(common.CSV_PATTERN, file.filename) is None:
            raise HTTPException(status_code=400, detail=f"{file.filename}の拡張子がCSVではありません")

        with open(file_path, "wb+") as f:
            shutil.copyfileobj(file.file, f)
            logger.info(f"{file_path} uploaded.")

        # ショットデータの場合はheader範囲の読み取り・加工
        if re.match(r"shots", file.filename) is not None:
            dr = DataReader()
            dr.read_shots_file(dir_path, file.filename)

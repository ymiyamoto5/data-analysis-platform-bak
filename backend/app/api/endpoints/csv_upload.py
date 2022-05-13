import os
import re
import shutil
from datetime import datetime
from typing import List

from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from backend.data_reader.data_reader import DataReader
from backend.file_manager.file_manager import FileInfo
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

router = APIRouter()


@router.post("/")
def upload(
    machine_id: str = Form(..., max_length=255, regex=common.ID_PATTERN), date_time: int = Form(...), files: List[UploadFile] = File(...)
):
    """csvファイルのアップロード"""

    dir_name: str = machine_id + "-" + str(date_time)
    upload_dir_path: str = os.path.join(os.environ["DATA_DIR"], dir_name)

    # アップロード用のディレクトリを作成
    if os.path.isdir(upload_dir_path):
        logger.debug(f"{upload_dir_path} is already exists")
    else:
        os.makedirs(upload_dir_path)
        logger.info(f"{upload_dir_path} created.")

    # fileをアップロード
    for file in files:
        file_path: str = os.path.join(upload_dir_path, file.filename)

        if re.search(common.CSV_PATTERN, file.filename) is None:
            raise HTTPException(status_code=400, detail=f"{file.filename}の拡張子がCSVではありません")
        with open(file_path, "wb+") as f:
            shutil.copyfileobj(file.file, f)

        # ショットデータの場合はheader範囲の読み取り・加工
        if re.match(r"loadstroke", file.filename) is not None:
            # ファイルの情報を取得
            parts: List[str] = re.findall(r"\d+", file.filename)
            timestamp_str: str = parts[0] + "000000"
            timestamp: float = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S%f").timestamp()

            file_info: FileInfo = FileInfo(file_path, timestamp)

            dr = DataReader()
            dr.read_loadstroke_files(upload_dir_path, file_info)

import os
from datetime import datetime, timedelta

from backend.app.crud.crud_machine import CRUDMachine
from backend.app.db.session import SessionLocal
from backend.app.models.machine import Machine
from backend.common.common_logger import logger
from sqlalchemy.orm.session import Session


class DataRecorderService:
    @staticmethod
    def get_processed_dir_path(machine_id: str, started_at: datetime) -> str:
        """処理済みファイルおよびpklファイル格納用のディレクトリ取得（なければ作成）"""

        jst_started_at: datetime = started_at + timedelta(hours=9)
        datetime_suffix: str = jst_started_at.strftime("%Y%m%d%H%M%S")

        dir_name: str = machine_id + "-" + datetime_suffix

        processed_dir_path: str = os.path.join(os.environ["data_dir"], dir_name)

        if os.path.isdir(processed_dir_path):
            logger.debug(f"{processed_dir_path} is already exists")
        else:
            os.makedirs(processed_dir_path)
            logger.info(f"{processed_dir_path} created.")

        return processed_dir_path

    @staticmethod
    def get_collect_status(machine_id) -> str:
        """データ収集ステータスを取得する"""

        # NOTE: DBセッションを使いまわすと更新データが得られないため、新しいセッション作成
        db: Session = SessionLocal()
        machine: Machine = CRUDMachine.select_by_id(db, machine_id)
        collect_status: str = machine.collect_status
        db.close()

        return collect_status

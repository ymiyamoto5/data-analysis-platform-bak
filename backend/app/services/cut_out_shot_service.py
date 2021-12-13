import os
import sys
import time
import traceback
from datetime import datetime
from typing import Final, List

import pandas as pd
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.db.session import SessionLocal
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.machine import Machine
from backend.app.models.sensor import Sensor
from backend.common import common
from backend.common.common_logger import logger
from backend.data_converter.data_converter import DataConverter
from backend.file_manager.file_manager import FileInfo, FileManager
from pandas.core.frame import DataFrame
from sqlalchemy.orm.session import Session


class CutOutShotService:
    @staticmethod
    def auto_cut_out_shot(db: Session, machine_id: str) -> None:
        """自動ショット切り出し"""

        logger.info(f"cut_out_shot process started. machine_id: {machine_id}")

        try:
            latest_data_collect_history: DataCollectHistory = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)
        except Exception:
            logger.exception(traceback.format_exc())
            sys.exit(1)

        has_been_processed: List[str] = []  # 処理済みファイルパスリスト

        INTERVAL: Final[int] = 5

        while True:
            time.sleep(INTERVAL)

            # 退避ディレクトリに存在するすべてのpklファイルリスト
            all_files: List[str] = FileManager.get_files(
                dir_path=latest_data_collect_history.processed_dir_path, pattern=f"{machine_id}_*.pkl"
            )

            # ループ毎の処理対象。未処理のもののみ対象とする。
            target_files: List[str] = CutOutShotService.get_target_files(all_files, has_been_processed)

            # NOTE: 毎度DBにアクセスするのは非効率なため、対象ファイルが存在しないときのみDBから収集ステータスを確認し、停止判断を行う。
            if len(target_files) == 0:
                collect_status = CutOutShotService.get_collect_status(machine_id)

                if collect_status == common.COLLECT_STATUS.RECORDED.value:
                    logger.info(f"cut_out_shot process finished. machine_id: {machine_id}")
                    break
                # 記録が完了していなければ継続
                continue

            # 切り出し処理
            logger.info(f"cut_out_shot processing. machine_id: {machine_id}, targets: {len(target_files)}")

            # 処理済みファイルリストに追加

    @staticmethod
    def get_target_files(all_files: List[str], has_been_processed: List[str]) -> List[str]:
        """all_files（全ファイル）のうち、has_been_processed（処理済み）を除外したリストを返す"""
        target_files: List[str] = []

        for file in all_files:
            if file not in has_been_processed:
                target_files.append(file)

        return target_files

    @staticmethod
    def get_collect_status(machine_id) -> str:
        """データ収集ステータスを取得する"""

        # NOTE: DBセッションを使いまわすと更新データが得られないため、新しいセッション作成
        db: Session = SessionLocal()
        machine: Machine = CRUDMachine.select_by_id(db, machine_id)
        collect_status: str = machine.collect_status
        db.close()

        return collect_status

    @staticmethod
    def get_target_dir(target_date_timestamp: str) -> str:
        """ブラウザから文字列で渡されたUNIXTIME(ミリ秒単位）から、データディレクトリ名の日付文字列を特定して返却"""

        # NOTE: ブラウザからは文字列のJST UNIXTIME(ミリ秒)で与えられる。秒単位に直して変換。
        target_date: datetime = datetime.fromtimestamp(int(target_date_timestamp) / 1000)
        target_date_str: str = datetime.strftime(target_date, "%Y%m%d%H%M%S")

        return target_date_str

    # @staticmethod
    # def get_files_info(machine_id: str, target_date_str: str) -> List[FileInfo]:
    #     target_dir = machine_id + "-" + target_date_str
    #     data_dir: str = os.environ["data_dir"]
    #     data_full_path: str = os.path.join(data_dir, target_dir)

    #     files_info: List[str] = FileManager.get_files(data_full_path, pattern=f"{machine_id}_*.pkl")

    #     return files_info

    @staticmethod
    def fetch_df(target_file: str) -> DataFrame:
        """引数で指定したファイル名のpklファイルを読み込みDataFrameで返す"""

        df = pd.read_pickle(target_file)

        return df

    @staticmethod
    def resample_df(df: DataFrame, sampling_frequency: int, rate: int) -> DataFrame:
        """引数のDataFrameについてリサンプリングして返却する"""

        df = DataConverter.down_sampling_df(df, sampling_frequency, rate=rate)

        return df

    @staticmethod
    def physical_convert_df(df: DataFrame, sensors: List[Sensor]) -> DataFrame:
        """引数のDataFrameをリサンプリングして返却する"""

        for sensor in sensors:
            func = DataConverter.get_physical_conversion_formula(sensor)
            df.loc[:, sensor.sensor_id] = df[sensor.sensor_id].map(func)

        return df

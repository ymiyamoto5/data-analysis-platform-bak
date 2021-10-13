import glob
import os
import time
import traceback
from datetime import datetime
from typing import Final, List, Optional, Tuple

from backend.app.api.deps import get_db
from backend.app.crud.crud_controller import CRUDController
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.models.machine import Machine
from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

router = APIRouter()


WAIT_SECONDS: Final[int] = 1


def validation(
    machine: Machine, collect_status: str, status
) -> Tuple[bool, Optional[str], int]:
    """machineとmachineに紐づくgatewayのvalidation
    * Noneでないこと
    * 対応するGatewayが1つ以上あること
    * 収集ステータスが正しいこと
    * gateway_resultが-1でないこと
    * GWステータスが正しいこと
    """

    if machine is None:
        message: str = ErrorMessage.generate_message(ErrorTypes.NOT_EXISTS)
        return False, message, 404

    if len(machine.gateways) == 0:
        message = ErrorMessage.generate_message(ErrorTypes.NO_DATA)
        return False, message, 404

    if machine.collect_status != collect_status:
        message = ErrorMessage.generate_message(
            ErrorTypes.GW_STATUS_ERROR, machine.collect_status
        )
        return False, message, 400

    for gateway in machine.gateways:
        if gateway.gateway_result == -1:
            message = ErrorMessage.generate_message(
                ErrorTypes.GW_RESULT_ERROR, gateway.gateway_result
            )
            return False, message, 500

        if gateway.status != status:
            message = ErrorMessage.generate_message(
                ErrorTypes.GW_STATUS_ERROR, gateway.status
            )
            return False, message, 500

    return True, None, 200


@router.post("/setup/{machine_id}")
def setup(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """指定機器のデータ収集段取開始"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集完了状態かつGW停止状態であることが前提
    is_valid, message, error_code = validation(
        machine, common.COLLECT_STATUS.RECORDED.value, common.STATUS.STOP.value
    )
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    try:
        CRUDController.setup(db, machine=machine, utc_now=utc_now)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/start/{machine_id}")
def start(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """指定機器のデータ収集開始"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 段取状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(
        machine, common.COLLECT_STATUS.SETUP.value, common.STATUS.RUNNING.value
    )
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    try:
        CRUDController.start(db, machine=machine, utc_now=utc_now)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/pause/{machine_id}")
def pause(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """指定機器のデータ収集中断（中断中もデータ自体は収集されている。中断区間はショット切り出しの対象外となる。）"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    try:
        CRUDController.pause(db, machine=machine, utc_now=utc_now)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/resume/{machine_id}")
def resume(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """指定機器のデータ収集再開"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集中断状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(
        machine, common.COLLECT_STATUS.PAUSE.value, common.STATUS.RUNNING.value
    )
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    # RESUMEはDBの状態としては保持しない。STARTに更新する。
    try:
        CRUDController.resume(db, machine=machine, utc_now=utc_now)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/stop/{machine_id}")
def stop(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """指定機器のデータ収集停止"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集開始状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(
        machine, common.COLLECT_STATUS.START.value, common.STATUS.RUNNING.value
    )
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    # DB更新
    try:
        CRUDController.stop(db, machine=machine, utc_now=utc_now)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/check/{machine_id}")
def check(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """data_recorderによるデータ取り込みが完了したか確認。dataディレクトリにdatファイルが残っていなければ完了とみなす。"""

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集停止状態かつGW停止状態であることが前提
    is_valid, message, error_code = validation(
        machine, common.COLLECT_STATUS.STOP.value, common.STATUS.STOP.value
    )
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    data_dir: str = common.get_config_value("data_dir", "/mnt/datadrive/data/")

    while True:
        data_file_list: List[str] = glob.glob(os.path.join(data_dir, "*.dat"))

        if len(data_file_list) != 0:
            time.sleep(WAIT_SECONDS)
            continue

        utc_now: datetime = datetime.utcnow()

        try:
            CRUDController.record(db, machine=machine, utc_now=utc_now)
        except Exception:
            raise HTTPException(status_code=500, detail="DB update error.")

        return

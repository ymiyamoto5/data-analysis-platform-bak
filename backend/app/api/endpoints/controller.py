import os
import time
import glob
from typing import Optional, List, Tuple, Final
from datetime import datetime
from fastapi import Depends, APIRouter, HTTPException, Path
from sqlalchemy.orm import Session
from backend.common import common
from backend.common.error_message import ErrorMessage, ErrorTypes
from backend.app.models.machine import Machine
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.crud.crud_controller import CRUDController
from backend.event_manager.event_manager import EventManager
from backend.app.api.deps import get_db

router = APIRouter()


WAIT_SECONDS: Final[int] = 1


def validation(machine: Machine, collect_status: str, status) -> Tuple[bool, Optional[str], int]:
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
        message = ErrorMessage.generate_message(ErrorTypes.GW_STATUS_ERROR, machine.collect_status)
        return False, message, 400

    for gateway in machine.gateways:
        if gateway.gateway_result == -1:
            message = ErrorMessage.generate_message(ErrorTypes.GW_RESULT_ERROR, gateway.gateway_result)
            return False, message, 500

        if gateway.status != status:
            message = ErrorMessage.generate_message(ErrorTypes.GW_STATUS_ERROR, gateway.status)
            return False, message, 500

    return True, None, 200


@router.post("/setup/{machine_id}")
def setup(machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """指定機器のデータ収集段取開始"""

    utc_now: datetime = datetime.utcnow()
    jst_now: common.DisplayTime = common.DisplayTime(utc_now)

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集完了状態かつGW停止状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.RECORDED.value, common.STATUS.STOP.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    # events_index作成(events-<gw-id>-yyyyMMddHHMMSS(jst))
    successful: bool
    events_index: str
    successful, events_index = EventManager.create_events_index(machine.machine_id, jst_now.to_string())

    if not successful:
        raise HTTPException(status_code=500, detail="events_indexの作成に失敗しました。")

    # events_indexに段取り開始(setup)を記録
    successful = EventManager.record_event(
        events_index, event_type=common.COLLECT_STATUS.SETUP.value, occurred_time=utc_now
    )

    if not successful:
        raise HTTPException(status_code=500, detail="events_indexのデータ投入に失敗しました。")

    try:
        CRUDController.setup(db, machine=machine, utc_now=utc_now)
    except Exception:
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/start/{machine_id}")
def start(machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """指定機器のデータ収集開始"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 段取状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.SETUP.value, common.STATUS.RUNNING.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    events_index: Optional[str] = EventManager.get_latest_events_index(machine_id)

    if events_index is None:
        raise HTTPException(status_code=500, detail="対象のevents_indexがありません。")

    # events_indexに収集開始(start)を記録
    successful: bool = EventManager.record_event(
        events_index, event_type=common.COLLECT_STATUS.START.value, occurred_time=utc_now
    )

    if not successful:
        raise HTTPException(status_code=500, detail="events_indexのデータ投入に失敗しました。")

    try:
        CRUDMachine.update(db, db_obj=machine, obj_in={"collect_status": common.COLLECT_STATUS.START.value})
    except Exception:
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/pause/{machine_id}")
def pause(machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """指定機器のデータ収集中断（中断中もデータ自体は収集されている。中断区間はショット切り出しの対象外となる。）"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集開始状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.START.value, common.STATUS.RUNNING.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    events_index: Optional[str] = EventManager.get_latest_events_index(machine_id)

    if events_index is None:
        raise HTTPException(status_code=500, detail="対象のevents_indexがありません。")

    # events_indexに中断(pause)を記録
    successful: bool = EventManager.record_event(
        events_index, event_type=common.COLLECT_STATUS.PAUSE.value, occurred_time=utc_now
    )

    if not successful:
        raise HTTPException(status_code=500, detail="events_indexのデータ投入に失敗しました。")

    try:
        CRUDMachine.update(db, db_obj=machine, obj_in={"collect_status": common.COLLECT_STATUS.PAUSE.value})
    except Exception:
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/resume/{machine_id}")
def resume(machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """指定機器のデータ収集再開"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集中断状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.PAUSE.value, common.STATUS.RUNNING.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    events_index: Optional[str] = EventManager.get_latest_events_index(machine_id)

    if events_index is None:
        raise HTTPException(status_code=500, detail="対象のevents_indexがありません。")

    # events_indexの中断イベントに再開イベントを追加
    successful: bool = EventManager.update_pause_event(events_index, occurred_time=utc_now)

    if not successful:
        raise HTTPException(status_code=500, detail="events_indexのデータ投入に失敗しました。")

    # RESUMEはDBの状態としては保持しない。STARTに更新する。
    try:
        CRUDMachine.update(db, db_obj=machine, obj_in={"collect_status": common.COLLECT_STATUS.START.value})
    except Exception:
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/stop/{machine_id}")
def stop(machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """指定機器のデータ収集開始"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集開始状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.START.value, common.STATUS.RUNNING.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    events_index: Optional[str] = EventManager.get_latest_events_index(machine_id)

    if events_index is None:
        raise HTTPException(status_code=500, detail="対象のevents_indexがありません。")

    # events_indexに収集停止(stop)を記録
    successful: bool = EventManager.record_event(
        events_index, event_type=common.COLLECT_STATUS.STOP.value, occurred_time=utc_now
    )

    if not successful:
        raise HTTPException(status_code=500, detail="events_indexのデータ投入に失敗しました。")

    # DB更新
    try:
        CRUDController.stop(db, machine=machine)
    except Exception:
        raise HTTPException(status_code=500, detail="DB update error.")

    return


@router.post("/check/{machine_id}")
def check(machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """data_recorderによるデータ取り込みが完了したか確認。dataディレクトリにdatファイルが残っていなければ完了とみなす。"""

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)

    # 収集停止状態かつGW停止状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.STOP.value, common.STATUS.STOP.value)
    if not is_valid:
        raise HTTPException(status_code=error_code, detail=message)

    data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")

    while True:
        data_file_list: List[str] = glob.glob(os.path.join(data_dir, "*.dat"))

        if len(data_file_list) != 0:
            time.sleep(WAIT_SECONDS)
            continue

        # 最新のevents_indexを取得し、記録完了イベントを記録
        events_index: Optional[str] = EventManager.get_latest_events_index(machine_id)

        if events_index is None:
            raise HTTPException(status_code=500, detail="対象のevents_indexがありません。")

        utc_now: datetime = datetime.utcnow()

        successful: bool = EventManager.record_event(
            events_index, event_type=common.COLLECT_STATUS.RECORDED.value, occurred_time=utc_now
        )

        if not successful:
            raise HTTPException(status_code=500, detail="events_indexのデータ投入に失敗しました。")

        try:
            CRUDController.record(db, machine=machine, utc_now=utc_now)
        except Exception:
            raise HTTPException(status_code=500, detail="DB update error.")

        return

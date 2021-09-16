from typing import List
from backend.app.crud.crud_sensor import CRUDSensor
from fastapi import Depends, APIRouter, HTTPException, Path, Query
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db
from backend.app.schemas import sensor
from backend.common import common

router = APIRouter()


@router.get("/", response_model=List[sensor.Sensor])
def fetch_sensors(db: Session = Depends(get_db)):
    """Sensorを起点に関連エンティティを全結合したデータを返す"""

    sensors = CRUDSensor.select_all(db)
    return sensors


@router.get("/{sensor_id}", response_model=sensor.Sensor)
def fetch_sensor(
    machine_id: str = Query(..., max_length=255, regex=common.ID_PATTERN),
    sensor_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """指定sensorの情報を取得。machine_idはクエリパラメータで取得。"""

    sensor = CRUDSensor.select_by_id(db, machine_id=machine_id, sensor_id=sensor_id)
    return sensor


@router.post("/", response_model=sensor.Sensor)
def create(sensor_in: sensor.SensorCreate, db: Session = Depends(get_db)):
    """sensorの作成。machine_idはhandler_idから引く。"""

    sensor = CRUDSensor.insert(db, obj_in=sensor_in)
    return sensor


@router.put("/{sensor_id}", response_model=sensor.Sensor)
def update(
    sensor_in: sensor.SensorUpdate,
    sensor_id: str = Path(...),
    db: Session = Depends(get_db),
):
    """sensorの更新。machine_idはPUTのbodyから取得し、sensor_idはURLパスパラメータで指定する。"""

    sensor = CRUDSensor.select_by_id(db, machine_id=sensor_in.machine_id, sensor_id=sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="センサーが存在しません")

    sensor = CRUDSensor.update(db, db_obj=sensor, obj_in=sensor_in)
    return sensor


@router.delete("/{sensor_id}", response_model=sensor.Sensor)
def delete(
    sensor_in: sensor.SensorDelete,
    sensor_id: str = Path(...),
    db: Session = Depends(get_db),
):
    """sensorの削除。machine_idはbodyから取得。"""

    sensor = CRUDSensor.select_by_id(db, machine_id=sensor_in.machine_id, sensor_id=sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="センサーが存在しません")

    sensor = CRUDSensor.delete(db, db_obj=sensor)
    return sensor

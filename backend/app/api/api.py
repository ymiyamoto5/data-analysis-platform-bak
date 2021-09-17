from fastapi import APIRouter
from backend.app.api.endpoints import machines
from backend.app.api.endpoints import machine_types
from backend.app.api.endpoints import gateways
from backend.app.api.endpoints import handlers
from backend.app.api.endpoints import sensors
from backend.app.api.endpoints import sensor_types
from backend.app.api.endpoints import controller
from backend.app.api.endpoints import cut_out_shot
from backend.app.api.endpoints import data_collect_history

api_router = APIRouter()

api_router.include_router(machines.router, prefix="/machines", tags=["machines"])
api_router.include_router(machine_types.router, prefix="/machine_types", tags=["machine_types"])
api_router.include_router(gateways.router, prefix="/gateways", tags=["gateways"])
api_router.include_router(handlers.router, prefix="/handlers", tags=["handlers"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
api_router.include_router(sensor_types.router, prefix="/sensor_types", tags=["sensor_types"])
api_router.include_router(controller.router, prefix="/controller", tags=["controller"])
api_router.include_router(cut_out_shot.router, prefix="/cut_out_shot", tags=["cut_out_shot"])
api_router.include_router(data_collect_history.router, prefix="/data_collect_history", tags=["data_collect_history"])

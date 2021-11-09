from backend.app.api.endpoints import (
    controller,
    cut_out_shot,
    data_collect_histories,
    features,
    gateways,
    handlers,
    machine_types,
    machines,
    models,
    sensor_types,
    sensors,
    tags,
)
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(machines.router, prefix="/machines", tags=["machines"])
api_router.include_router(machine_types.router, prefix="/machine_types", tags=["machine_types"])
api_router.include_router(gateways.router, prefix="/gateways", tags=["gateways"])
api_router.include_router(handlers.router, prefix="/handlers", tags=["handlers"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
api_router.include_router(sensor_types.router, prefix="/sensor_types", tags=["sensor_types"])
api_router.include_router(controller.router, prefix="/controller", tags=["controller"])
api_router.include_router(cut_out_shot.router, prefix="/cut_out_shot", tags=["cut_out_shot"])
api_router.include_router(
    data_collect_histories.router,
    prefix="/data_collect_histories",
    tags=["data_collect_histories"],
)
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(features.router, prefix="/features", tags=["features"])
api_router.include_router(models.router, prefix="/models", tags=["models"])

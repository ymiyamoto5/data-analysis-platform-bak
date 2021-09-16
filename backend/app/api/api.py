from fastapi import APIRouter
from backend.app.api.endpoints import machines
from backend.app.api.endpoints import machine_types
from backend.app.api.endpoints import gateways
from backend.app.api.endpoints import handlers
from backend.app.api.endpoints import controller

api_router = APIRouter()

api_router.include_router(machines.router, prefix="/machines", tags=["machines"])
api_router.include_router(machine_types.router, prefix="/machine_types", tags=["machine_types"])
api_router.include_router(gateways.router, prefix="/gateways", tags=["gateways"])
api_router.include_router(handlers.router, prefix="/handlers", tags=["handlers"])
api_router.include_router(controller.router, prefix="/controller", tags=["controller"])

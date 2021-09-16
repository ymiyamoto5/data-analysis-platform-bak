from fastapi import APIRouter
from backend.app.api.endpoints import machines
from backend.app.api.endpoints import machine_types
from backend.app.api.endpoints import controller

api_router = APIRouter()

api_router.include_router(machines.router, prefix="/machines", tags=["machines"])
api_router.include_router(machine_types.router, prefix="/machine_types", tags=["machine_types"])
api_router.include_router(controller.router, prefix="/controller", tags=["controller"])

from fastapi import APIRouter
from backend.app.api.endpoints import users
from backend.app.api.endpoints import items
from backend.app.api.endpoints import machines

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(machines.router, prefix="/machines", tags=["machines"])

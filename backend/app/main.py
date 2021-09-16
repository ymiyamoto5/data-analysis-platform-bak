from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from backend.app.api.api import api_router
import sqlalchemy.engine
from sqlalchemy import event

app = FastAPI()


# @event.listens_for(sqlalchemy.engine.Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys = ON")
#     cursor.close()


# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

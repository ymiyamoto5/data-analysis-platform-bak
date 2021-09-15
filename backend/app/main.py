from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from backend.app.models import models
from backend.app.db.session import engine
from backend.app.api.api import api_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

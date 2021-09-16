from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from backend.app.api.api import api_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend/dist/"), name="static")

templates = Jinja2Templates(directory="frontend/dist/")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

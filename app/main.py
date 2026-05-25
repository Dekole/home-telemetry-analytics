import asyncio
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import db
from api.events import router as events_router
from collector import run_collector

load_dotenv()
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(application: FastAPI):
    await db.init_pool()
    collector_task = asyncio.create_task(run_collector())
    yield
    collector_task.cancel()
    await db.close_pool()


app = FastAPI(title="home-telemetry-analytics", lifespan=lifespan)
app.include_router(events_router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "demo_mode": os.getenv("DEMO_MODE", "false").lower() == "true",
        "camera_connected": False,
    }


@app.get("/")
async def index():
    return FileResponse("static/index.html")

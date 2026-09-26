import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import settings
from app.logutil import log
from app.worker import worker


@asynccontextmanager
async def lifespan(_app: FastAPI):
    log.info("ingestor starting — ingest is async (202 + poll /v1/ingest/{id})")
    task = asyncio.create_task(worker())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Jena Ingestor", version="0.1.0", lifespan=lifespan)
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

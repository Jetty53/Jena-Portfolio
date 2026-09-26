from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import settings
from app.logutil import log
from app.sessions import init_schema

app = FastAPI(title="Jena Retriever", version="0.1.0")
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

try:
    init_schema()
    log.info("retriever ready — POST /v1/ask  (session_id + history for follow-ups)")
except Exception as e:
    log.warning("session schema init skipped: %s", e)

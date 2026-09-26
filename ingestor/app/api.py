from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.auth import require_token
from app.config import settings
from app.db import db
from app.logutil import step as log_step
from app.parsers.detect import UnsupportedFile, sniff
from app.store import get_request, list_audit
from app.worker import queue

router = APIRouter()

SOURCE_TYPES = {"cv", "github", "academic", "project", "preferences", "other"}
TERMINAL = {"succeeded", "failed", "partial"}


class IngestAccepted(BaseModel):
    request_id: str
    status: str
    files: list[str]
    poll_url: str


@router.get("/health")
def health():
    return {"ok": True, "embed_model": settings.gemini_embed_model, "embed_dim": settings.embed_dim}


@router.post("/v1/ingest/upload", dependencies=[Depends(require_token)])
async def upload(
    files: list[UploadFile] = File(...),
    source_type: str = Form("other"),
):
    if source_type not in SOURCE_TYPES:
        raise HTTPException(400, f"source_type must be one of {sorted(SOURCE_TYPES)}")
    if not files:
        raise HTTPException(400, "at least one file is required")
    if len(files) > settings.max_files_per_request:
        raise HTTPException(400, f"max {settings.max_files_per_request} files per request")

    payloads: list[tuple[str, bytes]] = []
    names_seen: dict[str, int] = {}
    for f in files:
        name = f.filename or "upload.bin"
        data = await f.read()
        if len(data) > settings.max_file_bytes:
            raise HTTPException(400, f"{name} exceeds 10MB limit")
        if not data:
            raise HTTPException(400, f"{name} is empty")
        try:
            sniff(name, data)
        except UnsupportedFile as e:
            raise HTTPException(400, str(e)) from e
        n = names_seen.get(name, 0)
        names_seen[name] = n + 1
        if n:
            stem, _, ext = name.rpartition(".")
            name = f"{stem}_{n}.{ext}" if ext else f"{name}_{n}"
        payloads.append((name, data))

    request_id = uuid4()
    with db() as conn:
        conn.execute(
            """
            INSERT INTO ingest_requests (id, status, source_type, origin, r2_prefix, file_count)
            VALUES (%s, 'queued', %s, 'upload', %s, %s)
            """,
            (
                str(request_id),
                source_type,
                f"{settings.r2_prefix_in_progress}/{request_id}/",
                len(payloads),
            ),
        )

    await queue().put({"request_id": request_id, "source_type": source_type, "files": payloads})
    log_step(str(request_id), "API accepted", f"{len(payloads)} file(s) queued — poll GET /v1/ingest/{request_id}")

    body = IngestAccepted(
        request_id=str(request_id),
        status="queued",
        files=[n for n, _ in payloads],
        poll_url=f"/v1/ingest/{request_id}",
    )
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=body.model_dump())


def _jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool, dict, list)):
        return value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


@router.get("/v1/ingest/{request_id}", dependencies=[Depends(require_token)])
def ingest_status(request_id: str):
    row = get_request(request_id)
    if not row:
        raise HTTPException(404, "request not found")
    steps = [
        {
            "step": a["step"],
            "status": a["status"],
            "detail": a["detail"],
            "created_at": _jsonable(a["created_at"]),
        }
        for a in list_audit(request_id)
    ]
    current = row.get("last_ok_step") or (steps[-1]["step"] if steps else "queued")
    st = row["status"]
    return {
        "request_id": str(row["id"]),
        "status": st,
        "done": st in TERMINAL,
        "current_step": current,
        "error": row.get("error"),
        "file_count": row.get("file_count"),
        "source_type": row.get("source_type"),
        "steps": steps,
    }

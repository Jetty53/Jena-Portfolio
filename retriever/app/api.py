import json
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.auth import require_token
from app.config import settings
from app.logutil import step
from app.pipeline import ask, iter_ask_stream

router = APIRouter()


class HistoryTurn(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4000)


class AskBody(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    source_type: str | None = None
    session_id: str | None = None
    history: list[HistoryTurn] | None = None


def _history(body: AskBody) -> list[dict] | None:
    return [t.model_dump() for t in body.history] if body.history else None


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.get("/health")
def health():
    return {
        "ok": True,
        "embed_model": settings.gemini_embed_model,
        "generate_model": settings.gemini_generate_model,
        "embed_dim": settings.embed_dim,
        "top_k": settings.retrieve_top_k,
    }


@router.post("/v1/ask", dependencies=[Depends(require_token)])
def ask_endpoint(body: AskBody):
    step("API ask", body.question[:160])
    try:
        return ask(
            body.question,
            source_type=body.source_type,
            history=_history(body),
            session_id=body.session_id,
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/v1/ask/stream", dependencies=[Depends(require_token)])
def ask_stream_endpoint(body: AskBody):
    step("API ask stream", body.question[:160])

    def events():
        try:
            for item in iter_ask_stream(
                body.question,
                source_type=body.source_type,
                history=_history(body),
                session_id=body.session_id,
            ):
                yield _sse(item["event"], item["data"])
        except ValueError as e:
            yield _sse("error", {"message": str(e)})
        except Exception as e:
            yield _sse("error", {"message": str(e)[:300]})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/v1/session", dependencies=[Depends(require_token)])
def new_session():
    return {"session_id": str(uuid4())}

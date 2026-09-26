from pathlib import Path
from uuid import UUID, uuid4

from app.config import settings
from app.db import db

_SCHEMA = Path(__file__).resolve().parent.parent / "sql" / "001_sessions.sql"


def init_schema() -> None:
    raw = _SCHEMA.read_text(encoding="utf-8")
    statements = [s.strip() for s in raw.split(";") if s.strip()]
    with db() as conn:
        for stmt in statements:
            conn.execute(stmt)


def ensure_session(session_id: str | None) -> str:
    sid = session_id or str(uuid4())
    with db() as conn:
        conn.execute(
            "INSERT INTO chat_sessions (id) VALUES (%s) ON CONFLICT (id) DO NOTHING",
            (sid,),
        )
    return sid


def load_history(session_id: str, limit: int | None = None) -> list[dict]:
    n = limit if limit is not None else settings.history_turns
    with db() as conn:
        rows = conn.execute(
            """
            SELECT role, content FROM (
                SELECT role, content, created_at
                FROM chat_turns
                WHERE session_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            ) t ORDER BY created_at
            """,
            (session_id, n),
        ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in rows]


def append_turn(session_id: str, role: str, content: str) -> None:
    with db() as conn:
        conn.execute(
            "INSERT INTO chat_turns (session_id, role, content) VALUES (%s, %s, %s)",
            (session_id, role, content),
        )


def is_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except (ValueError, TypeError):
        return False

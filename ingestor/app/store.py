from datetime import datetime, timezone
from uuid import UUID

from app.db import Jsonb, db


def audit(request_id: UUID, step: str, status: str, detail: dict | None = None, document_id: UUID | None = None) -> None:
    with db() as conn:
        conn.execute(
            """
            INSERT INTO ingest_audit (request_id, document_id, step, status, detail)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (str(request_id), str(document_id) if document_id else None, step, status, Jsonb(detail or {})),
        )


def set_request(request_id: UUID, **fields) -> None:
    if "started_at" in fields and fields["started_at"] is True:
        fields["started_at"] = datetime.now(timezone.utc)
    if "finished_at" in fields and fields["finished_at"] is True:
        fields["finished_at"] = datetime.now(timezone.utc)
    assignments = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [str(request_id)]
    with db() as conn:
        conn.execute(f"UPDATE ingest_requests SET {assignments} WHERE id = %s", values)


def get_request(request_id) -> dict | None:
    with db() as conn:
        row = conn.execute("SELECT * FROM ingest_requests WHERE id = %s", (str(request_id),)).fetchone()
        return dict(row) if row else None


def list_audit(request_id) -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            "SELECT step, status, detail, created_at FROM ingest_audit WHERE request_id = %s ORDER BY created_at",
            (str(request_id),),
        ).fetchall()
        return [dict(r) for r in rows]


def find_doc_by_hash(sha256: str) -> dict | None:
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE sha256 = %s AND status = 'embedded' ORDER BY created_at DESC LIMIT 1",
            (sha256,),
        ).fetchone()
        return dict(row) if row else None

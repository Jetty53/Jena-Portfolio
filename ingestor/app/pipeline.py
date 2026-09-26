from __future__ import annotations

import shutil
from pathlib import Path
from uuid import UUID, uuid4

from psycopg.errors import UniqueViolation

from app.chunking.semantic import semantic_chunks
from app.chunking.util import chunk_id, estimate_tokens, prefix_chunk, sha256_bytes
from app.config import settings
from app.db import Jsonb, db, vector_literal
from app.gemini import embed_texts
from app.logutil import step as log_step
from app.parsers import parse_file
from app.parsers.detect import sniff
from app.r2 import key_for, promote, put_bytes
from app.store import audit, find_doc_by_hash, set_request


def _tmp(request_id: UUID) -> Path:
    p = Path(settings.tmp_dir) / str(request_id)
    p.mkdir(parents=True, exist_ok=True)
    return p


def ingest_files(request_id: UUID, source_type: str, files: list[tuple[str, bytes]]) -> None:
    """files: (filename, raw_bytes). Worker stages R2 in-progress then promotes."""
    rid = str(request_id)
    tmp = _tmp(request_id)
    try:
        set_request(request_id, status="running", started_at=True, last_ok_step="queued")
        log_step(rid, "1/8 queued → running", f"{len(files)} file(s)")
        audit(request_id, "start", "ok", {"file_count": len(files)})
        any_ok = False
        last_error: str | None = None

        for filename, raw in files:
            staged_key = key_for(settings.r2_prefix_in_progress, rid, filename)
            try:
                log_step(rid, "2/8 stage R2 in-progress", f"{filename} → {staged_key}")
                put_bytes(staged_key, raw)
                audit(request_id, "r2_in_progress", "ok", {"key": staged_key})
                set_request(request_id, last_ok_step="r2_in_progress")
                _ingest_one(request_id, source_type, filename, raw, staged_key, tmp)
                any_ok = True
            except Exception as e:
                last_error = str(e)
                log_step(rid, "FAILED", f"{filename}: {last_error}")
                audit(request_id, "document", "failed", {"filename": filename, "error": last_error})
                try:
                    dest = promote(staged_key, settings.r2_prefix_failed, rid, filename)
                    log_step(rid, "R2 move", f"in-progress → failed  {dest}")
                    audit(request_id, "r2_failed", "ok", {"key": dest})
                except Exception as move_err:
                    log_step(rid, "R2 move failed", str(move_err))

        if any_ok and last_error:
            set_request(request_id, status="partial", error=last_error, finished_at=True, last_ok_step="done")
            log_step(rid, "8/8 done", "partial — some files failed")
        elif any_ok:
            set_request(request_id, status="succeeded", error=None, finished_at=True, last_ok_step="done")
            audit(request_id, "finalize", "ok", {})
            log_step(rid, "8/8 done", "succeeded")
        else:
            set_request(request_id, status="failed", error=last_error, finished_at=True, last_ok_step="done")
            audit(request_id, "finalize", "failed", {"error": last_error})
            log_step(rid, "8/8 done", f"failed — {last_error}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        audit(request_id, "cleanup", "ok", {})
        log_step(rid, "tmp cleanup", str(tmp))


def _ingest_one(
    request_id: UUID,
    source_type: str,
    filename: str,
    raw: bytes,
    staged_key: str,
    tmp: Path,
) -> None:
    rid = str(request_id)
    _ext, mime = sniff(filename, raw)
    digest = sha256_bytes(raw)
    log_step(rid, "3/8 hash / dedup", f"{filename} sha256={digest[:12]}…")
    audit(request_id, "hash", "ok", {"sha256": digest, "filename": filename})
    set_request(request_id, last_ok_step="hash")

    existing = find_doc_by_hash(digest)
    if existing:
        dest = promote(staged_key, settings.r2_prefix_succeeded, rid, filename)
        log_step(rid, "7/8 R2 move", f"duplicate — in-progress → succeeded  {dest}")
        audit(request_id, "dedup", "skipped", {"sha256": digest, "existing_document_id": existing["id"]})
        return

    dest_path = tmp / Path(filename).name
    dest_path.write_bytes(raw)

    log_step(rid, "4/8 parse", filename)
    parsed = parse_file(dest_path, filename, raw)
    if not parsed.text.strip():
        raise ValueError("parser returned empty text")
    audit(request_id, "parse", "ok", {"parser": parsed.parser, "chars": len(parsed.text)})
    set_request(request_id, last_ok_step="parse")
    log_step(rid, "4/8 parse ok", f"parser={parsed.parser} chars={len(parsed.text)}")

    log_step(rid, "5/8 chunk", "semantic chunking")
    raw_texts, chunker_version = semantic_chunks(parsed.text)
    if not raw_texts:
        raise ValueError("no chunks produced")
    texts = [prefix_chunk(filename, source_type, t) for t in raw_texts]
    audit(request_id, "chunk", "ok", {"count": len(texts), "chunker": chunker_version, "prefixed": True})
    set_request(request_id, last_ok_step="chunk")
    log_step(rid, "5/8 chunk ok", f"{len(texts)} chunks ({chunker_version}, prefixed)")

    log_step(rid, "6/8 embed", settings.gemini_embed_model)
    vectors = embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")
    audit(request_id, "embed", "ok", {"model": settings.gemini_embed_model, "count": len(vectors)})
    set_request(request_id, last_ok_step="embed")
    log_step(rid, "6/8 embed ok", f"{len(vectors)} vectors")

    doc_id = uuid4()
    dest_key = key_for(settings.r2_prefix_succeeded, rid, filename)

    log_step(rid, "7/8 store pgvector", f"document {doc_id}")
    try:
        with db() as conn:
            conn.execute(
                """
                INSERT INTO documents (
                    id, request_id, source_type, filename, mime_type, byte_size, sha256,
                    r2_key, parser, char_count, status, metadata
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'embedded',%s)
                """,
                (
                    str(doc_id),
                    str(request_id),
                    source_type,
                    filename,
                    mime,
                    len(raw),
                    digest,
                    dest_key,
                    parsed.parser,
                    len(parsed.text),
                    Jsonb(parsed.extra or {}),
                ),
            )
            for i, (text, vec) in enumerate(zip(texts, vectors, strict=True)):
                cid = chunk_id(doc_id, i, chunker_version)
                conn.execute(
                    """
                    INSERT INTO chunks (
                        id, document_id, request_id, chunk_index, text, token_count,
                        source_type, uri, embed_model, embed_dim, chunker_version, embedding
                    ) VALUES (
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s::vector
                    )
                    """,
                    (
                        str(cid),
                        str(doc_id),
                        str(request_id),
                        i,
                        text,
                        estimate_tokens(text),
                        source_type,
                        dest_key,
                        settings.gemini_embed_model,
                        settings.embed_dim,
                        chunker_version,
                        vector_literal(vec),
                    ),
                )
    except UniqueViolation:
        dest = promote(staged_key, settings.r2_prefix_succeeded, rid, filename)
        log_step(rid, "7/8 R2 move", f"race dedup — in-progress → succeeded  {dest}")
        audit(request_id, "dedup", "skipped", {"sha256": digest, "race": True})
        return

    dest = promote(staged_key, settings.r2_prefix_succeeded, rid, filename)
    log_step(rid, "7/8 R2 move", f"in-progress → succeeded  {dest}")
    audit(request_id, "r2_succeeded", "ok", {"key": dest})
    audit(request_id, "upsert", "ok", {"document_id": str(doc_id), "chunks": len(texts)}, document_id=doc_id)
    set_request(request_id, last_ok_step="upsert")

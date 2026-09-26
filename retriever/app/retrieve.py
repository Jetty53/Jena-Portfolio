import re

from app.config import settings
from app.db import db, vector_literal

_TERM = re.compile(r"[A-Za-z0-9]{3,}")


def query_terms(text: str, limit: int = 8) -> list[str]:
    seen: list[str] = []
    for t in _TERM.findall(text or ""):
        low = t.lower()
        if low not in seen:
            seen.append(low)
        if len(seen) >= limit:
            break
    return seen


def cosine_search(embedding: list[float], k: int | None = None, source_type: str | None = None) -> list[dict]:
    top_k = k if k is not None else settings.retrieve_top_k
    lit = vector_literal(embedding)
    sql = """
        SELECT
            c.id::text AS chunk_id,
            d.id::text AS document_id,
            d.filename,
            c.source_type,
            c.chunk_index,
            c.heading_path,
            c.text,
            1 - (c.embedding <=> %s::vector) AS score
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE (%s::text IS NULL OR c.source_type = %s)
        ORDER BY c.embedding <=> %s::vector
        LIMIT %s
    """
    pool = max(top_k * 3, top_k)
    with db() as conn:
        rows = conn.execute(sql, (lit, source_type, source_type, lit, pool)).fetchall()
    return _rows(rows)


def keyword_search(query: str, k: int | None = None, source_type: str | None = None) -> list[dict]:
    terms = query_terms(query)
    if not terms:
        return []
    top_k = k if k is not None else settings.retrieve_top_k
    pool = max(top_k * 3, top_k)
    likes = [f"%{t}%" for t in terms]
    sql = """
        SELECT
            c.id::text AS chunk_id,
            d.id::text AS document_id,
            d.filename,
            c.source_type,
            c.chunk_index,
            c.heading_path,
            c.text,
            0.0 AS score
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE (%s::text IS NULL OR c.source_type = %s)
          AND (
            c.text ILIKE ANY(%s)
            OR d.filename ILIKE ANY(%s)
          )
        LIMIT %s
    """
    with db() as conn:
        rows = conn.execute(sql, (source_type, source_type, likes, likes, pool)).fetchall()
    hits = _rows(rows)
    for h in hits:
        blob = f"{h['filename']} {h['text']}".lower()
        hits_n = sum(1 for t in terms if t in blob)
        h["score"] = hits_n / len(terms)
    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits


def hybrid_search(
    embedding: list[float],
    query: str,
    k: int | None = None,
    source_type: str | None = None,
) -> list[dict]:
    top_k = k if k is not None else settings.retrieve_top_k
    vec = cosine_search(embedding, k=top_k, source_type=source_type)
    kw = keyword_search(query, k=top_k, source_type=source_type)
    return rrf_merge(vec, kw, k=top_k)


def rrf_merge(vec_hits: list[dict], kw_hits: list[dict], k: int, k_rrf: int = 60) -> list[dict]:
    merged: dict[str, dict] = {}
    for rank, h in enumerate(vec_hits, start=1):
        cid = h["chunk_id"]
        item = merged.setdefault(cid, {**h, "rrf": 0.0, "vscore": h.get("score", 0.0), "kscore": 0.0})
        item["rrf"] += 1.0 / (k_rrf + rank)
        item["vscore"] = float(h.get("score") or 0.0)
    for rank, h in enumerate(kw_hits, start=1):
        cid = h["chunk_id"]
        item = merged.setdefault(cid, {**h, "rrf": 0.0, "vscore": 0.0, "kscore": h.get("score", 0.0)})
        item["rrf"] += 1.0 / (k_rrf + rank)
        item["kscore"] = float(h.get("score") or 0.0)
        if not item.get("vscore"):
            item["vscore"] = 0.0
    ranked = sorted(merged.values(), key=lambda x: x["rrf"], reverse=True)
    out = []
    for h in ranked[:k]:
        row = dict(h)
        row["score"] = float(h.get("vscore") or h.get("kscore") or 0.0)
        out.append(row)
    return out


def grounded_hits(hits: list[dict]) -> list[dict]:
    return [h for h in hits if h["score"] >= settings.retrieve_min_score or h.get("kscore", 0) > 0]


def _rows(rows) -> list[dict]:
    hits = []
    for row in rows:
        item = dict(row)
        item["score"] = float(item["score"])
        hits.append(item)
    return hits

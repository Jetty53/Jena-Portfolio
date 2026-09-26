from app.config import settings
from app.gemini import embed_query
from app.generate import answer_from_hits, answer_from_hits_stream, judge_answer
from app.logutil import step
from app.retrieve import grounded_hits, hybrid_search
from app.rewrite import rewrite_standalone
from app.sessions import append_turn, ensure_session, is_uuid, load_history


def _hit_summary(hits: list[dict]) -> str:
    if not hits:
        return "0 hits"
    top = hits[0]
    return f"{len(hits)} hits  top={top['filename']} cosine={top['score']:.3f}"


def _sources(hits: list[dict]) -> list[dict]:
    return [
        {
            "filename": h["filename"],
            "chunk_index": h["chunk_index"],
            "score": round(h["score"], 4),
            "source_type": h["source_type"],
        }
        for h in hits
    ]


def _merge_history(session_id: str | None, history: list[dict] | None) -> tuple[str | None, list[dict]]:
    sid = session_id if session_id and is_uuid(session_id) else None
    if history:
        trimmed = [
            {"role": t.get("role") or "user", "content": (t.get("content") or "").strip()}
            for t in history
            if (t.get("content") or "").strip()
        ]
        return sid, trimmed[-settings.history_turns :]
    if sid:
        return sid, load_history(sid)
    return None, []


def retrieve_for_ask(
    question: str,
    source_type: str | None = None,
    history: list[dict] | None = None,
    session_id: str | None = None,
) -> dict:
    q = question.strip()
    if not q:
        raise ValueError("question is empty")

    sid, prior = _merge_history(session_id, history)
    if sid:
        sid = ensure_session(sid)
    elif prior:
        sid = ensure_session(None)

    used = rewrite_standalone(q, prior)
    if used != q:
        step("0/4 rewrite", used[:160])

    step("1/4 embed", used[:120])
    vec = embed_query(used)
    step("2/4 hybrid", f"top_k={settings.retrieve_top_k}")
    raw_hits = hybrid_search(vec, used, source_type=source_type)
    hits = grounded_hits(raw_hits)
    step("2/4 hybrid ok", _hit_summary(hits) if hits else f"0 grounded (raw={len(raw_hits)})")
    return {
        "question": q,
        "used": used,
        "corrected": used != q,
        "sid": sid,
        "hits": hits,
        "sources": _sources(hits),
    }


def _persist(sid: str | None, question: str, answer: str) -> None:
    if not sid:
        return
    try:
        append_turn(sid, "user", question)
        append_turn(sid, "assistant", answer)
    except Exception:
        step("session persist skipped", sid)


def ask(
    question: str,
    source_type: str | None = None,
    history: list[dict] | None = None,
    session_id: str | None = None,
) -> dict:
    ctx = retrieve_for_ask(question, source_type=source_type, history=history, session_id=session_id)
    used = ctx["used"]
    hits = ctx["hits"]
    last_answer = ""
    last_judge: dict = {}
    corrected = ctx["corrected"]

    for attempt in range(settings.max_query_rewrite + 1):
        step("3/4 generate", settings.gemini_generate_model)
        last_answer = answer_from_hits(used, hits)
        step("3/4 generate ok", f"chars={len(last_answer)}")
        step("4/4 judge", "apt?")
        last_judge = judge_answer(used, last_answer, hits)
        apt = last_judge.get("apt", True)
        rewrite = (last_judge.get("rewritten_question") or "").strip()
        step("4/4 judge ok", f"apt={apt}  {last_judge.get('reason', '')[:160]}")
        if apt or attempt >= settings.max_query_rewrite:
            break
        if not rewrite or rewrite.lower() == used.lower():
            break
        corrected = True
        used = rewrite
        step("4/4 rewrite", used[:160])
        vec = embed_query(used)
        raw_hits = hybrid_search(vec, used, source_type=source_type)
        hits = grounded_hits(raw_hits)
        ctx["sources"] = _sources(hits)

    _persist(ctx["sid"], ctx["question"], last_answer)
    return {
        "question": ctx["question"],
        "used_question": used,
        "corrected": corrected,
        "session_id": ctx["sid"],
        "answer": last_answer,
        "judge": last_judge,
        "sources": ctx["sources"],
        "trace": [],
    }


def iter_ask_stream(
    question: str,
    source_type: str | None = None,
    history: list[dict] | None = None,
    session_id: str | None = None,
):
    ctx = retrieve_for_ask(question, source_type=source_type, history=history, session_id=session_id)
    yield {
        "event": "meta",
        "data": {
            "session_id": ctx["sid"],
            "used_question": ctx["used"],
            "corrected": ctx["corrected"],
            "sources": ctx["sources"],
        },
    }
    step("3/4 generate stream", settings.gemini_generate_model)
    parts: list[str] = []
    for piece in answer_from_hits_stream(ctx["used"], ctx["hits"]):
        parts.append(piece)
        yield {"event": "token", "data": {"t": piece}}
    answer = "".join(parts).strip()
    _persist(ctx["sid"], ctx["question"], answer)
    yield {
        "event": "done",
        "data": {
            "session_id": ctx["sid"],
            "used_question": ctx["used"],
            "answer": answer,
            "sources": ctx["sources"],
        },
    }

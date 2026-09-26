from app.gemini import _delta_text
from app.pipeline import ask


def test_ask_rewrites_when_not_apt(monkeypatch):
    calls = {"embed": [], "search": 0, "answer": 0, "judge": 0}

    def fake_embed(q):
        calls["embed"].append(q)
        return [0.1] * 8

    def fake_search(vec, query=None, source_type=None, **_kwargs):
        calls["search"] += 1
        name = "Resume.pdf" if calls["search"] == 1 else "syzfjbzwjncs.pdf"
        return [
            {
                "filename": name,
                "chunk_index": 0,
                "score": 0.7,
                "source_type": "cv",
                "heading_path": None,
                "text": "sample",
            }
        ]

    def fake_grounded(hits):
        return hits

    def fake_answer(q, hits):
        calls["answer"] += 1
        return "vague" if calls["answer"] == 1 else "specific from kb"

    def fake_judge(q, answer, hits):
        calls["judge"] += 1
        if calls["judge"] == 1:
            return {"apt": False, "reason": "vague", "rewritten_question": "What skills are on Jeet Nath's resume?"}
        return {"apt": True, "reason": "ok", "rewritten_question": ""}

    monkeypatch.setattr("app.pipeline.embed_query", fake_embed)
    monkeypatch.setattr("app.pipeline.hybrid_search", fake_search)
    monkeypatch.setattr("app.pipeline.grounded_hits", fake_grounded)
    monkeypatch.setattr("app.pipeline.answer_from_hits", fake_answer)
    monkeypatch.setattr("app.pipeline.judge_answer", fake_judge)

    out = ask("what does he do")
    assert out["corrected"] is True
    assert out["used_question"].startswith("What skills")
    assert out["answer"] == "specific from kb"
    assert calls["search"] == 2
    assert calls["answer"] == 2


def test_iter_ask_stream_yields_meta_tokens_done(monkeypatch):
    monkeypatch.setattr(
        "app.pipeline.retrieve_for_ask",
        lambda *a, **k: {
            "question": "q",
            "used": "q",
            "corrected": False,
            "sid": None,
            "hits": [],
            "sources": [{"filename": "Resume.pdf", "chunk_index": 0, "score": 0.8, "source_type": "cv"}],
        },
    )
    monkeypatch.setattr("app.pipeline.answer_from_hits_stream", lambda *a, **k: iter(["Hel", "lo"]))
    monkeypatch.setattr("app.pipeline._persist", lambda *a, **k: None)
    from app.pipeline import iter_ask_stream

    events = list(iter_ask_stream("q"))
    names = [e["event"] for e in events]
    assert names == ["meta", "token", "token", "done"]
    assert events[-1]["data"]["answer"] == "Hello"
    assert events[0]["data"]["sources"][0]["filename"] == "Resume.pdf"
    seen = [""]
    assert _delta_text({"candidates": [{"content": {"parts": [{"text": "Hel"}]}}]}, seen) == "Hel"
    assert _delta_text({"candidates": [{"content": {"parts": [{"text": "Hello"}]}}]}, seen) == "lo"

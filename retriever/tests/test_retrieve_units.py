from app.generate import format_context
from app.gemini import parse_json_object
from app.retrieve import grounded_hits, query_terms, rrf_merge
from app.rewrite import needs_conversation_rewrite


def test_parse_json_object_fence():
    obj = parse_json_object('```json\n{"apt": false, "rewritten_question": "skills?"}\n```')
    assert obj["apt"] is False
    assert obj["rewritten_question"] == "skills?"


def test_format_context_empty():
    assert "no chunks" in format_context([])


def test_format_context_includes_score():
    text = format_context(
        [
            {
                "filename": "Resume.pdf",
                "heading_path": None,
                "score": 0.81,
                "text": "Python RAG",
            }
        ]
    )
    assert "Resume.pdf" in text
    assert "0.810" in text
    assert "Python RAG" in text


def test_grounded_hits_filters(monkeypatch):
    from app import retrieve as retrieve_mod

    monkeypatch.setattr(retrieve_mod.settings, "retrieve_min_score", 0.5)
    hits = [
        {"score": 0.9, "filename": "a"},
        {"score": 0.2, "filename": "b"},
    ]
    kept = grounded_hits(hits)
    assert [h["filename"] for h in kept] == ["a"]


def test_query_terms():
    assert "jake" in query_terms("Where did Jake Ryan go?")


def test_rrf_prefers_overlap():
    vec = [{"chunk_id": "1", "filename": "a", "chunk_index": 0, "source_type": "cv", "score": 0.9, "text": "x"}]
    kw = [{"chunk_id": "1", "filename": "a", "chunk_index": 0, "source_type": "cv", "score": 1.0, "text": "x"}]
    out = rrf_merge(vec, kw, k=5)
    assert out[0]["chunk_id"] == "1"


def test_rewrite_needed_only_with_history():
    assert needs_conversation_rewrite("what are his hobbies?", [{"role": "user", "content": "Jake Ryan"}])
    assert not needs_conversation_rewrite("what are his hobbies?", [])
    assert not needs_conversation_rewrite("Where did Jake Ryan go to college?", [{"role": "user", "content": "hi"}])

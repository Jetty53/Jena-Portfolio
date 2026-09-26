from app.config import settings
from app.gemini import generate_text, generate_text_stream, parse_json_object

ANSWER_PROMPT = """Answer ONLY from CONTEXT. Use complete sentences. Plain text, no markdown.
Cite each fact with the source filename in parentheses, e.g. (syzfjbzwjncs.pdf).
If CONTEXT does not contain the answer, say it is not in the knowledge base.

QUESTION:
{question}

CONTEXT:
{context}

ANSWER:"""

JUDGE_PROMPT = """JSON only: {{"apt": true, "reason": "short", "rewritten_question": ""}}
apt=false if vague, wrong person, or a sharper standalone query would retrieve better.

QUESTION: {question}
CONTEXT: {context}
ANSWER: {answer}
"""


def format_context(hits: list[dict]) -> str:
    if not hits:
        return "(no chunks above similarity threshold)"
    blocks = []
    for i, h in enumerate(hits, start=1):
        heading = f" / {h['heading_path']}" if h.get("heading_path") else ""
        blocks.append(
            f"[{i}] {h['filename']}{heading} (score={h['score']:.3f})\n{h['text']}"
        )
    return "\n\n".join(blocks)


def answer_prompt(question: str, hits: list[dict]) -> str:
    return ANSWER_PROMPT.format(question=question, context=format_context(hits))


def answer_from_hits(question: str, hits: list[dict]) -> str:
    return generate_text(answer_prompt(question, hits), max_output_tokens=settings.answer_max_tokens)


def answer_from_hits_stream(question: str, hits: list[dict]):
    yield from generate_text_stream(answer_prompt(question, hits), max_output_tokens=settings.answer_max_tokens)


def judge_answer(question: str, answer: str, hits: list[dict]) -> dict:
    raw = generate_text(
        JUDGE_PROMPT.format(question=question, context=format_context(hits), answer=answer),
        temperature=0.0,
        max_output_tokens=settings.judge_max_tokens,
    )
    try:
        obj = parse_json_object(raw)
    except Exception:
        return {"apt": True, "reason": "judge parse failed; keep answer", "rewritten_question": ""}
    rewritten = str(obj.get("rewritten_question") or "").strip()
    return {
        "apt": bool(obj.get("apt")),
        "reason": str(obj.get("reason") or ""),
        "rewritten_question": rewritten,
    }

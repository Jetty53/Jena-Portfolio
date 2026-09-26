import re

from app.config import settings
from app.gemini import generate_text

_ANAPHORA = re.compile(
    r"\b(he|him|his|she|her|they|them|their|this|that|these|those)\b",
    re.I,
)

REWRITE_PROMPT = """Rewrite FOLLOW_UP into one standalone search question.
Resolve pronouns using HISTORY only. Do not add facts that were not asked.
Return the question text only.

HISTORY:
{history}

FOLLOW_UP:
{question}
"""


def needs_conversation_rewrite(question: str, history: list[dict]) -> bool:
    if not history:
        return False
    return bool(_ANAPHORA.search(question or ""))


def format_history(history: list[dict]) -> str:
    lines = []
    for turn in history[-settings.history_turns :]:
        role = turn.get("role") or "user"
        content = (turn.get("content") or "").strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines) if lines else "(none)"


def rewrite_standalone(question: str, history: list[dict]) -> str:
    q = question.strip()
    if not needs_conversation_rewrite(q, history):
        return q
    raw = generate_text(
        REWRITE_PROMPT.format(history=format_history(history), question=q),
        temperature=0.0,
        max_output_tokens=settings.rewrite_max_tokens,
    )
    out = (raw or "").strip().splitlines()[0].strip().strip('"')
    return out or q

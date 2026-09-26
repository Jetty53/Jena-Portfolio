import hashlib
import re
import uuid
from uuid import UUID


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def prefix_chunk(filename: str, source_type: str, text: str) -> str:
    return f"[file={filename} type={source_type}]\n{text}"


def chunk_id(document_id: UUID, index: int, version: str) -> UUID:
    raw = f"{document_id}:{index}:{version}".encode()
    return uuid.uuid5(uuid.NAMESPACE_URL, hashlib.sha256(raw).hexdigest())


_SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    parts = _SENTENCE.split(cleaned)
    return [p.strip() for p in parts if p.strip()]


def cosine(a: list[float], b: list[float]) -> float:
    num = sum(x * y for x, y in zip(a, b, strict=True))
    da = sum(x * x for x in a) ** 0.5
    db = sum(y * y for y in b) ** 0.5
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)

import json
import re
import time

import httpx

from app.config import settings

BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiError(Exception):
    pass


def _headers() -> dict:
    return {"Content-Type": "application/json", "X-goog-api-key": settings.gemini_api_key}


def _post(url: str, payload: dict, attempts: int = 4) -> dict:
    delay = 1.0
    last: Exception | None = None
    for _ in range(attempts):
        try:
            r = httpx.post(url, headers=_headers(), json=payload, timeout=120.0)
            if r.status_code == 429 or r.status_code >= 500:
                last = GeminiError(f"{r.status_code} {r.text[:300]}")
                time.sleep(delay)
                delay *= 2
                continue
            if r.status_code >= 400:
                raise GeminiError(f"{r.status_code} {r.text[:500]}")
            return r.json()
        except httpx.HTTPError as e:
            last = e
            time.sleep(delay)
            delay *= 2
    raise GeminiError(str(last))


def embed_query(text: str) -> list[float]:
    model = settings.gemini_embed_model
    payload = {
        "requests": [
            {
                "model": f"models/{model}",
                "content": {"parts": [{"text": text[:8000]}]},
                "taskType": "RETRIEVAL_QUERY",
                "outputDimensionality": settings.embed_dim,
            }
        ]
    }
    data = _post(f"{BASE}/{model}:batchEmbedContents", payload)
    embeddings = data.get("embeddings") or []
    if len(embeddings) != 1:
        raise GeminiError("expected one query embedding")
    values = embeddings[0].get("values") or (embeddings[0].get("embedding") or {}).get("values")
    if not values or len(values) != settings.embed_dim:
        raise GeminiError("unexpected embedding dimension")
    return values


def generate_text(prompt: str, temperature: float = 0.2, max_output_tokens: int | None = None) -> str:
    cap = max_output_tokens if max_output_tokens is not None else settings.answer_max_tokens
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": cap},
    }
    data = _post(f"{BASE}/{settings.gemini_generate_model}:generateContent", payload)
    parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
    return "\n".join(p.get("text", "") for p in parts).strip()


def _delta_text(data: dict, seen: list[str]) -> str:
    parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
    text = "".join(p.get("text", "") for p in parts)
    if not text:
        return ""
    prev = seen[0]
    if text.startswith(prev):
        piece = text[len(prev) :]
        seen[0] = text
        return piece
    seen[0] = prev + text
    return text


def generate_text_stream(prompt: str, temperature: float = 0.2, max_output_tokens: int | None = None):
    cap = max_output_tokens if max_output_tokens is not None else settings.answer_max_tokens
    url = f"{BASE}/{settings.gemini_generate_model}:streamGenerateContent?alt=sse"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": cap},
    }
    seen = [""]
    with httpx.Client(timeout=120.0) as client:
        with client.stream("POST", url, headers=_headers(), json=payload) as r:
            if r.status_code >= 400:
                raise GeminiError(f"{r.status_code} {r.read()[:500]}")
            for line in r.iter_lines():
                if not line:
                    continue
                if line.startswith("data:"):
                    raw = line[5:].strip()
                    if not raw or raw == "[DONE]":
                        continue
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    piece = _delta_text(data, seen)
                    if piece:
                        yield piece



_JSON_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.I)


def parse_json_object(text: str) -> dict:
    raw = (text or "").strip()
    if not raw:
        raise ValueError("empty json")
    m = _JSON_FENCE.search(raw)
    if m:
        raw = m.group(1).strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no json object")
    obj = json.loads(raw[start : end + 1])
    if not isinstance(obj, dict):
        raise ValueError("json is not an object")
    return obj

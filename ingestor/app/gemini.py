import base64
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


def embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    if not texts:
        return []
    model = settings.gemini_embed_model
    out: list[list[float]] = []
    batch_size = 20
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        requests = [
            {
                "model": f"models/{model}",
                "content": {"parts": [{"text": t[:8000]}]},
                "taskType": task_type,
                "outputDimensionality": settings.embed_dim,
            }
            for t in batch
        ]
        data = _post(f"{BASE}/{model}:batchEmbedContents", {"requests": requests})
        embeddings = data.get("embeddings") or []
        if len(embeddings) != len(batch):
            raise GeminiError("embedding batch size mismatch")
        for item in embeddings:
            values = item.get("values") or (item.get("embedding") or {}).get("values")
            if not values or len(values) != settings.embed_dim:
                raise GeminiError("unexpected embedding dimension")
            out.append(values)
    return out


def vision_extract_text(image_bytes: bytes, mime: str) -> str:
    b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Extract all readable text from this image. Return plain text only, no markdown.",
                    },
                    {"inlineData": {"mimeType": mime, "data": b64}},
                ]
            }
        ]
    }
    data = _post(f"{BASE}/{settings.gemini_vision_model}:generateContent", payload)
    parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
    return "\n".join(p.get("text", "") for p in parts).strip()

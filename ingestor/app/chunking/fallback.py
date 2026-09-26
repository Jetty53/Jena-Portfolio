from app.chunking.util import estimate_tokens, split_sentences


def fallback_chunks(text: str, max_tokens: int = 512, overlap_tokens: int = 64) -> list[str]:
    sentences = split_sentences(text) or ([text.strip()] if text.strip() else [])
    chunks: list[str] = []
    buf: list[str] = []
    tokens = 0
    for sent in sentences:
        t = estimate_tokens(sent)
        if buf and tokens + t > max_tokens:
            chunks.append(" ".join(buf))
            keep: list[str] = []
            kt = 0
            for s in reversed(buf):
                st = estimate_tokens(s)
                if kt + st > overlap_tokens:
                    break
                keep.append(s)
                kt += st
            buf = list(reversed(keep)) + [sent]
            tokens = sum(estimate_tokens(s) for s in buf)
        else:
            buf.append(sent)
            tokens += t
    if buf:
        chunks.append(" ".join(buf))
    return chunks

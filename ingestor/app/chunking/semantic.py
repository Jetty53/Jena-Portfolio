from app.chunking.fallback import fallback_chunks
from app.chunking.util import cosine, estimate_tokens, split_sentences
from app.config import settings
from app.gemini import GeminiError, embed_texts


def semantic_chunks(text: str) -> tuple[list[str], str]:
    sentences = split_sentences(text)
    if not sentences:
        return [], settings.chunker_version
    if len(sentences) == 1:
        return sentences, settings.chunker_version

    try:
        vectors = embed_texts(sentences, task_type="RETRIEVAL_DOCUMENT")
    except GeminiError:
        return fallback_chunks(text, settings.chunk_max_tokens), "fallback-overlap-v1"

    chunks: list[str] = []
    buf = [sentences[0]]
    last_vec = vectors[0]
    tok = estimate_tokens(sentences[0])

    for sent, vec in zip(sentences[1:], vectors[1:], strict=True):
        st = estimate_tokens(sent)
        sim = cosine(last_vec, vec)
        if tok + st > settings.chunk_max_tokens or (tok >= settings.chunk_min_tokens and sim < settings.semantic_sim_threshold):
            chunks.append(" ".join(buf))
            buf = [sent]
            tok = st
        else:
            buf.append(sent)
            tok += st
        last_vec = vec

    if buf:
        chunks.append(" ".join(buf))
    return chunks, settings.chunker_version

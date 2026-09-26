from app.chunking.fallback import fallback_chunks
from app.chunking.util import cosine, prefix_chunk, sha256_bytes
from app.parsers.detect import UnsupportedFile, sniff


def test_sha256_stable():
    assert sha256_bytes(b"abc") == sha256_bytes(b"abc")
    assert sha256_bytes(b"abc") != sha256_bytes(b"abd")


def test_sniff_pdf():
    ext, mime = sniff("cv.pdf", b"%PDF-1.7 junk")
    assert ext == ".pdf"
    assert "pdf" in mime


def test_sniff_png():
    ext, _ = sniff("shot.png", b"\x89PNG\r\n\x1a\nxxxx")
    assert ext == ".png"


def test_sniff_rejects_exe():
    try:
        sniff("x.exe", b"MZ\x90\x00")
        assert False
    except UnsupportedFile:
        pass


def test_fallback_chunks_split():
    text = "Hello world. " * 80
    chunks = fallback_chunks(text, max_tokens=40, overlap_tokens=8)
    assert len(chunks) >= 2
    assert all(chunks)


def test_cosine_self():
    v = [1.0, 0.0, 0.0]
    assert abs(cosine(v, v) - 1.0) < 1e-9


def test_prefix_chunk():
    out = prefix_chunk("Resume.pdf", "cv", "John Doe")
    assert out.startswith("[file=Resume.pdf type=cv]")
    assert "John Doe" in out

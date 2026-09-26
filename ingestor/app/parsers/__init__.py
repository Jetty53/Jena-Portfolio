from app.parsers.detect import sniff
from app.parsers.types import ParsedDoc


def parse_file(path, filename: str, data: bytes) -> ParsedDoc:
    from pathlib import Path

    from app.parsers.docx import parse_docx
    from app.parsers.image import parse_image
    from app.parsers.pdf import parse_pdf

    ext, mime = sniff(filename, data)
    loc = Path(path)
    if ext == ".pdf":
        return parse_pdf(loc)
    if ext == ".docx":
        return parse_docx(loc)
    if ext in {".jpg", ".png"}:
        return parse_image(loc, mime)
    raise ValueError(f"no parser for {ext}")

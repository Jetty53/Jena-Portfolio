from pathlib import Path

import fitz

from app.gemini import vision_extract_text
from app.parsers.types import ParsedDoc

MIN_CHARS_PER_PAGE = 40


def parse_pdf(path: Path) -> ParsedDoc:
    doc = fitz.open(path)
    pages: list[str] = []
    used_vision = False
    try:
        for i, page in enumerate(doc):
            text = page.get_text("text") or ""
            if len(text.strip()) < MIN_CHARS_PER_PAGE:
                pix = page.get_pixmap(dpi=140)
                png = pix.tobytes("png")
                text = vision_extract_text(png, "image/png")
                used_vision = True
            pages.append(text.strip())
    finally:
        doc.close()
    joined = "\n\n".join(p for p in pages if p)
    parser = "pymupdf+vision" if used_vision else "pymupdf"
    return ParsedDoc(text=joined, parser=parser, page_count=len(pages), extra={"pages": len(pages)})

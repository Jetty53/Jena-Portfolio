from pathlib import Path

from docx import Document

from app.parsers.types import ParsedDoc


def parse_docx(path: Path) -> ParsedDoc:
    document = Document(str(path))
    parts: list[str] = []
    for p in document.paragraphs:
        if p.text.strip():
            parts.append(p.text.strip())
    for table in document.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells if c.text.strip()]
            if cells:
                parts.append(" | ".join(cells))
    return ParsedDoc(text="\n".join(parts), parser="python-docx")

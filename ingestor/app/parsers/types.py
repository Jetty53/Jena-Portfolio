from dataclasses import dataclass


@dataclass
class ParsedDoc:
    text: str
    parser: str
    page_count: int | None = None
    extra: dict | None = None

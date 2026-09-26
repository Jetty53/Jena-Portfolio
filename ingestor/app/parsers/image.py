from pathlib import Path

from PIL import Image

from app.gemini import vision_extract_text
from app.parsers.types import ParsedDoc


def parse_image(path: Path, mime: str) -> ParsedDoc:
    Image.open(path).verify()
    data = path.read_bytes()
    text = vision_extract_text(data, mime)
    return ParsedDoc(text=text, parser="gemini-vision")

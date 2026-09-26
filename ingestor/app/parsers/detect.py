from pathlib import Path

ALLOWED = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}

MAGIC = {
    b"%PDF": ".pdf",
    b"\x89PNG": ".png",
    b"\xff\xd8\xff": ".jpg",
    b"PK\x03\x04": ".docx",  # zip; docx confirmed by name
}


class UnsupportedFile(Exception):
    pass


def sniff(filename: str, data: bytes) -> tuple[str, str]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".jpeg":
        suffix = ".jpg"

    head = data[:8]
    magic_ext = None
    for sig, ext in MAGIC.items():
        if head.startswith(sig):
            magic_ext = ext
            break

    if suffix not in ALLOWED:
        if magic_ext in ALLOWED and magic_ext != ".docx":
            suffix = magic_ext
        else:
            raise UnsupportedFile(f"unsupported type: {filename}")

    if magic_ext and magic_ext != ".docx" and suffix in {".pdf", ".png", ".jpg"} and magic_ext != suffix:
        raise UnsupportedFile(f"extension {suffix} does not match file bytes")

    return suffix, ALLOWED[suffix]

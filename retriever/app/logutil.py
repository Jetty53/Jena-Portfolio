import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

log = logging.getLogger("retriever")


def step(name: str, detail: str = "") -> None:
    extra = f" — {detail}" if detail else ""
    log.info("%s%s", name, extra)

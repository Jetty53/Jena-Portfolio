import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

log = logging.getLogger("ingestor")


def step(request_id, name: str, detail: str = "") -> None:
    extra = f" — {detail}" if detail else ""
    log.info("request=%s  |  %s%s", request_id, name, extra)

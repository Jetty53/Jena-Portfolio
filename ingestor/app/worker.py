import asyncio
from uuid import UUID

from app.logutil import step as log_step
from app.pipeline import ingest_files
from app.store import audit, set_request

_queue: asyncio.Queue | None = None


def queue() -> asyncio.Queue:
    global _queue
    if _queue is None:
        _queue = asyncio.Queue()
    return _queue


async def worker() -> None:
    q = queue()
    log_step("-", "worker ready", "async ingest queue")
    while True:
        item = await q.get()
        request_id: UUID = item["request_id"]
        log_step(str(request_id), "worker picked job", item.get("source_type", ""))
        try:
            await asyncio.to_thread(
                ingest_files,
                request_id,
                item["source_type"],
                item["files"],
            )
        except Exception as e:
            log_step(str(request_id), "worker crash", str(e))
            try:
                set_request(request_id, status="failed", error=str(e), finished_at=True)
                audit(request_id, "pipeline", "failed", {"error": str(e)})
            except Exception:
                pass
        finally:
            q.task_done()

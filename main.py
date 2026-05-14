import logging
import os
import threading
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI

from aivtuber import run_aivtuber, stop_aivtuber

logger = logging.getLogger(__name__)

_runner_thread: Optional[threading.Thread] = None


def _run_aivtuber_in_thread(stop_event: threading.Event) -> None:
    try:
        run_aivtuber(stop_event=stop_event)
    except Exception:
        logger.exception("aivtuber loop failed")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global _runner_thread

    if not os.getenv("YOUTUBE_VIDEO_ID", ""):
        raise RuntimeError("YOUTUBE_VIDEO_ID が未設定です。")

    runner_stop = threading.Event()
    _runner_thread = threading.Thread(
        target=_run_aivtuber_in_thread,
        args=(runner_stop,),
        daemon=False,
        name="aivtuber-loop",
    )
    _runner_thread.start()
    yield
    runner_stop.set()
    stop_aivtuber()
    if _runner_thread is not None:
        _runner_thread.join(timeout=60.0)


app = FastAPI(title="aivtuber-base", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )

import asyncio
import logging
import os

from pytapo import Tapo

logger = logging.getLogger(__name__)

_camera: Tapo | None = None


def _connect() -> Tapo:
    global _camera
    _camera = Tapo(
        host=os.environ["CAMERA_IP"],
        user=os.environ["CAMERA_USER"],
        password=os.environ["CAMERA_PASSWORD"],
        printDebugInformation=False,
        printWarnInformation=False,
    )
    return _camera


def _get_events_sync() -> list[dict]:
    global _camera
    if _camera is None:
        _connect()
    try:
        return _camera.getEvents()
    except Exception:
        logger.warning("pytapo call failed, reconnecting")
        _connect()
        return _camera.getEvents()


async def get_events() -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_events_sync)

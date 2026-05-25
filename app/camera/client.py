import asyncio
import logging
import os

from pytapo import Tapo

logger = logging.getLogger(__name__)

_camera: Tapo | None = None
_lock = asyncio.Lock()

PTZ_STEP = 10  # degrees per d-pad press


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


def _move_sync(direction: str) -> None:
    global _camera
    if _camera is None:
        _connect()
    try:
        _do_move(direction)
    except Exception:
        logger.warning("PTZ call failed, reconnecting")
        _connect()
        _do_move(direction)


def _do_move(direction: str) -> None:
    if direction == "home":
        _camera.calibrateMotor()
    elif direction == "up":
        _camera.moveMotor(0, PTZ_STEP)
    elif direction == "down":
        _camera.moveMotor(0, -PTZ_STEP)
    elif direction == "left":
        _camera.moveMotor(-PTZ_STEP, 0)
    elif direction == "right":
        _camera.moveMotor(PTZ_STEP, 0)


async def get_events() -> list[dict]:
    async with _lock:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_events_sync)


async def move(direction: str) -> None:
    async with _lock:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _move_sync, direction)

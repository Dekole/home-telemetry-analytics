import asyncio
import json
import logging
from datetime import datetime, timezone

import db
from camera.client import get_events

logger = logging.getLogger(__name__)

DEVICE_ID = "tcb72-01"
POLL_INTERVAL = 10

_seen_start_times: set[int] = set()


async def _load_seen_from_db() -> None:
    pool = db.get_pool()
    rows = await pool.fetch(
        "SELECT details->>'start_time' AS st FROM events WHERE device_id = $1",
        DEVICE_ID,
    )
    for row in rows:
        if row["st"] is not None:
            try:
                _seen_start_times.add(int(row["st"]))
            except (ValueError, TypeError):
                pass
    logger.info("Loaded %d known event start_times from DB", len(_seen_start_times))


_ALARM_TYPE_MAP = [
    (16, "pet"),
    (8,  "vehicle"),
    (4,  "person"),
    (2,  "motion"),
]

def _classify(alarm_type: int) -> str:
    for bit, name in _ALARM_TYPE_MAP:
        if alarm_type & bit:
            return name
    return "motion"


async def _write_event(start_time: int, raw: dict) -> None:
    pool = db.get_pool()
    ts = datetime.fromtimestamp(start_time, tz=timezone.utc)
    event_type = _classify(raw.get("alarm_type", 2))
    await pool.execute(
        "INSERT INTO events (timestamp, device_id, event_type, details) VALUES ($1, $2, $3, $4::jsonb)",
        ts,
        DEVICE_ID,
        event_type,
        json.dumps(raw),
    )


async def run_collector() -> None:
    await _load_seen_from_db()
    logger.info("Event collector started, polling every %ds", POLL_INTERVAL)
    while True:
        try:
            events = await get_events()
            new_count = 0
            for event in events:
                st = event.get("start_time")
                if st is None or st in _seen_start_times:
                    continue
                await _write_event(st, event)
                _seen_start_times.add(st)
                new_count += 1
            if new_count:
                logger.info("Wrote %d new event(s)", new_count)
        except Exception:
            logger.exception("Collector poll failed")
        await asyncio.sleep(POLL_INTERVAL)

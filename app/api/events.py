import json

from fastapi import APIRouter, Query

import db
from models import Event, EventsResponse

router = APIRouter()


@router.get("/events", response_model=EventsResponse)
async def get_events(
    type: str = Query(default="all"),
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    pool = db.get_pool()
    where = "" if type == "all" else "WHERE event_type = $1"
    type_arg = [] if type == "all" else [type]

    if type == "all":
        rows = await pool.fetch(
            f"SELECT * FROM events ORDER BY timestamp DESC LIMIT $1 OFFSET $2",
            limit, offset,
        )
        total = await pool.fetchval("SELECT COUNT(*) FROM events")
    else:
        rows = await pool.fetch(
            "SELECT * FROM events WHERE event_type = $1 ORDER BY timestamp DESC LIMIT $2 OFFSET $3",
            type, limit, offset,
        )
        total = await pool.fetchval(
            "SELECT COUNT(*) FROM events WHERE event_type = $1", type
        )

    events = []
    for row in rows:
        d = dict(row)
        if isinstance(d.get("details"), str):
            d["details"] = json.loads(d["details"])
        events.append(Event(**d))
    return EventsResponse(events=events, total=total)

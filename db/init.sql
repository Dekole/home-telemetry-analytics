-- home-telemetry-analytics schema
-- Run automatically by postgres:15 on first container start

CREATE TABLE IF NOT EXISTS events (
    event_id    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    device_id   TEXT        NOT NULL,
    event_type  TEXT        NOT NULL,
    details     JSONB
);

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_type      ON events (event_type);

-- D42: serialize per-room event sequence allocation across workers.
CREATE TABLE IF NOT EXISTS room_event_counters (
    room_id TEXT PRIMARY KEY REFERENCES rooms(room_id) ON DELETE CASCADE,
    next_sequence BIGINT NOT NULL CHECK (next_sequence > 0)
);


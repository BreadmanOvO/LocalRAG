-- D42: serialize per-room event sequence allocation across workers.
CREATE TABLE IF NOT EXISTS room_event_counters (
    room_id TEXT PRIMARY KEY REFERENCES rooms(room_id) ON DELETE CASCADE,
    next_sequence BIGINT NOT NULL CHECK (next_sequence > 0)
);

INSERT INTO room_event_counters(room_id, next_sequence)
SELECT rooms.room_id, COALESCE(MAX(run_events.room_sequence), 0) + 1
FROM rooms
LEFT JOIN run_events ON run_events.room_id = rooms.room_id
GROUP BY rooms.room_id
ON CONFLICT (room_id) DO UPDATE
SET next_sequence = GREATEST(room_event_counters.next_sequence, EXCLUDED.next_sequence);

INSERT INTO runtime_schema_migrations(version, name)
VALUES (3, 'room_event_counters') ON CONFLICT (version) DO NOTHING;

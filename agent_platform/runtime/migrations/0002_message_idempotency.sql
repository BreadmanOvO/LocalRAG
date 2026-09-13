-- Apply after 0001_initial.sql, including on existing D05 databases.
BEGIN;
ALTER TABLE messages ADD COLUMN IF NOT EXISTS idempotency_key TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS messages_room_idempotency_key
    ON messages(room_id, idempotency_key)
    WHERE idempotency_key IS NOT NULL;
INSERT INTO runtime_schema_migrations(version, name)
VALUES (2, 'message_idempotency') ON CONFLICT (version) DO NOTHING;
COMMIT;

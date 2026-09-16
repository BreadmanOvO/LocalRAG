-- Room ownership and secret-free model snapshots for recoverable execution.
CREATE TABLE IF NOT EXISTS runtime_room_leases (
    room_id VARCHAR(255) PRIMARY KEY,
    owner VARCHAR(255) NOT NULL,
    expires_at DOUBLE PRECISION NOT NULL,
    bindings JSONB NOT NULL DEFAULT '[]'::jsonb
);

INSERT INTO runtime_schema_migrations(version, name)
VALUES (6, 'room_leases') ON CONFLICT (version) DO NOTHING;

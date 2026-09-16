-- Align databases created by early v1.8 migrations with SqlAlchemyEventStore.
ALTER TABLE run_events ADD COLUMN IF NOT EXISTS usage JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE run_events ADD COLUMN IF NOT EXISTS timestamp TEXT NOT NULL DEFAULT '';

INSERT INTO runtime_schema_migrations(version, name)
VALUES (4, 'event_payload_compatibility') ON CONFLICT (version) DO NOTHING;

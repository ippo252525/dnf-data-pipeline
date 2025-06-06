CREATE TABLE IF NOT EXISTS character (
    id SERIAL PRIMARY KEY,
    character_id CHAR(32) NOT NULL,
    server_id VARCHAR(8) NOT NULL,
    character_name VARCHAR(16) NOT NULL,
    level SMALLINT NOT NULL,
    job_name VARCHAR(16) NOT NULL,
    job_grow_name VARCHAR(16) NOT NULL,
    fame INTEGER NOT NULL,
    adventure_name VARCHAR(16),
    guild_id CHAR(32),
    guild_name VARCHAR(16),
    fetched_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (character_id, server_id)
);
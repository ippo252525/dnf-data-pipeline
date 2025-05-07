CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(64) NOT NULL,
    server_id VARCHAR(32) NOT NULL,
    character_name VARCHAR(32) NOT NULL,
    level INTEGER NOT NULL,
    job_name VARCHAR(32) NOT NULL,
    job_grow_name VARCHAR(64) NOT NULL,
    fame INTEGER NOT NULL,
    adventure_name VARCHAR(32),
    guild_name VARCHAR(64),
    fetched_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (character_id, server_id)
);
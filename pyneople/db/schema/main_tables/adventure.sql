CREATE TABLE IF NOT EXISTS adventure (
    id SERIAL PRIMARY KEY,
    adventure_name VARCHAR(16),
    adventure_level SMALLINT,
    flag_reinforce
    fetched_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
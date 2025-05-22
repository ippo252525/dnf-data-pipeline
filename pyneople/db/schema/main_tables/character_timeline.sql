CREATE TABLE IF NOT EXISTS character_timeline (
    id SERIAL PRIMARY KEY,
    character_id CHAR(32) NOT NULL,
    server_id VARCHAR(8) NOT NULL,
    timeline_code SMALLINT,
    timeline_name TEXT,
    timeline_date TIMESTAMP WITH TIME ZONE,
    timeline_data JSONB,
    fetched_at TIMESTAMP WITH TIME ZONE NOT NULL
);
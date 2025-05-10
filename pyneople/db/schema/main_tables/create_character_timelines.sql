CREATE TABLE IF NOT EXISTS character_timelines (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(64) NOT NULL,
    server_id VARCHAR(32) NOT NULL,
    timeline_code INT NOT NULL,
    timeline_date TIMESTAMP WITH TIME ZONE NOT NULL,
    timeline_data JSONB ,
    fetched_at TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (character_id, server_id)
        REFERENCES characters(character_id, server_id)
        ON DELETE CASCADE
);
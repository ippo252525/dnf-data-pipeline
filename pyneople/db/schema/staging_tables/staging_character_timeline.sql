-- character_timelines 스테이징 테이블
CREATE TABLE IF NOT EXISTS staging_character_timeline (
    character_id CHAR(32) NOT NULL,
    server_id VARCHAR(8) NOT NULL,
    timeline_code SMALLINT,
    timeline_name TEXT,
    timeline_date TIMESTAMP WITH TIME ZONE,
    timeline_data JSONB,
    fetched_at TIMESTAMP WITH TIME ZONE NOT NULL
);
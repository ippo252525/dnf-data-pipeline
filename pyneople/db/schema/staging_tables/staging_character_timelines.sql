-- character_timelines 스테이징 테이블
CREATE TABLE staging_character_timelines (
    character_id VARCHAR(64) NOT NULL,
    server_id VARCHAR(32) NOT NULL,
    timeline_code INT NOT NULL,
    timeline_date TIMESTAMP WITH TIME ZONE NOT NULL,
    timeline_data JSONB NOT NULL,
    fetched_at TIMESTAMP WITH TIME ZONE NOT NULL
);
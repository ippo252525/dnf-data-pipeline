INSERT INTO character_timeline (
    character_id, server_id, timeline_code, timeline_date, timeline_data, fetched_at
)
SELECT
    character_id,
    server_id,
    timeline_code,
    timeline_date,
    CASE 
        WHEN timeline_data = 'null' THEN NULL
        ELSE timeline_data::jsonb
    END,
    fetched_at
FROM staging_character_timeline;
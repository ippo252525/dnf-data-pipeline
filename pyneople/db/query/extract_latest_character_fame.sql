SELECT DISTINCT ON (character_id, server_id)
    character_id,
    server_id,
    character_name,
    level,
    job_name,
    job_grow_name,
    fame
FROM staging_character_fame
ORDER BY character_id, server_id, fetched_at DESC;
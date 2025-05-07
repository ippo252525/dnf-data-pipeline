WITH latest_staging AS (
    SELECT
        character_id,
        server_id,
        character_name,
        level,
        job_name,
        job_grow_name,
        fame,
        adventure_name,
        guild_name,
        fetched_at,
        is_active,
        ROW_NUMBER() OVER (PARTITION BY character_id, server_id ORDER BY fetched_at DESC) AS rn
    FROM
        staging_characters
)
INSERT INTO characters (
    character_id,
    server_id,
    character_name,
    level,
    job_name,
    job_grow_name,
    fame,
    adventure_name,
    guild_name,
    fetched_at,
    is_active
)
SELECT
    character_id,
    server_id,
    character_name,
    level,
    job_name,
    job_grow_name,
    fame,
    adventure_name,
    guild_name,
    fetched_at,
    is_active
FROM
    latest_staging
WHERE
    rn = 1
ON CONFLICT (character_id, server_id)
DO UPDATE SET
    character_name = EXCLUDED.character_name,
    level = EXCLUDED.level,
    job_name = EXCLUDED.job_name,
    job_grow_name = EXCLUDED.job_grow_name,
    fame = EXCLUDED.fame,
    adventure_name = EXCLUDED.adventure_name,
    guild_name = EXCLUDED.guild_name,
    fetched_at = EXCLUDED.fetched_at,
    is_active = EXCLUDED.is_active
WHERE
    characters.fetched_at < EXCLUDED.fetched_at;
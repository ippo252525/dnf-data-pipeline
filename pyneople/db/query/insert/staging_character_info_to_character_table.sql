-- 1. 최신 캐릭터 정보만 추출 (중복 제거)
WITH latest_staging AS (
    SELECT DISTINCT ON (character_id, server_id)
        character_id,
        server_id,
        character_name,
        level,
        job_name,
        job_grow_name,
        fame,
        adventure_name,
        guild_id,
        guild_name,
        fetched_at
    FROM staging_character_info
    ORDER BY character_id, server_id, fetched_at DESC
)
-- 2. UPSERT (is_active 기본값 TRUE 활용)
INSERT INTO character (
    character_id,
    server_id,
    character_name,
    level,
    job_name,
    job_grow_name,
    fame,
    adventure_name,
    guild_id,
    guild_name,    
    fetched_at
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
    guild_id,
    guild_name,    
    fetched_at
FROM latest_staging
ON CONFLICT (character_id, server_id) DO UPDATE
SET
    character_name = EXCLUDED.character_name,
    level = EXCLUDED.level,
    job_name = EXCLUDED.job_name,
    job_grow_name = EXCLUDED.job_grow_name,
    fame = EXCLUDED.fame,
    adventure_name = EXCLUDED.adventure_name,
    guild_id = EXCLUDED.guild_id,
    guild_name = EXCLUDED.guild_name,    
    fetched_at = EXCLUDED.fetched_at,
    is_active = TRUE  -- 재활성화용
WHERE
    character.character_name IS DISTINCT FROM EXCLUDED.character_name OR
    character.level IS DISTINCT FROM EXCLUDED.level OR
    character.job_name IS DISTINCT FROM EXCLUDED.job_name OR
    character.job_grow_name IS DISTINCT FROM EXCLUDED.job_grow_name OR
    character.fame IS DISTINCT FROM EXCLUDED.fame OR
    character.adventure_name IS DISTINCT FROM EXCLUDED.adventure_name OR
    character.guild_id IS DISTINCT FROM EXCLUDED.guild_id OR
    character.guild_name IS DISTINCT FROM EXCLUDED.guild_name OR
    character.fetched_at IS DISTINCT FROM EXCLUDED.fetched_at;
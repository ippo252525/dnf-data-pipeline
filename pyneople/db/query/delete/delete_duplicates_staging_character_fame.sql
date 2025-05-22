WITH duplicates AS (
  SELECT ctid
  FROM (
    SELECT 
      ctid,
      ROW_NUMBER() OVER (
        PARTITION BY server_id, character_id
        ORDER BY fetched_at DESC -- 또는 원하는 기준 (예: 최신 데이터 남기기)
      ) AS rn
    FROM staging_character_fame
  ) sub
  WHERE rn > 1
)
DELETE FROM staging_character_fame
WHERE ctid IN (SELECT ctid FROM duplicates);
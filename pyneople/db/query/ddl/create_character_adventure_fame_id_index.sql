-- 모험단 별 가장 명성이 높은 캐릭터를 조회하기 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_character_adventure_fame_id
ON character (adventure_name, fame DESC, id DESC, character_id, server_id)
WHERE is_active = true AND adventure_name IS NOT NULL;
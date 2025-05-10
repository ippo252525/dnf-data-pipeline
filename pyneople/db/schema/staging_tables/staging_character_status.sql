CREATE TABLE IF NOT EXISTS "staging_character_status" (
  "server_id" TEXT,
  "character_id" CHAR(32),
  "buff_adventure_level" INT,
  "status_physical_defense_rate_value" REAL,
  "status_magical_defense_rate_value" REAL,
  "status_strength_value" INT,
  "status_intelligence_value" INT,
  "status_vitality_value" INT,
  "status_spirit_value" INT,
  "status_final_cooldown_reduction_rate_value" REAL,
  "fetched_at" TIMESTAMP WITH TIME ZONE
);
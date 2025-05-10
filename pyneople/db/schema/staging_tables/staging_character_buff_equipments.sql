CREATE TABLE IF NOT EXISTS "staging_character_buff_equipments" (
  "server_id" TEXT,
  "character_id" CHAR(32),
  "buff_skill_info_name" TEXT,
  "buff_skill_info_option_level" INT,
  "equipment" INT,
  "fetched_at" TIMESTAMP WITH TIME ZONE
);
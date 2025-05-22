CREATE UNLOGGED TABLE IF NOT EXISTS "staging_character_creature" (
  "server_id" TEXT,
  "character_id" CHAR(32),
  "item_name" TEXT,
  "clone_item_name" TEXT,
  "artifact_red_item_name" TEXT,
  "artifact_red_item_available_level" INT,
  "artifact_red_item_rarity" TEXT,
  "artifact_blue_item_name" TEXT,
  "artifact_blue_item_available_level" INT,
  "artifact_blue_item_rarity" TEXT,
  "artifact_green_item_name" TEXT,
  "artifact_green_item_available_level" INT,
  "artifact_green_item_rarity" TEXT,
  "fetched_at" TIMESTAMP WITH TIME ZONE
);
CREATE UNLOGGED TABLE IF NOT EXISTS "staging_character_flag" (
  "server_id" TEXT,
  "character_id" CHAR(32),
  "item_rarity" TEXT,
  "reinforce" INT,
  "gems_0_item_rarity" TEXT,
  "gems_1_item_rarity" TEXT,
  "gems_2_item_rarity" TEXT,
  "gems_3_item_rarity" TEXT,
  "fetched_at" TIMESTAMP WITH TIME ZONE
);
CREATE TABLE IF NOT EXISTS character_creature (
  server_id VARCHAR(8),
  character_id CHAR(32),
  item_name TEXT,
  clone_item_name TEXT,
  artifact_red_item_name TEXT,
  artifact_red_item_available_level SMALLINT,
  artifact_red_item_rarity VARCHAR(4),
  artifact_blue_item_name TEXT,
  artifact_blue_item_available_level SMALLINT,
  artifact_blue_item_rarity VARCHAR(4),
  artifact_green_item_name TEXT,
  artifact_green_item_available_level SMALLINT,
  artifact_green_item_rarity VARCHAR(4),
  fetched_at TIMESTAMP WITH TIME ZONE,
  UNIQUE (character_id, server_id)
);
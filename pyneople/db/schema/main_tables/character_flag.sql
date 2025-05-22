CREATE TABLE IF NOT EXISTS character_flag (
  server_id VARCHAR(8),
  character_id CHAR(32),
  item_rarity VARCHAR(4),
  reinforce SMALLINT,
  gems_0_item_rarity VARCHAR(4),
  gems_1_item_rarity VARCHAR(4),
  gems_2_item_rarity VARCHAR(4),
  gems_3_item_rarity VARCHAR(4),
  fetched_at TIMESTAMP WITH TIME ZONE,
  UNIQUE (character_id, server_id)
);
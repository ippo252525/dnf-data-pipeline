CREATE TABLE IF NOT EXISTS character_buff_equipment (
  server_id VARCHAR(8),
  character_id CHAR(32),
  buff_skill_info_name TEXT,
  buff_skill_info_option_level SMALLINT,
  equipment SMALLINT,
  fetched_at TIMESTAMP WITH TIME ZONE,
  UNIQUE (character_id, server_id)
);
CREATE TABLE IF NOT EXISTS "staging_characters" (
  "server_id" TEXT,
  "character_id" CHAR(32),
  "character_name" TEXT,
  "level" INT,
  "job_name" TEXT,
  "job_grow_name" TEXT,
  "fame" INT,
  "adventure_name" TEXT,
  "guild_id" CHAR(32),
  "guild_name" TEXT,
  "fetched_at" TIMESTAMP WITH TIME ZONE
);
CREATE TABLE IF NOT EXISTS "staging_character_fame" (
  "server_id" TEXT,
  "character_id" CHAR(32),
  "character_name" TEXT,
  "level" INT,
  "job_name" TEXT,
  "job_grow_name" TEXT,
  "fame" INT,
  "fetched_at" TIMESTAMP WITH TIME ZONE
);
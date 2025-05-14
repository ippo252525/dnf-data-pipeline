CREATE TABLE IF NOT EXISTS character_fame_history
(
    snapshot_date     Date,
    server_id         LowCardinality(String),
    character_id      String,
    character_name    String,
    level             UInt8,
    job_name          LowCardinality(String),
    job_grow_name     LowCardinality(String),
    fame              UInt32
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(snapshot_date)
ORDER BY (snapshot_date, server_id, fame, character_id)
SETTINGS index_granularity = 8192;



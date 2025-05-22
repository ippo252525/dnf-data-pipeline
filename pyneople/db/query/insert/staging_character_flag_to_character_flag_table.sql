TRUNCATE TABLE character_flag;
INSERT INTO character_flag
SELECT * FROM staging_character_flag;
TRUNCATE TABLE character_creature;
INSERT INTO character_creature
SELECT * FROM staging_character_creature;
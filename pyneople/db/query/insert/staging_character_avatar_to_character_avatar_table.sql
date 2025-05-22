TRUNCATE TABLE character_avatar;
INSERT INTO character_avatar
SELECT * FROM staging_character_avatar;
SELECT 
DISTINCT ON (adventure_name) 
character_id, server_id
FROM character
WHERE adventure_name IS NOT null and is_active  = true 
ORDER BY adventure_name, fame, id desc;
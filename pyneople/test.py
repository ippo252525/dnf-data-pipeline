from pyneople.api_to_mongo import api_to_mongo
from pyneople.mongo_to_psql import mongo_to_psql

from pyneople.config.logger_config import setup_logging
import logging
setup_logging(logging.INFO)

sql = """
SELECT character_id, server_id 
FROM characters
LIMIT 1000;
"""
endpoints = ['character_equipment', 'character_avatar', 'character_status', 'character_creature']
CHARACTER_BASE_ENDPOINTS = [
    'character_info',
    'character_status',
    'character_equipment',
    'character_avatar',
    'character_creature',
    'character_flag',
    # 'character_talisman', 탈리스만은 2025년 6월경 캐릭터 스킬 개편에 따라 지원하지 않음
    # 'character_skill_style', 아직 미구현
    'character_buff_equipment',
    'character_buff_avatar',
    'character_buff_creature'
]

api_to_mongo(CHARACTER_BASE_ENDPOINTS, True, sql = sql)
mongo_to_psql(CHARACTER_BASE_ENDPOINTS,
              character_info_endpoints=['character_creature'],
              num_queue_to_psql_workers = 2,
              mongo_to_psql_pool_max_size=20)
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
endpoints = [
    'character_info',
    'character_timeline',
    'character_status',
    'character_equipment',
    'character_avatar',
    'character_creature',
    'character_flag',
    'character_buff_equipment'
]

api_to_mongo(endpoints, True, sql = sql)
mongo_to_psql(endpoints, ['character_equipment'],
              num_queue_to_psql_workers = 2,
              mongo_to_psql_pool_max_size=20)

# api_to_mongo(['character_fame'], True, max_fame = 200000)
# mongo_to_psql(['character_fame'],
#               num_queue_to_psql_workers = 10,
#               mongo_to_psql_pool_max_size=20)
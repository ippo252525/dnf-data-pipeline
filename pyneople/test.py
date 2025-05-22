from pyneople.api_to_mongo import api_to_mongo
from pyneople.mongo_to_psql import mongo_to_psql

from pyneople.config.logger_config import setup_logging
import logging
setup_logging(logging.INFO)

sql = """
SELECT character_id, server_id 
FROM character
LIMIT 1;
"""

endpoints = [
    'character_timeline'#,
    # 'character_status',
    # 'character_equipment',
    # 'character_avatar',
    # 'character_creature',
    # 'character_flag',
    # 'character_buff_equipment'
]

api_to_mongo(
    endpoints = endpoints, 
    mongo_collection_name='test',
    check_rate_limit= True, 
    rows = [('0845ca92e00e2ddc9044607d84da5bc4', 'anton')]
    # sql = sql
)
# mongo_to_psql(
#     endpoints = endpoints, 
#     character_info_endpoints=['character_equipment'],
#     num_queue_to_psql_workers = 10,
#     mongo_to_psql_pool_max_size=20
# )

# api_to_mongo(
#     endpoints=['character_fame'], 
#     mongo_collection_name='character_fame',
#     error_collection_name='character_fame_error',
#     check_rate_limit=True, 
#     max_fame = 1000000
# )
# mongo_to_psql(
#     endpoints=['character_fame'], 
#     mongo_collection_name='character_fame',
#     error_collection_name='character_fame_error',
#     num_queue_to_psql_workers = 10,
#     mongo_to_psql_pool_max_size=20
# )
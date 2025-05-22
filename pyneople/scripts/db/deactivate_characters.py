from pymongo import MongoClient
from pyneople.utils.db_utils.psql_connection import psql_connection
from pyneople.config.config import Settings
from psycopg2.extras import execute_values

import logging
logger = logging.getLogger(__name__)

def deactivate_characters(
        error_collection_name : str,
        target_table_name : str = 'character'
):
    """
    error_collection에 있는 데이터 중 404 error를 확인하고 해당 데이터를 character table에서 비활성화 시키는 함수
    Args:
        error_collection_name (str): MongoDB에서 사용할 에러 컬렉션 이름
        target_table_name (str): 비활성화 시킬 테이블 이름
    """    
    
    mongo_client = MongoClient(Settings.MONGO_URL)
    mongo_db = mongo_client[Settings.MONGO_DB_NAME]
    error_collection = mongo_db[error_collection_name]
    mongo_cur = error_collection.find({'error_data.error.code' : 'DNF001'})
    not_found_characters = [(error_data['api_request']['params']['characterId'], error_data['api_request']['params']['serverId']) for error_data in mongo_cur]
    if not not_found_characters:
        logger.info("404 Not Found Character Error 없음")
        return
    with psql_connection() as psql_conn:
        with psql_conn.cursor() as psql_cur:
            query = f"""
            UPDATE {target_table_name} AS c
            SET is_active = FALSE
            FROM (VALUES %s) AS vals(character_id, server_id)
            WHERE c.character_id = vals.character_id AND c.server_id = vals.server_id;
            """
            execute_values(psql_cur, query, not_found_characters)
            logger.info(f"404 Not Found Character Error {len(not_found_characters)}개 deactivate 완료")
    

    
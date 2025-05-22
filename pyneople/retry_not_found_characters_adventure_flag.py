from venv import logger
from pyneople.api_to_mongo import api_to_mongo
from pyneople.config.config import Settings
from pyneople.utils.db_utils.psql_connection import psql_connection
from pyneople.utils.monitoring import send_slack_alert_sync
from pymongo import MongoClient
import logging
logger = logging.getLogger(__name__)

def retry_not_found_characters_adventure_flag(error_collection_name: str, max_depth: int = 3, depth: int = 0):
    """
    404 Not Found Character Error 인 캐릭터의 모험단의 다른 캐릭터를 가지고 와서 다시 요청
    재귀적으로 최대 max_depth까지 반복
    """

    mongo_client = MongoClient(Settings.MONGO_URL)
    error_collection = mongo_client[Settings.MONGO_DB_NAME][error_collection_name]
    errors = list(error_collection.find({'error_data.error.code': 'DNF001'}))
    
    if depth >= max_depth:
        if errors:
            logger.error(f"Max retry depth reached with errors: {errors}")  
            raise Exception(f"Max retry depth reached with errors: {errors}")
        
    if not errors:
        logger.info("No errors found to retry.")
        return

    new_characters = []
    with psql_connection() as psql_conn:
        with psql_conn.cursor() as cur:
            for error in errors:
                api_request = error.get('api_request')
                character_id = api_request.get('params').get('character_id')
                server_id = api_request.get('params').get('server_id')
                sql = f"""
                    SELECT adventure_name
                    FROM character
                    WHERE character_id = %s AND server_id = %s;
                """
                cur.execute(sql, (character_id, server_id))
                result = cur.fetchone()
                if not result:
                    continue
                adventure_name = result[0]
                sql = f"""
                    SELECT character_id, server_id
                    FROM character
                    WHERE adventure_name = %s AND character_id != %s AND server_id = %s
                    AND is_active = True
                    ORDER BY fame DESC, id DESC
                    LIMIT 1;
                """
                cur.execute(sql, (adventure_name, character_id, server_id))
                new_result = cur.fetchone()
                if new_result:
                    new_characters.append(new_result)
    
    if not new_characters:
        print("No new characters found to retry.")
        return

    # 새로운 캐릭터 ID와 서버 ID를 사용하여 API 요청을 수행
    logger.info(f"Retrying with new characters: {len(new_characters)}")
    send_slack_alert_sync(f'404 Not Found Character Error 인 캐릭터의 모험단의 다른 캐릭터를 가지고 와서 다시 요청합니다. {len(new_characters)}개 캐릭터를 요청합니다.')
    api_to_mongo(
        endpoints=['adventure_flag'],
        check_rate_limit=True,
        num_api_fetch_workers=50,
        rows=new_characters,
        error_collection_name=error_collection_name
    )

    # 재귀 호출
    retry_not_found_characters_adventure_flag(error_collection_name, max_depth, depth + 1)
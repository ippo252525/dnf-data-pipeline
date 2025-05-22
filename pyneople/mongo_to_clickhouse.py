from pyneople.config.config import Settings
from pymongo import MongoClient
import clickhouse_connect
from datetime import date, datetime
from pyneople.metadata.metadata_constants import TIMELINE_CODE_TO_KEYS_MAP
from pyneople.metadata.metadata_generated import CLICKHOUSE_TABLE_COLUMNS_MAP
from pyneople.utils.common import to_snake_case

import logging
logger = logging.getLogger(__name__)

def _preprocess_character_timeline_clickhouse(data):
    """
    clickhouse 저장을 위한 단일 타임라인 데이터 전처리 함수
    """
    try:
        result = {'timeline_code' : data['code'], 'timeline_name' : data['name'], 'timeline_date' : datetime.strptime(data['date'], '%Y-%m-%d %H:%M')}
        if data.get('data'):
            for key in TIMELINE_CODE_TO_KEYS_MAP.get(data['code']):
            #     if key == 'ticket':
            #         value = data['data'].get(key, {}).get('itemName')
            #     elif key == 'resultItems':    
            #         value = data['data'].get(key)[0].get('itemName')
            #     else:    
                value = data['data'].get(key)
                if isinstance(value, (list, dict)):
                    if key in ['ticket', 'itemObtainInfo']:
                        value = value.get('itemName')
                    elif key == 'resultItems':
                        value = value[0].get('itemName')
                result[f'timeline_data_{to_snake_case(key)}'] = value    
            return result    
        else:
            return result
    except Exception as e:
        print(f"Error processing data: {data}, Error: {e}")
        print(f"Error processing data: {data.get('data')}, Error: {e}")
        raise

def mongo_to_clickhouse_timeline(
    snapshot_date: date,
    batch_size: int = 5000
):
    """
    MongoDB에서 ClickHouse로 데이터 이동
    """
    # MongoDB 연결
    mongo_client = MongoClient(Settings.MONGO_URL)
    db = mongo_client[Settings.MONGO_DB_NAME]
    collection = db[Settings.MONGO_COLLECTION_NAME]

    # ClickHouse 연결
    ch_client = clickhouse_connect.get_client(
        host=Settings.CLICK_HOUSE_HOST,
        port=Settings.CLICK_HOUSE_PORT,
        username=Settings.CLICK_HOUSE_USER_NAME,
        password=""
    )

    # 데이터 가져오기
    count = 0
    with mongo_client.start_session() as session:
        cursor = collection.find({}, no_cursor_timeout=True, batch_size=batch_size, session=session)
        batch = []

        # ClickHouse에 데이터 삽입
        for doc in cursor:
            doc = doc['data']
            character_id = doc['characterId']
            server_id = doc['serverId']
            doc = doc['timeline']['rows']
            doc = [{
                'server_id' : server_id,
                'character_id' : character_id,
                **_preprocess_character_timeline_clickhouse(timeline_data)
            } for timeline_data in doc]
            doc = [tuple(row.get(column) for column in CLICKHOUSE_TABLE_COLUMNS_MAP['character_timeline'][1:]) for row in doc]
            doc = [(snapshot_date, *row) for row in doc]
            batch += doc
            if len(batch) >= batch_size:
                ch_client.insert('character_timeline', batch, CLICKHOUSE_TABLE_COLUMNS_MAP['character_timeline'])
                logger.info(f"character_timeline : {count}번 batch 삽입 완료, batch size : {len(batch)}")
                count += 1
                batch = []
        if batch:
            ch_client.insert('character_timeline', batch, CLICKHOUSE_TABLE_COLUMNS_MAP['character_timeline'])
    
    logger.info("mongo_to_clickhouse 완료")
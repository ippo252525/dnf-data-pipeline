import clickhouse_connect
from pymongo import MongoClient
from typing import Callable
from pyneople.config.config import Settings
from pyneople.metadata.metadata_generated import CLICKHOUSE_TABLE_COLUMNS_MAP
from datetime import date
import logging
logger = logging.getLogger(__name__)
# import asyncio

def mongo_to_clickhouse_with_filter(
    filter : dict,
    clickhouse_table_name : str,
    snapshot_date : date,
    batch_size : int = 5000,
    preprocess : Callable = lambda x: x
    ):
    
    mongo_client = MongoClient(Settings.MONGO_URL)
    mongo_db = mongo_client[Settings.MONGO_DB_NAME]
    mongo_collection = mongo_db[Settings.MONGO_COLLECTION_NAME]
    
    ch_client = clickhouse_connect.get_client(
            host=Settings.CLICK_HOUSE_HOST,
            port=Settings.CLICK_HOUSE_PORT,
            username=Settings.CLICK_HOUSE_USER_NAME,
            password=""
        )
    
    try:
        with mongo_client.start_session() as session:
            mongo_cursor = mongo_collection.find(filter, no_cursor_timeout=True, batch_size=batch_size, session=session)
            count = 0
            batch = []
            for doc in mongo_cursor:
                doc = doc.get('data')
                doc = preprocess(doc, snapshot_date)
                
                if isinstance(doc, list):
                    batch.extend(doc)
                else:
                    batch.append(doc)            
                
                if len(batch) >= batch_size:
                    ch_client.insert('character_timeline', batch, CLICKHOUSE_TABLE_COLUMNS_MAP[clickhouse_table_name])
                    logger.info(f"character_timeline : {count}번 batch 삽입 완료, batch size : {len(batch)}")
                    count += 1
                    batch = []
            
            if batch:
                ch_client.insert('character_timeline', batch, CLICKHOUSE_TABLE_COLUMNS_MAP[clickhouse_table_name])
    finally:
        ch_client.close()
        mongo_client.close()            

# def mongo_to_clickhouse_with_filter(
#     filter : dict,
#     clickhouse_table_name : str,
#     batch_size : int = 5000,
#     preprocess : Callable = lambda x: x
# ):
#     asyncio.run(_mongo_to_clickhouse_with_filter(
#         filter=filter,
#         psql_table_name=clickhouse_table_name,
#         batch_size=batch_size,
#         preprocess=preprocess
#     ))
    
    
        
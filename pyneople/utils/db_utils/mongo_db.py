"""
MongoDB 조작에 필요한 유틸리티 함수
"""
from pyneople.config.config import Settings
from pymongo import MongoClient
import logging

# logging 설정
logger = logging.getLogger(__name__)

def drop_collection(collection_names: str | list[str] | None = None):
    """
    MongoDB에서 지정된 컬렉션을 삭제하는 함수
    
    Args:
        collection_names (str | list[str] | None): 삭제할 컬렉션의 이름, None인 경우 모든 컬렉션을 삭제
    """
    mongo_client = MongoClient(Settings.MONGO_URL)
    db = mongo_client[Settings.MONGO_DB_NAME]
    
    if isinstance(collection_names, str):
        collection_names = [collection_names]
    
    if collection_names is None:
        collection_names = db.list_collection_names()
        # system.으로 시작하는 컬렉션은 제외
        collection_names = [name for name in collection_names if not name.startswith("system.")]    

    for name in collection_names:
            db[name].drop()
            logger.info(f"Drop collection : '{name}')")
    mongo_client.close()            

def clear_collection(collection_names: str | list[str] | None = None):
    """
    MongoDB에서 지정된 컬렉션을 비우는 함수
    
    Args:
        collection_names (str | list[str] | None): 비울 컬렉션의 이름, None인 경우 모든 컬렉션을 비움
    """
    mongo_client = MongoClient(Settings.MONGO_URL)
    db = mongo_client[Settings.MONGO_DB_NAME]

    if isinstance(collection_names, str):
        collection_names = [collection_names]
    
    if collection_names is None:
        collection_names = db.list_collection_names()
        # system.으로 시작하는 컬렉션은 제외
        collection_names = [name for name in collection_names if not name.startswith("system.")]

    for name in collection_names:
        result = db[name].delete_many({})
        logger.info(f"Cleared '{name}' ({result.deleted_count} documents deleted)")

    mongo_client.close()
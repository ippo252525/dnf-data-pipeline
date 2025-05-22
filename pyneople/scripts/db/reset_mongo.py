from pymongo import MongoClient
from pyneople.config.config import Settings

import logging
logger = logging.getLogger(__name__)

def drop_collection(collection_names: str | list[str]):
    mongo_client = MongoClient(Settings.MONGO_URL)
    db = mongo_client[Settings.MONGO_DB_NAME]
    if isinstance(collection_names, str):
        collection_names = [collection_names]    
    for name in collection_names:
            db[name].drop()
            logger.info(f"Drop collection : '{name}')")
    mongo_client.close()            

def clear_collection(collection_names: str | list[str]):
    mongo_client = MongoClient(Settings.MONGO_URL)
    db = mongo_client[Settings.MONGO_DB_NAME]

    if isinstance(collection_names, str):
        collection_names = [collection_names]

    for name in collection_names:
        result = db[name].delete_many({})
        logger.info(f"Cleared '{name}' ({result.deleted_count} documents deleted)")

    mongo_client.close()

if __name__ == "__main__":
    mongo_client = MongoClient(Settings.MONGO_URL)
    db = mongo_client[Settings.MONGO_DB_NAME]
    for coll_name in db.list_collection_names():
        if not coll_name.startswith("system."):
            clear_collection(coll_name)
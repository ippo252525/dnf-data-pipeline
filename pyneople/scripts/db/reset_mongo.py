from pymongo import MongoClient
from pyneople.config.config import Settings

def clear_collection(collection_names: str | list[str]):
    mongo_client = MongoClient(Settings.MONGO_URL)
    db = mongo_client[Settings.MONGO_DB_NAME]

    if isinstance(collection_names, str):
        collection_names = [collection_names]

    for name in collection_names:
        result = db[name].delete_many({})
        print(f"Cleared '{name}' ({result.deleted_count} documents deleted)")

    mongo_client.close()

if __name__ == "__main__":
    mongo_client = MongoClient(Settings.MONGO_URL)
    db = mongo_client[Settings.MONGO_DB_NAME]
    for coll_name in db.list_collection_names():
        if not coll_name.startswith("system."):
            clear_collection(coll_name)
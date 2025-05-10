from pymongo import MongoClient
from pyneople.config.config import Settings

def main():
    mongo_client = MongoClient(Settings.MONGO_URL)
    db = mongo_client[Settings.MONGO_DB_NAME]
    coll = db[Settings.MONGO_COLLECTION_NAME]
    error_coll = db[Settings.MONGO_ERROR_COLLECTION_NAME]
    print(Settings.MONGO_COLLECTION_NAME)
    print(coll.delete_many({}))
    print(Settings.MONGO_ERROR_COLLECTION_NAME)
    print(error_coll.delete_many({}))

if __name__ == "__main__":
    main()
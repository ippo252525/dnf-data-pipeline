from motor.motor_asyncio import AsyncIOMotorClient
from pyneople.config.config import Settings

class MongoConnectionManager:
    """
    MongoDB 관리를 위한 매니저 클래스입니다.
    MongoDB에 연결하고, 데이터베이스와 컬렉션을 초기화합니다.
    """
    _collection = None
    _error_collection = None

    @classmethod
    async def init_collection(cls):
        if cls._collection is None:
            mongo_client = AsyncIOMotorClient(Settings.MONGO_URL)
            mongo_db = mongo_client[Settings.MONGO_DB_NAME]
            cls._collection = mongo_db[Settings.MONGO_COLLECTION_NAME]
            cls._error_collection = mongo_db[Settings.MONGO_ERROR_COLLECTION_NAME]

    @classmethod
    def get_collection(cls):
        if cls._collection is None:
            raise RuntimeError("Mongo collection not initialized. Call init_collection() first.")
        return cls._collection
    
    @classmethod
    def get_error_collection(cls):
        if cls._error_collection is None:
            raise RuntimeError("Mongo error collection not initialized. Call init_collection() first.")
        return cls._error_collection
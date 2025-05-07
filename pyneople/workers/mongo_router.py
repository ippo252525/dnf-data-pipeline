from motor.motor_asyncio import AsyncIOMotorCollection
from pyneople.utils.api_utils.extract_character_info_data import extract_character_info_data
from pyneople.config.config import Settings
            
class MongoRouter:

    def __init__(self, 
        mongo_collection: AsyncIOMotorCollection, 
        queue_map: dict, 
        character_info_endpoints : list,
        batch_size: int = Settings.DEFAULT_MONGO_ROUTER_BATCH_SIZE):
        self.character_info_endpoints = character_info_endpoints
        self.mongo_collection = mongo_collection
        self.queue_map = queue_map
        self.batch_size = batch_size
    
    async def route(self, id_filter):
        """
        MongoDB에서 특정 범위(id_filter)에 대해 데이터를 읽고, endpoint 별 큐에 분배
        """
        cursor = self.mongo_collection.find(id_filter).batch_size(self.batch_size)
        async for document in cursor:
            endpoint = document.get('endpoint')
            
            target_queue = self.queue_map.get(endpoint)
            if target_queue:
                await target_queue.put(document.get('data'))
            
            if self.character_info_endpoints:
                if endpoint in self.character_info_endpoints:
                    target_queue = self.queue_map.get('character_info')
                    if target_queue:
                        await target_queue.put(extract_character_info_data(document))

            
                
                
from motor.motor_asyncio import AsyncIOMotorCollection
from pyneople.config.config import Settings

async def get_split_filters(mongo_collection: AsyncIOMotorCollection, 
                            num_workers: int = Settings.DEFAULT_NUM_MONGO_ROUTERS):
        """
        MongoDB _id를 기준으로 num_workers개 범위 필터를 계산해서 반환하는 비동기 함수
        
        MongoDB 단일 Collection에서 데이터를 가져오는 워커를 어려개 동시에 사용 할 때 사용

        Args:
            mongo_collection(AsyncIOMotorCollection): 비동기 MongoDB 드라이버 motor의 collection 객체
            num_workers(int): 사용 할 워커의 개수

        Returns:
            list: _id기반 필터을 원소로 가지는 list
        """
        total_docs = await mongo_collection.estimated_document_count()
        split_points = []

        for i in range(1, num_workers):
            skip = int(total_docs * i / num_workers)
            doc = await mongo_collection.find({}).sort('_id', 1).skip(skip).limit(1).to_list(1)
            if doc:
                split_points.append(doc[0]['_id'])

        # ID 범위 필터 만들기
        filters = []
        last_id = None
        for split_id in split_points:
            if last_id is None:
                filters.append({'_id': {'$lt': split_id}})
            else:
                filters.append({'_id': {'$gte': last_id, '$lt': split_id}})
            last_id = split_id
        if last_id:
            filters.append({'_id': {'$gte': last_id}})
        else:
            filters.append({})  # 데이터 적은 경우

        return filters
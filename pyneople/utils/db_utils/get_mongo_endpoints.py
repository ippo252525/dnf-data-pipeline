from motor.motor_asyncio import AsyncIOMotorCollection

async def get_mongo_endpoints(mongo_collection: AsyncIOMotorCollection) -> list:
    """
    MongoDB에서 엔드포인트 목록을 가져오는 함수

    문서 수가 10만 개 이상인 경우에는 커서를 사용하여 비동기적으로 엔드포인트를 가져오고 문서 수가 적은 경우에는 distinct를 사용하여 엔드포인트를 가져옴
    
    Args:
        mongo_collection (AsyncIOMotorCollection): MongoDB 컬렉션 객체
    
    Returns:
        list: 엔드포인트 목록
    """
    endpoints = []
    
    # 대략적 문서 수를 가져옵니다.
    doc_count = await mongo_collection.estimated_document_count()

    if doc_count > 100000:
        # 엔드포인트 목록을 가져오는 데 시간이 걸릴 수 있으므로 비동기적으로 처리합니다.
        cursor = mongo_collection.find({}).batch_size(1000)
        async for document in cursor:
            endpoint = document.get('endpoint')
            if endpoint not in endpoints:
                endpoints.append(endpoint)
    else:
        # 문서 수가 적은 경우에는 직접 가져옵니다.
        endpoints = await mongo_collection.distinct('endpoint')
    
    return endpoints
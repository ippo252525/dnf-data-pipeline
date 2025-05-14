import asyncio
import asyncpg
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pyneople.config.config import Settings
from pyneople.workers.mongo_router import MongoRouter
from pyneople.workers.queue_to_psql_worker import QueueToPSQLWorker
from pyneople.workers.shutdwon_controller import ShutdownController
from pyneople.utils.db_utils.get_mongo_endpoints import get_mongo_endpoints
from pyneople.utils.db_utils.get_mongo_split_filters import get_split_filters

# EndpointRegistry 등록을 위한 endpoint_class import
import pyneople.api.registry.endpoint_class
from pyneople.api.registry.endpoint_registry import EndpointRegistry

import logging
logger = logging.getLogger(__name__)

async def _mongo_to_psql(
    endpoints: Optional[list] = None,
    character_info_endpoints: Optional[list] = None,
    mongo_collection_name : str = Settings.MONGO_COLLECTION_NAME,
    error_collection_name : str = Settings.MONGO_ERROR_COLLECTION_NAME,
    queue_size : int = Settings.DEFAULT_MONGO_TO_PSQL_QUEUE_SIZE,
    num_queue_to_psql_workers: int = Settings.DEFAULT_NUM_QUEUE_TO_PSQL_WORKERS,
    mongo_router_batch_size: int = Settings.DEFAULT_MONGO_ROUTER_BATCH_SIZE,
    queue_to_psql_batch_size: int = Settings.DEFAULT_QUEUE_TO_PSQL_BATCH_SIZE,
    num_mongo_routers: int = Settings.DEFAULT_NUM_MONGO_ROUTERS,
    mongo_to_psql_pool_max_size: int = Settings.DEFAULT_MONGO_TO_PSQL_POOL_MAX_SIZE
):
    """
    MongoDB에 저장된 데이터를 PostgreSQL로 이동시키는 비동기 파이프라인을 실행하는 함수

    MongoRouter를 통해 MongoDB 데이터를 큐로 라우팅하고, QueueToPSQLWorker가 이를 PostgreSQL 테이블로 저장함.
    각 워커와 큐는 endpoint별로 분리되어 병렬로 처리되며, 종료 시 graceful shutdown을 보장함

    Args:
        endpoints (Optional[list]): 처리할 API endpoint 리스트. 지정하지 않으면 MongoDB에서 자동 감지
        character_info_endpoints (Optional[list]): 캐릭터 정보를 추출해야 하는 endpoint 리스트
        mongo_collection_name (str) : 데이터를 가져올 MongoDB collection name
        error_collection_name (str) : error를 저장 할 MongoDB collection name
        queue_size (int): endpoint별 큐의 최대 크기
        num_queue_to_psql_workers (int): endpoint별 QueueToPSQLWorker의 개수
        mongo_router_batch_size (int): MongoRouter가 MongoDB에서 가져올 document의 batch 크기
        queue_to_psql_batch_size (int): PostgreSQL로 저장할 때 사용할 데이터 batch 크기
        num_mongo_routers (int): MongoRouter 인스턴스 수
        mongo_to_psql_pool_max_size (int): PostgreSQL connection pool의 최대 크기

    Returns:
        None
    """    
    # 1. DB 연결
    # MongoDB
    mongo_client = AsyncIOMotorClient(Settings.MONGO_URL)
    mongo_collection = mongo_client[Settings.MONGO_DB_NAME][mongo_collection_name]    
    mongo_error_collection = mongo_client[Settings.MONGO_DB_NAME][error_collection_name]
    
    # PostgreSQL
    async with asyncpg.create_pool(
        user=Settings.POSTGRES_USER,
        password=Settings.POSTGRES_PASSWORD,
        database=Settings.POSTGRES_DB,
        host=Settings.POSTGRES_HOST,
        port=Settings.POSTGRES_PORT,
        min_size=num_queue_to_psql_workers,
        max_size=mongo_to_psql_pool_max_size,
    ) as psql_pool:
        logging.info(f"MongoDD Collection 확보 완료, PostgreSQL 연결 완료")
        # 2. MongoDB Collection에 저장 된 endpoint 목록 가져오기
        
        # endpoints가 명시된 경우 사용 endpoint 유효성 검사
        if endpoints:
            for endpoint in endpoints:
                if endpoint not in EndpointRegistry.get_registered_endpoints():
                    raise ValueError(f"Invalid endpoint: {endpoint} 는 지원하지 않는 endpoint 입니다")

        # endpoints 명시 안한 경우 직접 가져옴
        else:
            endpoints = await get_mongo_endpoints(mongo_collection)

        endpoints = set(endpoints)

        # 캐릭터 정보를 추출해서 사용 할 endpoint가 있으면 endpoint : 'character_info' 를 endpoints에 추가함
        if character_info_endpoints:
            # character_info_endpoints에 명시된 endpoint가 캐릭터 정보를 추출할 수 있는 endpoint인지 확인
            for character_info_endpoint in character_info_endpoints:
                if not EndpointRegistry.get_class(character_info_endpoint).has_character_info_data:
                    raise ValueError(f"Invalid endpoint: {character_info_endpoint} 는 캐릭터 정보 추출을 지원하지 않습니다")
            # 캐릭터 정보를 추출할 수 있는 endpoint가 명시된 경우 endpoints에 'character_info'를 추가    
            endpoints.add('character_info')
            
        logger.info(f'사용 endpoints : {endpoints}, 캐릭터 정보 추출 endpoints : {character_info_endpoints}')

        # 3. 큐 생성 (endpoint별)
        endpoint_queue_map = {endpoint : asyncio.Queue(maxsize=queue_size) for endpoint in endpoints}

        shutdown_event = asyncio.Event()
        error_shutdown_event = asyncio.Event()
        # 4. MongoRouter 생성 후 실행
        # MongoRouter는 mongo_collection과 endpoint_queue_map을 사용하여 데이터를 라우팅합니다.
        routers = [MongoRouter(mongo_collection, endpoint_queue_map, character_info_endpoints, error_shutdown_event, mongo_router_batch_size) for _ in range(num_mongo_routers)]
        filters = await get_split_filters(mongo_collection, num_mongo_routers)
        router_tasks = [asyncio.create_task(router.route(filter)) for router, filter in zip(routers, filters)]
        logger.info(f"MongoRouter {num_mongo_routers}개 실행 시작")

        # 5. QueueToPSQLWorker 생성 후 실행
        # queue 하나 당 num_queue_to_psql_workers 개의 QueueToPSQLWorker를 생성합니다.
        queue_to_psql_workers = []
        for endpoint in endpoints:
            endpoint_class = EndpointRegistry.get_class(endpoint)
            for i in range(num_queue_to_psql_workers):
                queue = endpoint_queue_map[endpoint]
                table_name = endpoint_class.staging_table_name
                preprocess = endpoint_class.preprocess
                worker = QueueToPSQLWorker(
                    queue=queue,
                    psql_pool=psql_pool,
                    endpoint=endpoint,
                    table_name=table_name,
                    preprocess=preprocess,
                    batch_size=queue_to_psql_batch_size,
                    shutdown_event=shutdown_event,
                    error_shutdown_event=error_shutdown_event,
                    error_collection=mongo_error_collection,
                    name = f'QueueToPSQLWorker_{endpoint}_{i}'
                )
                queue_to_psql_workers.append(worker)
        queue_to_psql_worker_tasks = [asyncio.create_task(queue_to_psql_worker.run()) for queue_to_psql_worker in queue_to_psql_workers]    
        logger.info(f"QueueToPSQLWorker {len(queue_to_psql_workers)}개 실행 시작")


        # 6. ShutdownController 생성 후 실행
        # ShutdownController는 error_shutdown_event가 설정되면 모든 워커를 종료하고 큐를 정리합니다.
        all_tasks = router_tasks + queue_to_psql_worker_tasks
        asyncio.create_task(ShutdownController(list(endpoint_queue_map.values()), error_shutdown_event, all_tasks).run())

        # 7. 종료
        # try:
        await asyncio.gather(*router_tasks)
        # except asyncio.CancelledError:
            # pass    
        logger.info(f"MongoRouter {num_mongo_routers}개 실행 완료")    
        
        joins = [queue.join() for queue in endpoint_queue_map.values()]
        # try:
        await asyncio.gather(*joins)
        #except asyncio.CancelledError:
        #    pass    
        logger.info(f"endpoint queue join 완료")
        shutdown_event.set()
        
        # try:
        await asyncio.gather(*queue_to_psql_worker_tasks, return_exceptions=True)
        # except asyncio.CancelledError:
        #     pass
        logger.info(f"QueueToPSQLWorker {len(endpoints) * num_queue_to_psql_workers}개 실행 완료")        

def mongo_to_psql(
    endpoints: Optional[list] = None,
    character_info_endpoints: Optional[list] = None,
    mongo_collection_name : str = Settings.MONGO_COLLECTION_NAME,
    error_collection_name : str = Settings.MONGO_ERROR_COLLECTION_NAME,
    queue_size: int = Settings.DEFAULT_MONGO_TO_PSQL_QUEUE_SIZE,
    num_queue_to_psql_workers: int = Settings.DEFAULT_NUM_QUEUE_TO_PSQL_WORKERS,
    mongo_router_batch_size: int = Settings.DEFAULT_MONGO_ROUTER_BATCH_SIZE,
    queue_to_psql_batch_size: int = Settings.DEFAULT_QUEUE_TO_PSQL_BATCH_SIZE,
    num_mongo_routers: int = Settings.DEFAULT_NUM_MONGO_ROUTERS,
    mongo_to_psql_pool_max_size: int = Settings.DEFAULT_MONGO_TO_PSQL_POOL_MAX_SIZE
):
    asyncio.run(
        _mongo_to_psql(
            endpoints=endpoints,
            character_info_endpoints=character_info_endpoints,
            mongo_collection_name = mongo_collection_name,
            error_collection_name = error_collection_name,
            queue_size=queue_size,
            num_queue_to_psql_workers=num_queue_to_psql_workers,
            mongo_router_batch_size=mongo_router_batch_size,
            queue_to_psql_batch_size=queue_to_psql_batch_size,
            num_mongo_routers=num_mongo_routers,
            mongo_to_psql_pool_max_size=mongo_to_psql_pool_max_size
        )
    )        
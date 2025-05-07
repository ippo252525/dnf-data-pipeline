import asyncio
import aiohttp
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient

from pyneople.config.config import Settings
from pyneople.workers.api_fetch_worker import APIFetchWorker
from pyneople.utils.monitoring import count_requests_per_second
from pyneople.workers.mongo_store_worker import MongoStoreWorker
from pyneople.workers.shutdwon_controller import ShutdownController

# EndpointRegistry 등록을 위한 endpoint_class import
import pyneople.api.registry.endpoint_class
from pyneople.api.registry.endpoint_registry import EndpointRegistry

import logging

logger = logging.getLogger(__name__)

async def _api_to_mongo(endpoints : list[str],
                       
               check_rate_limit : bool = None,
               num_api_fetch_workers : int = Settings.DEFAULT_NUM_API_FETCH_WORKERS, 
               num_mongo_store_workers : int = Settings.DEFAULT_NUM_MONGO_STORE_WORKERS,
               api_request_queue_size : int = Settings.DEFAULT_API_REQUEST_QUEUE_SIZE,
               mongo_store_batch_size : int = Settings.DEFAULT_MONGO_STORE_BATCH_SIZE,
               seeder_batch_size : int = Settings.DEFAULT_SEEDER_BATCH_SIZE,
               psql_pool_max_size : int = Settings.DEFAULT_SEEDER_PSQL_POOL_MAX_SIZE,
               **seed_kwargs):
    """
    Neople API 데이터를 수집하고 MongoDB에 저장하는 전체 비동기 파이프라인을 실행하는 함수

    지정된 endpoint별 seeder로부터 API 요청을 생성하고,
    fetch worker를 통해 데이터를 수집한 후,
    MongoDB store worker를 통해 저장함.
    모든 구성 요소는 비동기적으로 실행되며, 안전한 종료 절차가 포함됨

    Args:
        endpoints (list[str]): 사용할 API endpoint 리스트
        check_rate_limit (bool, optional): 초당 요청 수를 모니터링할지 여부
        num_api_fetch_workers (int): 실행할 API fetch worker 수
        num_mongo_store_workers (int): 실행할 MongoDB store worker 수
        api_request_queue_size (int): API 요청 큐의 최대 크기
        mongo_store_batch_size (int): MongoDB에 저장할 때 사용할 batch 크기
        seeder_batch_size (int): seeder가 한 번에 처리할 데이터 수
        psql_pool_max_size (int): PostgreSQL connection pool의 최대 크기
        **seed_kwargs: 각 seeder에 전달할 추가 파라미터 (예: start_date, end_date 등)

    Returns:
        None
    """    
    # Shutdown event 설정
    api_shutdown_event = asyncio.Event()
    mongo_shutdown_event = asyncio.Event()

    # DB 연결
    mongo_client = AsyncIOMotorClient(Settings.MONGO_URL)
    mongo_collection = mongo_client[Settings.MONGO_DB_NAME][Settings.MONGO_COLLECTION_NAME]
    error_collection = mongo_client[Settings.MONGO_DB_NAME][Settings.MONGO_ERROR_COLLECTION_NAME]        
    async with asyncpg.create_pool(
        user=Settings.POSTGRES_USER,
        password=Settings.POSTGRES_PASSWORD,
        database=Settings.POSTGRES_DB,
        host=Settings.POSTGRES_HOST,
        port=Settings.POSTGRES_PORT,
        min_size=len(endpoints),
        max_size=psql_pool_max_size,
    ) as psql_pool:
        
        # Queue 선언
        api_request_queue = asyncio.Queue(maxsize=api_request_queue_size)
        data_queue = asyncio.Queue()
        
        async with aiohttp.ClientSession() as session:
            
            # 여러 개의 워커 생성
            if check_rate_limit:
                asyncio.create_task(count_requests_per_second(api_shutdown_event))
            seeders = [EndpointRegistry.get_class(endpoint).seeder(endpoint, api_request_queue, psql_pool, api_shutdown_event, seeder_batch_size, name = f'{endpoint}_Seeder') for endpoint in endpoints]
            api_fetch_workers = [APIFetchWorker(api_request_queue, data_queue, session, api_shutdown_event, error_collection, name = f'APIFetchWorker_{i}') for i in range(num_api_fetch_workers)]
            mongo_store_workers = [MongoStoreWorker(data_queue, mongo_collection, mongo_shutdown_event, mongo_store_batch_size, name = f'MongoStoreWorker_{i}') for i in range(num_mongo_store_workers)]

            
            # 워커 태스크 실행
            seeders_tasks = [asyncio.create_task(seeder.seed(**seed_kwargs)) for seeder in seeders]
            logger.info(f"seeder {len(seeders)}개 실행 시작")
            api_fetch_worker_tasks = [asyncio.create_task(worker.run()) for worker in api_fetch_workers]
            logger.info(f"api_fetch_worker {len(api_fetch_workers)}개 실행 시작")
            mongo_store_worker_tasks = [asyncio.create_task(worker.run()) for worker in mongo_store_workers]
            logger.info(f"mongo_store_worker {len(mongo_store_workers)}개 실행 시작")
            
            shutdown_controller_tasks = [
                asyncio.create_task(ShutdownController([api_request_queue], api_shutdown_event, seeders_tasks + api_fetch_worker_tasks, 'APIShutdwonController').run()),
                asyncio.create_task(ShutdownController([data_queue], mongo_shutdown_event, api_fetch_worker_tasks + mongo_store_worker_tasks, 'MongoShutdwonController').run())
            ]

            
            try:
                await asyncio.gather(*seeders_tasks)
            except asyncio.CancelledError:
                pass    
            logger.info(f"seeder {len(seeders)}개 실행 완료")

            # 모든 작업이 끝날 때까지 대기
            await api_request_queue.join()
            logger.info("api_request_queue join 완료")

            api_shutdown_event.set()
            logger.info("api_shutdown_event set 완료")

            try:
                await asyncio.gather(*api_fetch_worker_tasks)
            except asyncio.CancelledError:    
                pass
            logger.info(f"api_fetch_worker {len(api_fetch_workers)}개 실행 완료")

            await data_queue.join()
            logger.info("data queue join 완료")
            
            mongo_shutdown_event.set()
            logger.info("mongo_shutdown_event set 완료")
            
            try:
                await asyncio.gather(*mongo_store_worker_tasks)
            except asyncio.CancelledError:
                pass    
            logger.info(f"mongo_store_worker {len(mongo_store_workers)}개 실행 완료")

            await asyncio.gather(*shutdown_controller_tasks)
            logger.info("shutdown_controller_tasks 완료")
            logger.info("api_to_mongo 완료")

def api_to_mongo(
    endpoints: list[str],
    check_rate_limit: bool = None,
    num_api_fetch_workers: int = Settings.DEFAULT_NUM_API_FETCH_WORKERS,
    num_mongo_store_workers: int = Settings.DEFAULT_NUM_MONGO_STORE_WORKERS,
    api_request_queue_size: int = Settings.DEFAULT_API_REQUEST_QUEUE_SIZE,
    mongo_store_batch_size: int = Settings.DEFAULT_MONGO_STORE_BATCH_SIZE,
    seeder_batch_size: int = Settings.DEFAULT_SEEDER_BATCH_SIZE,
    psql_pool_max_size: int = Settings.DEFAULT_SEEDER_PSQL_POOL_MAX_SIZE,
    **seed_kwargs
):
    asyncio.run(
        _api_to_mongo(
            endpoints=endpoints,
            check_rate_limit=check_rate_limit,
            num_api_fetch_workers=num_api_fetch_workers,
            num_mongo_store_workers=num_mongo_store_workers,
            api_request_queue_size=api_request_queue_size,
            mongo_store_batch_size=mongo_store_batch_size,
            seeder_batch_size=seeder_batch_size,
            psql_pool_max_size=psql_pool_max_size,
            **seed_kwargs
        )
    )           
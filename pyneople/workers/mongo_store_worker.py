import asyncio
from motor.motor_asyncio import AsyncIOMotorCollection
from pyneople.config.config import Settings
from pyneople.utils.decorators import log_execution_time
import logging

logger = logging.getLogger(__name__)                           

# MongoDB에 데이터를 저장하는 워커 클래스
class MongoStoreWorker:
    """
    데이터를 MongoDB에 저장하는 비동기 워커 클래스

    데이터 큐에서 일정량의 데이터를 모은 후, MongoDB 컬렉션에 batch insert를 수행함

    Attributes:
        queue (asyncio.Queue): 처리할 데이터를 담고 있는 큐
        mongo_collection (AsyncIOMotorCollection): 데이터를 저장할 MongoDB 컬렉션
        batch_size (int): 한 번에 저장할 데이터 개수
        shutdown_event (asyncio.Event): 워커 종료를 제어하는 이벤트
        timeout (float): 큐에서 데이터를 기다리는 최대 시간 (초)
        name (str): 워커 이름
    """    
    def __init__(self, data_queue: asyncio.Queue, mongo_collection: AsyncIOMotorCollection, shutdown_event : asyncio.Event, batch_size: int = Settings.DEFAULT_MONGO_STORE_BATCH_SIZE, timeout : float = Settings.DEFAULT_MONGO_STORE_WORKER_TIMEOUT, name : str = 'MongoStoreWorker'):
        self.queue = data_queue
        self.mongo_collection = mongo_collection
        self.batch_size = batch_size
        self.shutdown_event = shutdown_event
        self.timeout = timeout
        self.name = name or self.__class__.__name__
        self.batch = []
        self.num_unfinished_task = 0

    async def run(self):
        """
        워커의 메인 루프를 실행하는 메서드

        shutdown_event가 설정될 때까지 반복 실행되며, 큐에서 데이터를 수집하고
        MongoDB에 저장한 후 task_done을 호출함
        """        
        while not self.shutdown_event.is_set():
            self.batch = []
            self.num_unfinished_task = 0
            try:
                await self._collect_batch()
                if not self.batch:
                    logger.info(f'{self.name} : batch가 비어있음')
                    continue
                logger.info(f'{self.name} : 데이터 {self.num_unfinished_task}개 수집 완료')
                await self._insert_batch()  
            except asyncio.CancelledError:
                logger.info(f'{self.name} : CancelledError 발생, unfinished_task : {self.num_unfinished_task}')
                raise
            except Exception as e:
                logger.error(f"{self.name} : 오류 발생 - {e}")
                self.shutdown_event.set()
                break
            finally:
                for _ in range(self.num_unfinished_task):
                    self.queue.task_done()
        logger.info(f'{self.name} : shutdown_event가 설정되어 종료됨')

    @log_execution_time('collect_batch')
    async def _collect_batch(self):
        
        while len(self.batch) < self.batch_size:
            if self.shutdown_event.is_set():
                break
            data = None
            try:
                data = self.queue.get_nowait()
            except asyncio.QueueEmpty:
                logger.debug(f"{self.name} : nowait_get 실패")
                try:
                    data = await asyncio.wait_for(self.queue.get(), timeout=self.timeout)
                except asyncio.TimeoutError:
                    logger.warning(f"{self.name} : 큐에서 데이터를 가져오지 못함 (Timeout)")
                    break                
            finally:
                if data is not None:
                    self.num_unfinished_task += 1    
            self.batch.append(data)    
            
    @log_execution_time('insert_batch')
    async def _insert_batch(self):
        try:
            await self.mongo_collection.insert_many(self.batch)
            logger.info(f'{self.name} : {len(self.batch)}개 데이터 저장 완료')
        except Exception as e:
            logger.error(f"{self.name} : 데이터 저장 실패 - {e}")
            for doc in self.batch:
                logger.debug(f"Failed document: {doc}")
            raise e    
import asyncpg
import asyncio
from typing import Optional
from pyneople.config.config import Settings
from motor.motor_asyncio import AsyncIOMotorCollection
from pyneople.utils.decorators import log_execution_time
from pyneople.metadata.metadata_generated import TABLE_COLUMNS_MAP
import traceback

import logging
logger = logging.getLogger(__name__)

class QueueToPSQLWorker:
    """
    큐에서 데이터를 수집하고 PostgreSQL 테이블로 bulk insert하는 비동기 워커 클래스

    Attributes:
        queue (asyncio.Queue): 처리할 데이터를 담고 있는 큐
        psql_pool (asyncpg.Pool): PostgreSQL connection pool
        endpoint (str): 처리 대상 API endpoint
        table_name (str): 데이터를 저장할 PostgreSQL 테이블 이름
        preprocess (callable): 데이터를 insert 가능한 형태로 변환하는 전처리 함수
        batch_size (int): 한 번에 처리할 데이터 개수
        shutdown_event (asyncio.Event): 워커 종료 제어 이벤트
        timeout (float): 큐에서 데이터를 대기할 최대 시간 (초)
        name (str): 워커 이름
        batch (list): 현재 batch에 수집된 데이터
        num_unfinished_task (int): 현재 처리 중인 태스크 수
    """    
    def __init__(self, 
                 queue : asyncio.Queue, 
                 psql_pool : asyncpg.Pool, 
                 endpoint : str, 
                 table_name : str, 
                 preprocess : callable, 
                 batch_size : int,
                 shutdown_event : asyncio.Event, 
                 error_collection : AsyncIOMotorCollection,
                 timeout : float = Settings.DEFAULT_QUEUE_TO_PSQL_WORKER_TIMEOUT,
                 name : Optional[str]  = None):
        self.queue = queue
        self.psql_pool = psql_pool
        self.endpoint = endpoint
        self.table_name = table_name
        self.preprocess = preprocess
        self.batch_size = batch_size
        self.shutdown_event = shutdown_event
        self.timeout = timeout  
        self.error_collection = error_collection
        self.name = name or self.__class__.__name__
        self.batch = []
        self.num_unfinished_task = 0

    async def run(self):
        """
        워커의 메인 루프를 실행하는 메서드

        shutdown_event가 설정되기 전까지 큐에서 데이터를 수집하고 PostgreSQL로 저장함.
        예외 발생 시 로그를 출력하고 종료 이벤트를 설정함
        """        
        while not self.shutdown_event.is_set():
            self.batch = []
            self.num_unfinished_task = 0
            try:
                await self._collect_batch()
                if not self.batch:
                    logger.info(f'{self.name} : batch가 비어있음')
                    continue
                logger.info(f'{self.name} : 데이터 {len(self.batch)}개 수집 완료')
                await self._copy_to_psql()  
            except asyncio.CancelledError:
                logger.info(f'{self.name} : CancelledError 발생, unfinished_task : {self.num_unfinished_task}')
                raise
            except Exception as e:
                # logger.error(f"{self.name} : 오류 발생")
                logger.error(f"{self.name} : 오류 발생\n{e}")
                self.shutdown_event.set()
                break
            finally:
                for _ in range(self.num_unfinished_task):
                    self.queue.task_done()    
        logger.info(f'{self.name} : shutdown_event가 설정되어 종료됨')
    
    @log_execution_time('collect_batch')
    async def _collect_batch(self):
        """
        큐에서 데이터를 수집하여 batch에 저장하는 메서드

        shutdown 이벤트나 타임아웃이 발생할 때까지 데이터를 수집하며,
        전처리 함수를 통해 데이터 포맷을 변환함

        Raises:
            asyncio.TimeoutError: 큐에서 데이터를 일정 시간 동안 가져오지 못한 경우
        """        
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
            data = self.preprocess(data, TABLE_COLUMNS_MAP[self.table_name])
            if isinstance(data, list):
                self.batch.extend(data)
            else:
                self.batch.append(data)        

    @log_execution_time('copy_to_psql')
    async def _copy_to_psql(self):
        """
        batch에 수집된 데이터를 PostgreSQL에 bulk insert하는 메서드

        데이터는 `copy_records_to_table`을 사용해 삽입되며,
        실패 시 전체 batch 내용을 출력하고 예외를 다시 발생시킴

        Raises:
            Exception: copy 작업 중 발생한 예외
        """        
        try:
            async with self.psql_pool.acquire() as conn:
                async with conn.transaction():
                    await conn.copy_records_to_table(
                        self.table_name,
                        records=[tuple(row.values()) for row in self.batch],
                        columns=self.batch[0].keys(),
                    )
        except Exception as e:
            self.error_collection.insert_one({'error' : str(e), 'batch' : self.batch})
            logger.error(f"{self.name} : copy 중 오류 발생")
            # for doc in self.batch:
                # logger.debug(f"Failed document: {doc}")
            # raise e

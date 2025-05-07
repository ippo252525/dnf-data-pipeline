import asyncio
import asyncpg
from typing import Optional
from itertools import cycle
from pyneople.config.config import Settings
from abc import ABC, abstractmethod

import logging

logger = logging.getLogger(__name__)

class BaseSeeder(ABC):
    """
    비동기 API request를 생성하여 큐에 넣는 seeder의 추상 base class

    Attributes:
        end_point (str): 사용할 API endpoint
        api_request_queue (asyncio.Queue): API 요청을 저장할 큐
        psql_pool (asyncpg.Pool): PostgreSQL connection pool
        shutdown_event (asyncio.Event): 종료 이벤트 플래그
        seeder_batch_size (int): 한 번에 처리할 데이터 수
        api_keys (Optional[list]): API key 리스트 (순환 구조)
        name (Optional[str]): Seeder 이름
    """    
    def __init__(self, 
                 end_point : str, 
                 api_request_queue: asyncio.Queue, 
                 psql_pool: asyncpg.Pool, 
                 shutdown_event: asyncio.Event, 
                 seeder_batch_size: int = Settings.DEFAULT_SEEDER_BATCH_SIZE,
                 api_keys: Optional[list]  = None,
                 name : Optional[str] = None):
        self.end_point = end_point
        self.api_request_queue = api_request_queue
        self.shutdown_event = shutdown_event
        self.psql_pool = psql_pool
        self.api_keys = cycle(api_keys.copy() if api_keys is not None else Settings.API_KEYS.copy())
        self.seeder_batch_size = seeder_batch_size
        self.name = name or self.__class__.__name__
    
    @abstractmethod
    async def seed(self):
        """
        데이터를 기반으로 API 요청을 생성하고 큐에 삽입하는 비동기 메서드
        """        
        pass
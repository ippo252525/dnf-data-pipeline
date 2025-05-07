import asyncio
import asyncpg
from typing import Optional
from itertools import cycle
from datetime import datetime, timedelta
from pyneople.config.config import Settings
from pyneople.api.metadata import PARAMS_FOR_SEED_CHARACTER_FAME
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
        api_keys (list[str]): API key 리스트 (순환 구조)
        name (Optional[str]): Seeder 이름
    """    
    def __init__(self, 
                 end_point : str, 
                 api_request_queue: asyncio.Queue, 
                 psql_pool: asyncpg.Pool, 
                 shutdown_event: asyncio.Event, 
                 seeder_batch_size: int = Settings.DEFAULT_SEEDER_BATCH_SIZE,
                 api_keys: list[str] = Settings.API_KEYS,
                 name : Optional[str] = None):
        self.end_point = end_point
        self.api_request_queue = api_request_queue
        self.shutdown_event = shutdown_event
        self.psql_pool = psql_pool
        self.api_keys = cycle(api_keys)
        self.seeder_batch_size = seeder_batch_size
        self.name = name or self.__class__.__name__
    
    @abstractmethod
    async def seed(self):
        """
        데이터를 기반으로 API 요청을 생성하고 큐에 삽입하는 비동기 메서드
        """        
        pass

class CharacterBaseSeeder(BaseSeeder):
    """
    캐릭터 ID와 서버 ID를 기반으로 API 요청을 생성하는 seeder의 base 구현

    Methods:
        seed(**kwargs): SQL 쿼리 결과 또는 직접 주어진 row를 처리하여 요청 생성
        _process_rows(rows, **kwargs): row를 순회하며 API 요청 생성 및 큐에 삽입
        _get_api_requests(character_id, server_id, **kwargs): 단일 캐릭터에 대한 요청 리스트 생성
    """    
    async def seed(self, **kwargs):
        """
        SQL 쿼리 또는 직접 전달된 row를 기반으로 API 요청을 생성하여 큐에 삽입하는 메서드

        Args:
            **kwargs: 다음 중 하나 이상을 포함해야 함
                - sql (str): PostgreSQL에서 데이터를 가져올 쿼리
                - rows (list[tuple]): (character_id, server_id) 쌍의 리스트
                - seeder_batch_size (int, optional): 한 번에 가져올 row 수
        """        
        if kwargs['sql']:
            async with self.psql_pool.acquire() as conn:
                async with conn.transaction():
                    cursor = await conn.cursor(kwargs['sql'])
                    while not self.shutdown_event.is_set():
                        rows_batch = await cursor.fetch(kwargs.get('seeder_batch_size', self.seeder_batch_size))
                        if not rows_batch:
                            break
                        await self._process_rows(rows_batch, **kwargs)
        elif kwargs['rows']:
            await self._process_rows(kwargs['rows'], **kwargs)
        else:
            raise ValueError("sql 또는 rows 둘 중 하나는 반드시 제공되어야 합니다.")
        logger.info(f"{self.name}종료")
    async def _process_rows(self, rows, **kwargs):
        """
        row 리스트를 순회하며 캐릭터 정보 기반 API 요청을 생성하고 큐에 삽입하는 메서드

        Args:
            rows (list[tuple]): (character_id, server_id) 쌍의 리스트
            **kwargs: 추가 파라미터
        """        
        for character_id, server_id in rows:
            api_requests = self._get_api_requests(character_id, server_id, **kwargs)
            for api_request in api_requests:
                await self.api_request_queue.put(api_request)   

    def _get_api_requests(self, character_id, server_id, **kwargs):     
        """
        단일 캐릭터에 대한 API 요청 리스트를 생성하는 메서드

        Args:
            character_id (str): 캐릭터 ID
            server_id (str): 서버 ID
            **kwargs: 추가 파라미터

        Returns:
            list[dict]: API 요청 dict 리스트
        """          
        api_requests = [{
            'endpoint' : self.end_point,
            'params' : {
                'characterId' : character_id,
                'serverId' : server_id,
                'apikey' : next(self.api_keys)
            }
        }]   
        return api_requests

class CharacterFameSeeder(BaseSeeder):
    """
    캐릭터 명성 기준 초기 데이터를 수집하는 seeder 클래스

    Methods:
        seed(max_fame): maxFame 기준으로 조합된 job 정보와 함께 API 요청 생성
    """    
    async def seed(self, max_fame : int):
        for seed_params in PARAMS_FOR_SEED_CHARACTER_FAME:
            if self.shutdown_event.is_set():
                break
            api_request = {
                'endpoint' : self.end_point, 
                'params' : {
                        'maxFame' : max_fame,
                        'jobId' : seed_params['jobId'],
                        'jobGrowId' : seed_params['jobGrowId'],
                        'serverId' : seed_params['serverId'],
                        'apikey' : next(self.api_keys)
                }
            }
            await self.api_request_queue.put(api_request)
        logger.info(f"{self.name}종료")

class CharacterTimelineSeeder(CharacterBaseSeeder):
    """
    캐릭터 타임라인 데이터를 일정 기간 범위로 나누어 수집하는 seeder 클래스

    Methods:
        _get_api_request(character_id, server_id, **kwargs): 기간 범위를 나눠 API 요청 리스트 생성
    """    
    def _get_api_request(self, character_id, server_id, **kwargs):
        api_requests = []
        start_date = kwargs.get('start_date', '2025-01-09 12:00')
        end_date = kwargs.get('end_date', datetime.now().strftime("%Y-%m-%d %H:%M"))
        code = kwargs.get('code', '')
        limit = kwargs.get('limit', 100)
        
        end_dt = datetime.strptime(end_date, '%Y-%m-%d %H:%M')
        start_dt = datetime.strptime(start_date, '%Y-%m-%d %H:%M')

        ranges = []
        current_start = start_dt
        while current_start < end_dt:
            current_end = min(current_start + timedelta(days=90), end_dt)
            ranges.append((current_start, current_end))
            current_start = current_end

            for range_start, range_end in ranges:
                api_request = {
                    'endpoint': self.end_point,
                    'params': {
                        'characterId': character_id,
                        'serverId': server_id,
                        'startDate': range_start.strftime('%Y-%m-%d %H:%M'),
                        'endDate': range_end.strftime('%Y-%m-%d %H:%M'),
                        'code': code,
                        'limit': limit,
                        'apikey': next(self.api_keys)
                    }
                }
                api_requests.append(api_request)
        return api_requests

SEEDERS = {
    'character_fame' : CharacterFameSeeder,
    'character_info' : CharacterBaseSeeder,
    'character_timeline' : CharacterTimelineSeeder
}
from pyneople.api.seeders.base_seeder import BaseSeeder

import logging

logger = logging.getLogger(__name__)

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
                        print(rows_batch)
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
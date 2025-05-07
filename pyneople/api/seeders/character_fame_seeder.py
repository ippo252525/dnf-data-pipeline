from pyneople.api.seeders.base_seeder import BaseSeeder
from pyneople.metadata.metadata_generated import PARAMS_FOR_SEED_CHARACTER_FAME

import logging

logger = logging.getLogger(__name__)

class CharacterFameSeeder(BaseSeeder):
    """
    캐릭터 명성 기준 초기 데이터를 수집하는 seeder 클래스

    Methods:
        seed(max_fame): maxFame 기준으로 조합된 job 정보와 함께 API 요청 생성
    """    
    async def seed(self, max_fame : int, **kwargs):
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
from pyneople.api.seeders.character_base_seeder import CharacterBaseSeeder
from datetime import datetime, timedelta

import logging

logger = logging.getLogger(__name__)

class CharacterTimelineSeeder(CharacterBaseSeeder):
    """
    캐릭터 타임라인 데이터를 일정 기간 범위로 나누어 수집하는 seeder 클래스

    Methods:
        _get_api_request(character_id, server_id, **kwargs): 기간 범위를 나눠 API 요청 리스트 생성
    """    
    def _get_api_request(self, character_id, server_id, **kwargs):
        api_requests = []
        start_date = kwargs.get('timeline_start_date', '2025-01-09 12:00')
        end_date = kwargs.get('timeline_end_date', datetime.now().strftime("%Y-%m-%d %H:%M"))
        code = kwargs.get('timeline_code', '')
        limit = kwargs.get('timeline_limit', 100)
        
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
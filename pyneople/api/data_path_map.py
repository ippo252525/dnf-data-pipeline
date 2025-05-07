import json
import os
from pyneople.utils.api_utils.build_path_map import build_data_path_map

def _standardize_data_map(data_map):
    data_map = {k: v if isinstance(v, tuple) else (v,) for k, v in data_map.items()}
    data_map.update(fetched_at = ('fetched_at',))
    return data_map

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _get_data_path_map(endpoint, identifier_key=None):
    file_path = os.path.join(BASE_DIR, f'marked_responses/{endpoint}.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        data = build_data_path_map(data, identifier_key=identifier_key)     
    return _standardize_data_map(data) 

# 캐릭터 기본 정보 조회
CHARACTER_INFO_DATA_PATH_MAP = _get_data_path_map('character_info')

# 캐릭터 타임라인 정보 조회
CHARACTER_TIMELINE_DATA_PATH_MAP = {
    'server_id': 'serverId',
    'character_id': 'characterId',    
    'timeline_code': 'code',
    'timeline_name': 'name',
    'timeline_date': 'date',
    'timeline_data': 'data'
}
CHARACTER_TIMELINE_DATA_PATH_MAP = _standardize_data_map(CHARACTER_TIMELINE_DATA_PATH_MAP)

# 캐릭터 능력치 정보 조회
CHARACTER_STATUS_DATA_PATH_MAP = _get_data_path_map('character_status', 'name')

# 캐릭터 장착 장비 조회
CHARACTER_EQUIPMENT_DATA_PATH_MAP = _get_data_path_map('character_equipment', 'slotId')

# 캐릭터 장착 아바타 조회
CHARACTER_AVATAR_DATA_PATH_MAP = _get_data_path_map('character_avatar', 'slotId')

# 캐릭터 장착 크리쳐 조회
CHARACTER_CREATURE_DATA_PATH_MAP = _get_data_path_map('character_creature', 'slotColor')

# 캐릭터 장착 휘장 조회
CHARACTER_FLAG_DATA_PATH_MAP = _get_data_path_map('character_flag')

# 캐릭터 장착 탈리스만 조회
# CHARACTER_TALISMAN_DATA_PATH_MAP = _get_data_path_map('character_talisman')

# 캐릭터 스킬 스타일 조회
# CHARACTER_SKILL_STYLE_DATA_PATH_MAP = _get_data_path_map('character_skill_style')

# 캐릭터 버프 스킬 강화 장착 장비 조회
CHARACTER_BUFF_EQUIPMENT_DATA_PATH_MAP = _get_data_path_map('character_buff_equipment', 'slotId')

# 캐릭터 버프 스킬 강화 장착 아바타 조회
CHARACTER_BUFF_AVATAR_DATA_PATH_MAP = _get_data_path_map('character_buff_avatar', 'slotId')

# 캐릭터 버프 스킬 강화 장착 크리쳐 조회
CHARACTER_BUFF_CREATURE_DATA_PATH_MAP = _get_data_path_map('character_buff_creature')

# 캐릭터 명성 검색
CHARACTER_FAME_DATA_PATH_MAP = {
    'server_id': 'serverId',
    'character_id': 'characterId',
    'character_name': 'characterName',
    'level': 'level',
    'job_id': 'jobId',
    'job_grow_id': 'jobGrowId',
    'job_name': 'jobName',
    'job_grow_name': 'jobGrowName',
    'fame': 'fame'
}
CHARACTER_FAME_DATA_PATH_MAP = _standardize_data_map(CHARACTER_FAME_DATA_PATH_MAP)
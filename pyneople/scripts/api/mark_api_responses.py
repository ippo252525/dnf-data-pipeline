# 해당 스크립트는 api구조 분석을 위한 마킹 스크립트입니다. 
# 사용자 코드에서 import하거나 직접 실행 금지

from dotenv import load_dotenv
import requests
import json
import os

from pyneople.utils.api_utils.api_request_builder import build_api_request
from pyneople.utils.api_utils.url_builder import build_url
from pyneople.utils.common import to_snake_case
from pyneople.config.config import Settings
from pyneople.metadata.metadata_constants import CHARACTER_STATUS_TRANSLATION_MAP
load_dotenv()  

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.abspath(os.path.join(BASE_DIR, '../../api/marked_responses/'))

# # server_id와 character_id만 요구하는 엔드포인트
CHARACTER_BASE_ENDPOINTS = [
    'character_info',
    'character_status',
    'character_equipment',
    'character_avatar',
    'character_creature',
    'character_flag',
    # 'character_talisman', 탈리스만은 2025년 6월경 캐릭터 스킬 개편에 따라 지원하지 않음
    # 'character_skill_style', 아직 미구현
    'character_buff_equipment',
    'character_buff_avatar',
    'character_buff_creature'
]

# 유일 장비를 착용 할 수 있는 부위
HAS_EXALTED_INFO_SLOT_IDS = ['EARRING', 'MAGIC_STON']

def _mark(s):
    s = s.strip('_')
    return f"__{to_snake_case(s)}__"

# 각 엔트포인트에 따른 수동 조정
def _mark_manually(data, key, name = None):
    """ 
    data['key']를 직접 마킹하는 함수
    """
    if data.get(key):
        if name:
            data[key] = _mark(f'{to_snake_case(name)}_{to_snake_case(key)}')
        else:
            data[key] = _mark(key)



def _get_common_identifier_key(data : list, identifier_key : str):
    """
    리스트 내의 모든 원소가 dict이고 모든 dict가 identifier_key를 key로 가지고 있으면 identifier_key를 반환하는 함수
    """
    if all(isinstance(item, dict) for item in data) and all(identifier_key in item for item in data):
        return identifier_key
    return None

def _mark_character_base_info(
        data,
        identifier_key: str = None,
        exclude_to_keys: list = None,
        path="",
        depth=0 
):
    """
    API 응답의 최종 value를 마킹하는 함수.
    
    __data_name__ 식으로 마킹하며 해당 데이터는 data_name : data_path 구조를 가지는 data_path_map을 생성하는 메타데이터로 활용됨
    """
    if identifier_key is None:
        identifier_key = ''
    if exclude_to_keys is None:
        exclude_to_keys = []    
    # 1. dict 처리
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if depth == 0 and key in exclude_to_keys:
                new_path = path
            else:    
                new_path = key if path is None else f"{path}_{key}"
            result[key] = _mark_character_base_info(value, identifier_key, exclude_to_keys ,new_path, depth + 1)
        return result

    # 2. list 처리
    elif isinstance(data, list):

        identifier_key = _get_common_identifier_key(data, identifier_key)
        result = []

        # list 의 모든 원소가 dict이고 identifier_key를 가지고 있는 경우
        if identifier_key:
            for item in data:
                identifier_value = item[identifier_key]
                if identifier_key == 'name':
                    identifier_value = CHARACTER_STATUS_TRANSLATION_MAP[identifier_value]
                new_path = f"{path}_{to_snake_case(identifier_value)}"
                new_item = {}
                for key, value in item.items():
                    if key == identifier_key:
                        new_item[key] = value  # ex) slotId : WEAPON은 유지
                    else:
                        filed_path = f"{new_path}_{key}"     
                        new_item[key] = _mark_character_base_info(value, identifier_key, exclude_to_keys, filed_path, depth + 1)
                result.append(new_item)
        else:
            for index, item in enumerate(data):
                # 리스트의 원소가 1개 인 경우 path에 추가하지 않는다.
                if len(data) == 1:
                    new_path = path
                else:
                    new_path = f"{path}_{index}"
                result.append(_mark_character_base_info(item, identifier_key, exclude_to_keys, new_path, depth + 1))
        return result

    # 3. primitive 처리
    else:
        return _mark(path)

# 중복 마킹 값 검사를 위한 마킹 값 수집 함수
def _extract_all_values(data):
    result = []

    def _extract(obj):
        if isinstance(obj, dict):
            for value in obj.values():
                _extract(value)
        elif isinstance(obj, list):
            for item in obj:
                _extract(item)
        else:
            if obj.startswith('__') and obj.endswith('__'): # 마킹된 값만 추가한다
                result.append(obj)

    _extract(data)
    return result

# 수집된 마킹 값을 바탕으로 중복값이 있는지 확인하는 함수
def _has_duplicates(data):
    values = _extract_all_values(data)
    return len(values) != len(set(values))

# Character Equipment
def _mark_character_equipment_manually(data):
    _mark_manually(data, 'setItemInfo')
    for equipment in data['equipment']:
        slot_id = equipment['slotId']
        
        # 마법부여 정보는 따로 전처리 함수를 이용함
        _mark_manually(equipment, 'enchant', slot_id)
        
        # 유일 장비를 장착 할 수 있는 부위인 경우 해당 key를 추가한다
        if slot_id in HAS_EXALTED_INFO_SLOT_IDS:
            equipment['exaltedInfo'] = {
                'damage' : f"__{to_snake_case(slot_id)}_exalted_info_damage__",
                'buff' : f"__{to_snake_case(slot_id)}_exalted_info_buff__",
                'explain' : f"__{to_snake_case(slot_id)}_exalted_info_explain__"
            }
            equipment['potency'] = {
                'value' : f"__{to_snake_case(slot_id)}_potency_value__",
                'damage' : f"__{to_snake_case(slot_id)}_potency_damage__",
                'buff' : f"__{to_snake_case(slot_id)}_potency_buff__"
            }
                
    return data

# Character Avatar
def _mark_character_avatar_manually(data):
    for equipment in data['avatar']:
        slot_id = equipment['slotId'].lower()
        _mark_manually(equipment, 'clone', slot_id)
    return data

# Character Flag
def _mark_character_flag_manually(data):
    _mark_manually(data['flag'], 'reinforceStatus')
    return data

# Character Buff
def _mark_charater_buff_manually(data):
    _mark_manually(data['skill']['buff'], 'skillInfo')
    return data

# 엔드포인트에 따른 식별 key를 반환하는 dict
ENDPOINT_TO_IDENTIFIER_KEY = {
    'character_status' : 'name',
    'character_equipment' : 'slotId',
    'character_avatar' : 'slotId',
    'character_creature' : 'slotColor',
    'character_buff_equipment' : 'slotId',
    'character_buff_avatar' : 'slotId'
}

# 엔드포인트에 따른 최상단에서 제외 할 key들을 반환하는 dict
ENDPOINT_TO_EXCLUDE_TOP_KEYS = {
    'character_equipment' : ["equipment"],
    'character_avatar' : ['avatar'],
    'character_creature' : ['creature'],
    'character_flag' : ['flag'],
    'character_buff_equipment' : ['skill'],
    'character_buff_avatar' : ['skill'],
    'character_buff_creature' : ['skill']
}

# 엔드포인트로 각 수동 마킹 함수를 매핑하는 dict
ENDPOINT_TO_MANUAL_MARK_FUNCTION = {
    'character_equipment' : _mark_character_equipment_manually,
    'character_avatar' : _mark_character_avatar_manually,
    'character_flag' : _mark_character_flag_manually,
    'character_buff_equipment' : _mark_charater_buff_manually,
    'character_buff_avatar' : _mark_charater_buff_manually,
    'character_buff_creature' : _mark_charater_buff_manually,
} 


# 해당 엔드포인트 마킹 후 저장
if __name__ == "__main__":
    for endpoint in CHARACTER_BASE_ENDPOINTS:
        identifier_key = ENDPOINT_TO_IDENTIFIER_KEY.get(endpoint)
        exclude_top_keys = ENDPOINT_TO_EXCLUDE_TOP_KEYS.get(endpoint)
        manual_mark_function = ENDPOINT_TO_MANUAL_MARK_FUNCTION.get(endpoint)
        api_request = build_api_request(endpoint, apikey=Settings.API_KEYS[0], serverId=os.getenv('SAMPLE_SERVER_ID'), characterId=os.getenv('SAMPLE_CHARACTER_ID'))
        url = build_url(api_request)
        response = requests.get(url)
        data = response.json()
        file_path = os.path.join(SAVE_DIR, f"{endpoint}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            # 기본 정보 마킹
            data = _mark_character_base_info(data, identifier_key, exclude_top_keys)
            # 엔드포인트에 따른 추가 정보 마킹
            if manual_mark_function:
                data = manual_mark_function(data)
            # 중복 여부 확인
            if _has_duplicates(data):
                raise ValueError("중복된 마킹 값이 존재합니다.")
            json.dump(data, f, ensure_ascii=False, indent=2)    
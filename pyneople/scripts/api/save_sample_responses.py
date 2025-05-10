from pyneople.utils.api_utils.api_request_builder import build_api_request
from pyneople.utils.api_utils.url_builder import build_url
import requests
import json
import os
from pyneople.config.config import Settings
from pyneople.metadata.metadata_constants import HAS_EXALTED_INFO_SLOT_IDS
from pyneople.scripts.api.mark_api_responses import CHARACTER_BASE_ENDPOINTS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.abspath(os.path.join(BASE_DIR, '../../api/sample_responses/'))

for endpoint in CHARACTER_BASE_ENDPOINTS:
    response = requests.get(
    build_url(
        build_api_request(
            endpoint, 
            Settings.API_KEYS[0], 
            serverId = Settings.SAMPLE_SERVER_ID, 
            characterId = Settings.SAMPLE_CHARACTER_ID)))
    data = response.json()
    
    file_path = os.path.join(SAVE_DIR, f"{endpoint}.json")
    
    if endpoint == 'character_equipment':
        
        for equipment in data['equipment']:
            
            if equipment.get('upgradeInfo'):
                # 모든 장비 융합석 정보를 세트 융합석으로
                equipment['upgradeInfo'] = {
                    "itemId": "b02eb44e29cab6fb6c3761749ee3f601",
                    "itemName": "정화 : 혹한을 녹이는 따스한 빛",
                    "itemRarity": "에픽",
                    "setItemId": "11f7d203a05ea6f13300c0facb39f11e",
                    "setItemName": "칠흑의 정화 세트",
                    "setPoint": 65
                    }
                
            if equipment.get('tune'):
                # 모든 조율 정보에 upgrade 추가
                if equipment['tune'][0].get('upgrade') is not False:
                    equipment['tune'][0]['upgrade'] = None

            # 유일 장비 정보 추가
            if equipment.get('slotId') in HAS_EXALTED_INFO_SLOT_IDS:
                equipment["exaltedInfo"] = {
                    "damage": "38.4%",
                    "buff": 11220,
                    "explain": "<나벨의 기억>\n장착 중인 가장 높은 세트 포인트 2100점 이상에서만 능력을 발휘합니다.\n세트 포인트 2550이상 달성 시 더 강한 효과가 발동됩니다."
                    }
                equipment["potency"] = {
                    "value": 100,
                    "damage": "10%",
                    "buff": 4650
                    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
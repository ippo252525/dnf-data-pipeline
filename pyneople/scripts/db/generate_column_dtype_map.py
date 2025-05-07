"""
endpoint 별로 column 을 key로 data_type를 value로 가지는 dict생성 후 json파일로 저장하는 함수
"""
import re
import os
import json
from datetime import datetime, timezone
import requests
import pyneople.api.registry.endpoint_class
from pyneople.api.registry.endpoint_registry import EndpointRegistry
from pyneople.utils.api_utils.extract_values import _get_nested_value
from pyneople.utils.api_utils.url_builder import build_url
from pyneople.utils.api_utils.api_request_builder import build_api_request
from pyneople.config.config import Settings


def recommend_type(value):
    """
    SAMPLE CASE 의 실제 데이터를 받아서 해당 데이터에 맞는 SQL data type을 반환하는 함수
    스테이징 테이블에만 쓰이는 관계로 최대한 여유롭게 처리함
    """
    if isinstance(value, bool):
        return "BOOLEAN"
    elif isinstance(value, int):
        return "INT"
    elif isinstance(value, float):
        return "REAL"
    elif isinstance(value, str):
        if re.fullmatch(r"[0-9a-f]{32}", value):
            return "CHAR(32)"
        try:
            datetime.fromisoformat(value)
            return "TIMESTAMP WITH TIME ZONE"
        except ValueError:
            pass
        try:
            json.loads(value)
            return "JSONB"
        except(json.JSONDecodeError, TypeError):
            pass
        return "TEXT"    
    elif isinstance(value, datetime):
        return "TIMESTAMP WITH TIME ZONE"
    elif value is None:
        return "TEXT"
    else:
        return "TEXT"

if __name__ == '__main__':
    endpoint_to_column_dtype_map = {}
    endpoints = EndpointRegistry.get_registered_endpoints()
    for endpoint in endpoints:
        endpoint_column_dtype_dict = {}
        # 해당 데이터는 직접 입력
        if endpoint in ['character_fame', 'character_timeline']:
            continue
        endpoint_class = EndpointRegistry.get_class(endpoint)
        columns = endpoint_class.data_path_map.keys()
        api_request = build_api_request(endpoint, apikey=Settings.API_KEYS[0], serverId=Settings.SAMPLE_SERVER_ID, characterId=Settings.SAMPLE_CHARACTER_ID)
        url = build_url(api_request)
        response = requests.get(url)
        data = response.json()
        data.update({'fetched_at' : datetime.now(timezone.utc)})
        for column in columns:
            try:
                value = _get_nested_value(data, endpoint_class.data_path_map[column])
            except Exception as e:
                print(f"column : {column}, path : {endpoint_class.data_path_map[column]}, error : {e}")
                if column in ["magic_ston_exalted_info_buff", "magic_ston_potency_value", "magic_ston_potency_buff"
                              "earring_exalted_info_buff", "earring_potency_value", "earring_potency_buff"]:
                    value = 100
                else:    
                    value = None
            endpoint_column_dtype_dict.update({column : recommend_type(value)})
        endpoint_to_column_dtype_map[endpoint] = endpoint_column_dtype_dict

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SAVE_DIR = os.path.abspath(os.path.join(BASE_DIR, '../../db/'))
    file_path = os.path.join(SAVE_DIR, "endpoint_to_column_dtype_map.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(endpoint_to_column_dtype_map, f, ensure_ascii=False, indent=2) 
from pyneople.utils.api_utils.extract_values import extract_values
from pyneople.api.data_path_map import CHARACTER_TIMELINE_DATA_PATH_MAP
from pyneople.metadata.metadata_constants import TIMELINE_CODE_TO_KEYS_MAP
from pyneople.metadata.metadata_generated import CLICKHOUSE_TABLE_COLUMNS_MAP
from pyneople.utils.common import to_snake_case
from datetime import datetime, date
from zoneinfo import ZoneInfo
import json

KST = ZoneInfo('Asia/Seoul')
UTC = ZoneInfo('UTC')

def preprocess_character_timeline(data : dict, columns : list):
    data = [
            {
                **timeline_data, 
                'fetched_at' : data['fetched_at'].replace(tzinfo=ZoneInfo("UTC")),
                'serverId' : data['serverId'],
                'characterId' : data['characterId']
            } 
            for timeline_data in data['timeline']['rows']
        ]
    for character_timeline in data:
        character_timeline['date'] = datetime.strptime(character_timeline['date'], '%Y-%m-%d %H:%M').replace(tzinfo=KST).astimezone(UTC)
        character_timeline['data'] = json.dumps(character_timeline['data'])
    return [extract_values(timeline_data, columns, CHARACTER_TIMELINE_DATA_PATH_MAP) for timeline_data in data] 


def flatten_character_timeline(data : dict, clickhouse_columns : list):
    """
    PostgreSQL staging_character_timeline 테이블에 저장 된 값을 불러와서 clickhouse에 저장할 수 있는 형태로 변환하는 함수
    """
    result = {'server_id' : data[0], 'character_id' : data[1], 'timeline_code' : data[2], 'timeline_name' : data[3], 'timeline_date' : data[4]}
    timeline_data = data[5]
    for key in TIMELINE_CODE_TO_KEYS_MAP[result.get('timeline_code')]:
        value = timeline_data.get(key)
        result[f'timeline_data_{to_snake_case(key)}'] = value
    return tuple(result.get(column) for column in clickhouse_columns[1:])

def _preprocess_character_timeline_clickhouse(data : dict):
    """
    clickhouse 저장을 위한 단일 타임라인 데이터 전처리 함수
    """
    try:
        result = {'timeline_code' : data['code'], 'timeline_name' : data['name'], 'timeline_date' : datetime.strptime(data['date'], '%Y-%m-%d %H:%M')}
        if data.get('data'):
            for key in TIMELINE_CODE_TO_KEYS_MAP.get(data['code']):
                value = data['data'].get(key)
                if isinstance(value, (list, dict)):
                    if key in ['ticket', 'itemObtainInfo']:
                        value = value.get('itemName')
                    elif key == 'resultItems':
                        value = value[0].get('itemName')
                result[f'timeline_data_{to_snake_case(key)}'] = value    
            return result    
        else:
            return result
    except Exception as e:
        print(f"Error processing data: {data}, Error: {e}")
        print(f"Error processing data: {data.get('data')}, Error: {e}")
        raise

def preprocess_character_timeline_clickhouse_batch(doc : dict, snapshot_date : date):
    character_id = doc['characterId']
    server_id = doc['serverId']
    doc = doc['timeline']['rows']
    doc = [{
        'server_id' : server_id,
        'character_id' : character_id,
        **_preprocess_character_timeline_clickhouse(timeline_data)
    } for timeline_data in doc]
    doc = [tuple(row.get(column) for column in CLICKHOUSE_TABLE_COLUMNS_MAP['character_timeline'][1:]) for row in doc]
    doc = [(snapshot_date, *row) for row in doc]
    return doc
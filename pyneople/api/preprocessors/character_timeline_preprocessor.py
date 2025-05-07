from pyneople.utils.api_utils.extract_values import extract_values
from pyneople.api.data_path_map import CHARACTER_TIMELINE_DATA_PATH_MAP
from datetime import datetime
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


    
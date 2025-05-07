from pyneople.api.data_path_map import CHARACTER_AVATAR_DATA_PATH_MAP
from pyneople.utils.api_utils.extract_values import extract_values
from zoneinfo import ZoneInfo

def preprocess_character_avatar(data : dict, columns : list):
    data = extract_values(data, columns, CHARACTER_AVATAR_DATA_PATH_MAP)
    data['fetched_at'] = data['fetched_at'].replace(tzinfo=ZoneInfo("UTC"))
    
    if any(column.endswith('clone') for column in columns):
        # print([column for column in columns if column.endswith('clone')])
        for column in [column for column in columns if column.endswith('clone')]:
            if data.get(column):
                data[column] = data[column].get('itemName')
    if data.get('aura_skin_emblems'):
       data['aura_skin_emblems'] = None
    return data
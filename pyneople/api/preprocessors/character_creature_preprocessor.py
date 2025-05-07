from pyneople.api.data_path_map import CHARACTER_CREATURE_DATA_PATH_MAP
from pyneople.utils.api_utils.extract_values import extract_values
from zoneinfo import ZoneInfo

def preprocess_character_creature(data : dict, columns : list):
    data = extract_values(data, columns, CHARACTER_CREATURE_DATA_PATH_MAP)
    data['fetched_at'] = data['fetched_at'].replace(tzinfo=ZoneInfo("UTC"))
    return data
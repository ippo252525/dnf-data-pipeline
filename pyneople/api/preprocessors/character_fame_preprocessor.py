from pyneople.utils.api_utils.extract_values import extract_values
from pyneople.api.data_path_map import CHARACTER_FAME_DATA_PATH_MAP
from zoneinfo import ZoneInfo

def preprocess_character_fame(data : dict, columns : list):
    data = [{**character_data, 'fetched_at' : data['fetched_at'].replace(tzinfo=ZoneInfo("UTC"))} for character_data in  data['rows']]
    return [extract_values(character_data, columns, CHARACTER_FAME_DATA_PATH_MAP) for character_data in data]
    
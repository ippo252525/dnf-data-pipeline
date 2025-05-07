from pyneople.api.data_path_map import CHARACTER_BUFF_CREATURE_DATA_PATH_MAP
from pyneople.utils.api_utils.extract_values import extract_values
from pyneople.utils.common import format_buff_skill_info, format_enchant_info
from zoneinfo import ZoneInfo

def preprocess_character_buff_creature(data : dict, columns : list):
    data = extract_values(data, columns, CHARACTER_BUFF_CREATURE_DATA_PATH_MAP)
    data['fetched_at'] = data['fetched_at'].replace(tzinfo=ZoneInfo("UTC"))
    if data.get('skill_info'):
        data['skill_info'] = format_buff_skill_info(data['skill_info'])    
    if data.get('buff_creature_enchant'):
        data['buff_creature_enchant'] = format_enchant_info(data['buff_creature_enchant'])
    return data
    
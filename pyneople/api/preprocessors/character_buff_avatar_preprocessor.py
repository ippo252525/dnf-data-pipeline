from pyneople.api.data_path_map import CHARACTER_BUFF_AVATAR_DATA_PATH_MAP
from pyneople.utils.api_utils.extract_values import extract_values
from pyneople.utils.common import format_buff_skill_info
from zoneinfo import ZoneInfo

def preprocess_character_buff_avatar(data : dict, columns : list):
    data = extract_values(data, columns, CHARACTER_BUFF_AVATAR_DATA_PATH_MAP)
    data['fetched_at'] = data['fetched_at'].replace(tzinfo=ZoneInfo("UTC"))
    if data.get('skill_info'):
        data['skill_info'] = format_buff_skill_info(data['skill_info'])
    return data
    
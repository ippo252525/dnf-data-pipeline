from pyneople.api.data_path_map import CHARACTER_BUFF_EQUIPMENT_DATA_PATH_MAP
from pyneople.utils.api_utils.extract_values import extract_values
from pyneople.utils.common import format_buff_equipment_info
from zoneinfo import ZoneInfo

def preprocess_character_buff_equipment(data : dict, columns : list):
    job_name = data.get('jobName')
    # 노전직의 경우 버프 자체가 없다
    if data.get('skill', {}).get('buff'):
        buff_name = data.get('skill', {}).get('buff', {}).get('skillInfo', {}).get('name')
    data = extract_values(data, columns, CHARACTER_BUFF_EQUIPMENT_DATA_PATH_MAP)
    data['fetched_at'] = data['fetched_at'].replace(tzinfo=ZoneInfo("UTC"))
    if data.get('equipment'):
        data['equipment'] = format_buff_equipment_info(data['equipment'], buff_name, job_name)
    return data

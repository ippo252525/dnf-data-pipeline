from pyneople.api.data_path_map import CHARACTER_BUFF_EQUIPMENT_DATA_PATH_MAP
from pyneople.metadata.metadata_constants import EXORCIST_JOB_GROW_NAMES
from pyneople.utils.api_utils.extract_values import extract_values
from pyneople.utils.common import format_buff_equipment_info
from zoneinfo import ZoneInfo

def preprocess_character_buff_equipment(data : dict, columns : list):
    job_name = data.get('jobName')
    # 노전직의 경우 버프 자체가 없다
    if data.get('skill', {}).get('buff'):
        buff_name = data.get('skill', {}).get('buff', {}).get('skillInfo', {}).get('name')
        # 버프가 있어도 buff_name이 None인 케이스가 있다 ex) 퇴마사 봉마연희
        if buff_name is None :
            if data['jobGrowName'] in EXORCIST_JOB_GROW_NAMES:
                buff_name = '봉마연희'
            else:
                #TODO : 전직 명에 따른 버프 이름 매핑해서 buff_name 이 None인 케이스에도 buff_name 문자열로 할당 되도록 한다.
                buff_name = '버프 이름 미상'
                
    data = extract_values(data, columns, CHARACTER_BUFF_EQUIPMENT_DATA_PATH_MAP)
    data['fetched_at'] = data['fetched_at'].replace(tzinfo=ZoneInfo("UTC"))
    if data.get('equipment'):
        data['equipment'] = format_buff_equipment_info(data['equipment'], buff_name, job_name)
    return data

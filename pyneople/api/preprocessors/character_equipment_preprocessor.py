from pyneople.api.data_path_map import CHARACTER_EQUIPMENT_DATA_PATH_MAP
from pyneople.utils.api_utils.extract_values import extract_values
from pyneople.utils.common import format_enchant_info, format_fusion_option_info
from zoneinfo import ZoneInfo

def preprocess_character_equipment(data : dict, columns : list):
    data = extract_values(data, columns, CHARACTER_EQUIPMENT_DATA_PATH_MAP)
    data['fetched_at'] = data['fetched_at'].replace(tzinfo=ZoneInfo("UTC"))
    
    # 세트 아이템 정보는 세트이름||세트포인트 문자열로 반환
    if data.get('set_item_info') and isinstance(data['set_item_info'], list):
        if data['set_item_info'][0]['active'].get('setPoint'):
            data['set_item_info'] = f"{data['set_item_info'][0]['setItemName']}||{data['set_item_info'][0]['active']['setPoint']['current']}"
        else:
            data['set_item_info'] = None
            
    # 마법부여 정보 정리
    if any(column.endswith('enchant') for column in columns):
        for column in [column for column in columns if column.endswith('enchant')]:
            data[column] = format_enchant_info(data[column])
    
    # 융합 옵션 정보 정리
    if any(column.endswith('fusion_option') for column in columns):
        for column in [column for column in columns if column.endswith('fusion_option')]:
            data[column] = format_fusion_option_info(data[column])    
    return data

    
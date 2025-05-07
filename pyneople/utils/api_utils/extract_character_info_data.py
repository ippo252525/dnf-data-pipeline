from pyneople.api.data_path_map import CHARACTER_INFO_DATA_PATH_MAP

def extract_character_info_data(data : dict):
    """데이터에서 캐릭터 정보를 추출해서 반환하는 함수"""
    data = data['data']
    character_info_keys = [key[0] for key in CHARACTER_INFO_DATA_PATH_MAP.values()]
    return {key : data[key] for key in character_info_keys}

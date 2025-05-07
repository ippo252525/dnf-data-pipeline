from typing import Optional

def build_next_character_timeline_api_request(data : dict, api_request : dict) -> Optional[dict]: 
    """
    timeline 응답의 next 값을 기반으로 다음 API request parameters를 설정하는 함수

    next 값이 존재하면 해당 값을 request parameter로 추가하고, 없으면 None 반환

    Args:
        data (dict): Neople Open API 응답 데이터. 'timeline' key와 그 안의 'next' 값을 포함함
        api_request (dict): endpoint와 request parameters를 key로 가지는 dict

    Returns:
        Optional[dict]: 수정된 api_request dict 또는 None
    """
    # next가 있는 경우 next를 추가하고 아니면 None반환
    if data['timeline']['next']:
        api_request['params']['next'] = data['timeline']['next']
        return api_request
    else:
        return None
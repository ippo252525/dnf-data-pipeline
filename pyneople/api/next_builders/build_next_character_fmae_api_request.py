from typing import Optional

def build_next_character_fame_api_request(data : dict, api_request : dict) -> Optional[dict]:
    """
    캐릭터 명성 데이터를 기준으로 다음 API request parameters를 설정하는 함수

    주어진 데이터가 200개 이상이면 마지막 명성 값을 기준으로 maxFame을 조정하고,
    200개 미만이면 전체 명성 범위의 최소값보다 1 작은 값을 설정함.
    maxFame이 0 이하인 경우 None 반환

    Args:
        data (dict): Neople Open API 응답 데이터.
        api_request (dict): endpoint와 request parameters를 key로 가지는 dict

    Returns:
        Optional[dict]: 수정된 api_request dict 또는 None
    """
    if len(data['rows']) >= 200:
        # 200개는 제일 작은 값부터 다시 조회
        api_request['params']['maxFame'] = data['rows'][-1]['fame']
        
        if data['rows'][0]['fame'] ==  data['rows'][-1]['fame']:
            # 모든 명성 값이 같은 경우는 1만 빼고 다시 조회
            api_request['params']['maxFame'] = data['rows'][0]['fame'] - 1
    else:
        # 200개 미만이면 최소명성 - 1 부터 조회
        api_request['params']['maxFame'] = data['fame']['min'] - 1    
    
    if api_request['params']['maxFame'] <= 0:
        return None
    else:
        return api_request
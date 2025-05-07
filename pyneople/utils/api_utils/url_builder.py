from pyneople.api.endpoint_definitions import ENDPOINT_DEFINITIONS

def build_url(api_request : dict) -> str:
    """ENDPOINT_DEFINITIONS 정보를 기반으로 URL을 생성합니다.
    Args:
        api_request (dict): API 요청 정보. 'endpoint'와 'params'를 포함해야 합니다.
    Returns:
        str: 생성된 URL.
    Raises:
        ValueError: 잘못된 API 요청 정보가 제공된 경우.
    """
    template = ENDPOINT_DEFINITIONS.get(api_request['endpoint'])
    if not template:
        raise ValueError(f"Unknown endpoint: {api_request['endpoint']}")
    
    filled_params = {**template['default_params'], **api_request['params']}
    return template.get('url').format(**filled_params)
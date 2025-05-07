def build_api_request(endpoint : str, apikey : str, **kwargs):
    """
    api_request dict를 생성해 주는 함수
    
    Args:
        endpoint(str): 엔드포인트
        apikey(str): API key
        **kwargs: 요청 파라미터로 들어갈 값
    Returns:
        dict: endpoint, parmas를 key로 가지는 api_request
    """
    return {
        'endpoint' : endpoint,
        'params' : {
            **kwargs,
            'apikey' : apikey
        }
    }
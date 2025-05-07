class EndpointRegistry:
    """엔드포인트 이름과 클래스 매핑을 관리하는 레지스트리 클래스."""
    _registry = {}

    @classmethod
    def register(cls, name: str, endpoint_cls):
        """엔드포인트 클래스를 레지스트리에 등록합니다.

        Args:
            name (str): 엔드포인트를 식별하는 문자열 이름.
            endpoint_cls (Type): 등록할 엔드포인트 클래스 객체.
        """        
        cls._registry[name] = endpoint_cls

    @classmethod
    def get_class(cls, endpoint_name: str):
        """엔드포인트 이름으로 등록된 클래스를 조회합니다.

        Args:
            endpoint_name (str): 조회할 엔드포인트 이름.

        Returns:
            Type: 등록된 엔드포인트 클래스.

        Raises:
            ValueError: 등록되지 않은 엔드포인트 이름을 조회할 경우 발생합니다.
        """        
        try:
            return cls._registry[endpoint_name]
        except KeyError:
            raise ValueError(f"해당 클래스는 등록되어 있지 않습니다 '{endpoint_name}'")

    @classmethod
    def get_registered_endpoints(cls):
        return list(cls._registry.keys())

def register_endpoint(name: str):
    """클래스를 엔드포인트 레지스트리에 자동 등록하는 데코레이터입니다.

    Args:
        name (str): 등록할 엔드포인트의 이름.

    Returns:
        Callable: 데코레이터 함수. 클래스를 받아서 자동 등록합니다.
    """    
    def decorator(cls):
        EndpointRegistry.register(name, cls)
        return cls
    return decorator
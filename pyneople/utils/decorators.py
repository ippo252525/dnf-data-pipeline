import time
import functools
import logging
import asyncio

logger = logging.getLogger(__name__)

def log_execution_time(metric_name: str):
    """
    함수 실행 시간을 로깅하는 데코레이터

    - 비동기/동기 함수 자동 지원
    - 클래스 메서드인 경우 self.name을 로그에 자동 포함

    Args:
        metric_name (str): 로그 태그용 메트릭 이름

    Returns:
        Callable: 데코레이터 함수
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.perf_counter()
                duration = end - start

                name = _extract_name(args)
                logger.info(f"[{name}{metric_name}] 실행 시간: {duration:.2f}초")

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                end = time.perf_counter()
                duration = end - start

                name = _extract_name(args)
                logger.info(f"[{name}{metric_name}] 실행 시간: {duration:.2f}초")

        def _extract_name(args):
            if args and hasattr(args[0], "name"):
                return f"{args[0].name} "
            return ""

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
import asyncpg
from pyneople.config.config import Settings

# 현재 사용하지 않는 클래스
class PSQLConnectionManager:
    """
    이 클래스는 PostgreSQL 데이터베이스와의 연결을 관리합니다.
    단일 코루틴 에서 연결을 생성하고, 커넥션 풀을 사용하여 여러 요청을 처리합니다.
    """
    _pool = None

    @classmethod
    async def init_pool(cls):
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                user=Settings.POSTGRES_USER,
                password=Settings.POSTGRES_PASSWORD,
                database=Settings.POSTGRES_DB,
                host=Settings.POSTGRES_HOST,
                port=Settings.POSTGRES_PORT
            )

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            raise RuntimeError("PSQL Pool not initialized. Call init_pool() first.")
        return cls._pool
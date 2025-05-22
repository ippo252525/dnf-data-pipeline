from pyneople.utils.db_utils.psql_connection import psql_connection

import logging
# logging 설정
logger = logging.getLogger(__name__)

def truncate_tables(table_names : str | list[str], cascade : bool = False):
    """
    PostgreSQL에서 지정된 테이블을 비우는 함수

    Args:
        table_names (str | list[str]): 비울 테이블의 이름
    """
    if isinstance(table_names, str):
        table_names = [table_names]
    with psql_connection() as conn:
        with conn.cursor() as cur:
            for table_name in table_names:
                if cascade:
                    cur.execute(f"TRUNCATE TABLE {table_name} CASCADE")
                else:
                    cur.execute(f"TRUNCATE TABLE {table_name}") 
                logger.info(f"Truncated table: {table_name}")
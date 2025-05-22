from pyneople.utils.db_utils.psql_connection import psql_connection
from pyneople.config.config import Settings
import clickhouse_connect
from datetime import date
from typing import Callable


import logging
logger = logging.getLogger(__name__)


def psql_to_clickhouse(
    sql: str,
    snapshot_date: date,
    click_house_table_name: str,
    click_house_column_names: list[str] = '*',
    preprocess_func: Callable | None = None,
    batch_size: int = 10000
):
    """
    PostgreSQL에서 ClickHouse로 데이터 이동
    Args:
        sql (str): PostgreSQL에서 데이터를 가져오기 위한 SQL 쿼리
        snapshot_date (date): 스냅샷 날짜
        click_house_table_name (str): ClickHouse 테이블 이름
        click_house_column_names (list[str]): ClickHouse 테이블의 컬럼 이름
    """
    # ClickHouse 연결
    ch_client = clickhouse_connect.get_client(
        host=Settings.CLICK_HOUSE_HOST,
        port=Settings.CLICK_HOUSE_PORT,
        username=Settings.CLICK_HOUSE_USER_NAME,
        password=""
    )
    count = 0
    with psql_connection() as conn:
        with conn.cursor(name="server_side_cursor") as cur:
            cur.execute(sql)
            while True:
                rows = cur.fetchmany(batch_size)
                if not rows:
                    break
                rows = [(snapshot_date, *preprocess_func(row, click_house_column_names)) for row in rows]
                ch_client.insert(click_house_table_name, rows, click_house_column_names)
                count += 1
                logger.info(f"{click_house_table_name} : {count}번 batch 삽입 완료")
    logger.info("psql_to_clickhouse 완료")

if __name__ == "__main__":
    psql_to_clickhouse(
        sql = """
            SELECT DISTINCT ON (character_id, server_id)
                character_id,
                server_id,
                character_name,
                level,
                job_name,
                job_grow_name,
                fame
            FROM staging_character_fame
            ORDER BY character_id, server_id, fetched_at DESC;
            """,
        snapshot_date = date.today(),
        click_house_table_name='character_fame_history'
    )
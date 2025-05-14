from pyneople.utils.db_utils.psql_connection import psql_connection
from pyneople.config.config import Settings
import clickhouse_connect
from datetime import date


import logging
logger = logging.getLogger(__name__)


def psql_to_clickhouse(
        sql : str,
        snapshot_date : date,
        click_house_table_name : str,
        click_house_column_names : list[str] = '*'
):

    # ClickHouse 연결
    ch_client = clickhouse_connect.get_client(
        host=Settings.CLICK_HOUSE_HOST,
        port=Settings.CLICK_HOUSE_PORT,
        username=Settings.CLICK_HOUSE_USER_NAME,
        password=""
    )

    with psql_connection() as conn:
        cur = conn.cursor()
        # PostgreSQL에서 데이터 가져오기
        cur.execute(sql)
        batch_size = 10000
        count = 0
        while True:
            rows = cur.fetchmany(batch_size)
            if not rows:
                break
            rows = [(snapshot_date, *row) for row in rows]
            # ClickHouse로 데이터 적재
            ch_client.insert(click_house_table_name, rows, click_house_column_names)
            count += 1
            logger.info(f"{count} bacth insert 완료")

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

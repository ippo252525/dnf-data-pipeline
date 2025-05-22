import psycopg2
from psycopg2.extras import execute_values
from pyneople.config.config import Settings
from pyneople.utils.db_utils.psql_connection import psql_connection

base_sql = """
SELECT character_id, server_id, character_name, level,
       job_name, job_grow_name, fame, fetched_at
FROM staging_character_fame
WHERE MOD(ABS(HASHTEXT(server_id || ':' || character_id)), {n_partitions}) = {worker_id};
"""

upsert_sql = """
INSERT INTO character (
    character_id, server_id, character_name, level,
    job_name, job_grow_name, fame, fetched_at
)
VALUES %s
ON CONFLICT (character_id, server_id) DO UPDATE
SET
    character_name = EXCLUDED.character_name,
    level = EXCLUDED.level,
    job_name = EXCLUDED.job_name,
    job_grow_name = EXCLUDED.job_grow_name,
    fame = EXCLUDED.fame,
    fetched_at = EXCLUDED.fetched_at,
    is_active = TRUE
WHERE
    character.character_name IS DISTINCT FROM EXCLUDED.character_name OR
    character.level IS DISTINCT FROM EXCLUDED.level OR
    character.job_name IS DISTINCT FROM EXCLUDED.job_name OR
    character.job_grow_name IS DISTINCT FROM EXCLUDED.job_grow_name OR
    character.fame IS DISTINCT FROM EXCLUDED.fame;
"""

def psql_batch_upsert(worker_id: int, n_partitions: int = 4, batch_size: int = 10000):
    count = 0
    with psql_connection() as select_conn:
        # cur = select_conn.cursor(name=f"character_stream_{worker_id}")
        cur = select_conn.cursor(name="character_stream")
        # cur = select_conn.cursor()
        # cur.execute(base_sql.format(n_partitions=n_partitions, worker_id=worker_id))
        cur.execute("SELECT character_id, server_id, character_name, level, job_name, job_grow_name, fame, fetched_at FROM staging_character_fame")
        with psql_connection() as upsert_conn:
            while True:
                batch = cur.fetchmany(batch_size)
                if not batch:
                    break
                
                with upsert_conn.cursor() as upsert_cur:
                    execute_values(upsert_cur, upsert_sql, batch)
                    upsert_conn.commit()
                    count += len(batch)
                    print(f"{count} streaming complete.")

if __name__ == "__main__":
    psql_batch_upsert()
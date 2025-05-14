from pyneople.utils.db_utils.psql_connection import psql_connection

def truncate_tables(table_names : str | list[str]):
    if isinstance(table_names, str):
        table_names = [table_names]
    with psql_connection() as conn:
        cur = conn.cursor()
        for table_name in table_names:
            cur.execute(f'TRUNCATE TABLE {table_name};')
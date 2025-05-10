import os
from pyneople.utils.db_utils.psql_connection import psql_connection
from pyneople.utils.db_utils.execute_sql_file import execute_sql_file

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(BASE_DIR, '../../db/schema/main_tables')
    sql_files = [
            os.path.join(folder_path, f) 
            for f in os.listdir(folder_path)
            if f.endswith(".sql")
        ]
    with psql_connection() as conn:
        with conn.cursor() as cur:
            for sql_path in sql_files:
                execute_sql_file(sql_path, cur)

if __name__ == "__main__":
    main()
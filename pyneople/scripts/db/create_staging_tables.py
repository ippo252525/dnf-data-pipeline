import os
from pyneople.utils.db_utils.psql_connection import psql_connection

def run_sql_file(file_path, conn):
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    print(f"Executed: {file_path}")

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(BASE_DIR, '../../db/schema/staging_tables')
    sql_files = [
            os.path.join(folder_path, f) 
            for f in os.listdir(folder_path)
            if f.endswith(".sql")
        ]
    with psql_connection() as conn:
        for sql_path in sql_files:
            run_sql_file(sql_path, conn)


if __name__ == "__main__":
    main()
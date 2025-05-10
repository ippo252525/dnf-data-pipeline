"""
.env.local에 정의된 psql의 모든 스테이징 테이블을 삭제하고 db/schema/staging_tables 폴더의 모든 CREATE TABLE sql 파일을 실행시키는 스크립트
"""
import os 
from pyneople.utils.db_utils.psql_connection import psql_connection
from pyneople.config.config import Settings
from pyneople.utils.db_utils.execute_sql_file import execute_sql_file


def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    staging_table_folder_path = os.path.join(BASE_DIR, '../../db/schema/staging_tables')
    staging_table_sql_files = [
            os.path.join(staging_table_folder_path, f) 
            for f in os.listdir(staging_table_folder_path)
            if f.endswith(".sql")
            ]
    
    with psql_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = '{Settings.POSTGRES_SCHEMA}' AND tablename LIKE 'staging%';
            """)
            tables = cur.fetchall()
            tables = [i[0] for i in tables]
            # 모든 스테이징 테이블 삭제 DROP    
            for staging_table_name in tables:
                cur.execute(f'DROP TABLE IF EXISTS "{staging_table_name}";')
            
            # 모든 스테이징 테이블 생성
            for sql_path in staging_table_sql_files:
                execute_sql_file(sql_path, cur)

if __name__ == "__main__":
    main()
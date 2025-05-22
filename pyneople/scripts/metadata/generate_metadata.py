import psycopg2
import os
import json
import requests
import clickhouse_connect
from pyneople.config.config import Settings
from pyneople.metadata.metadata_constants import SERVER_ID_LIST, NO_JOG_GROW_JOB_IDS
from pyneople.utils.api_utils.api_request_builder import build_api_request
from pyneople.utils.api_utils.url_builder import build_url
from pyneople.utils.db_utils.postgresql import psql_connection

# === 설정 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, '../../metadata/metadata_generated.json')

metadata = dict()

# PostgreSQL 테이블 컬럼 정보 받아오기
metadata['psql_table_columns_map'] = dict()

with psql_connection() as conn:
    SCHEMA = Settings.POSTGRES_SCHEMA
    query = """
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE table_schema = %s
        AND column_default IS NULL
    ORDER BY table_name, ordinal_position;
    """
    with conn.cursor() as cur:
        cur.execute(query, (SCHEMA,))
        rows = cur.fetchall()

for table_name, column_name in rows:
    metadata['psql_table_columns_map'].setdefault(table_name, []).append(column_name)

# Clickhouse 테이블 컬럼 정보 받아오기
metadata['clickhouse_table_columns_map'] = dict()
ch_client = clickhouse_connect.get_client(
    host=Settings.CLICK_HOUSE_HOST,
    port=Settings.CLICK_HOUSE_PORT,
    username=Settings.CLICK_HOUSE_USER_NAME,
    password=""
)
tables = ch_client.query(f"SELECT name FROM system.tables WHERE database = '{Settings.CLICK_HOUSE_USER_NAME}'")
table_names = [row[0] for row in tables.result_rows]

for table_name in table_names:
    columns = ch_client.query(f"DESCRIBE TABLE {Settings.CLICK_HOUSE_USER_NAME}.{table_name}") 
    columns = [row[0] for row in columns.result_rows] 
    metadata['clickhouse_table_columns_map'][table_name] = columns

# 직업 정보 받아오기
metadata['params_for_seed_character_fame'] = list()
response = requests.get(build_url(build_api_request('job_info', apikey=Settings.API_KEYS[0])))
data = response.json()
data = data['rows']
job_data = []
for job in data:
    
    # 노전직 캐릭터가 있을 수 있는 전직이면
    if job['jobId'] in NO_JOG_GROW_JOB_IDS:
        job_data.append({
            'jobId' : job['jobId'],
            'jobGrowId' : '1ea40db11ff66e70bcb0add7fae44cdb' # 노전직 job grow id 수동으로 추가
        })
    
    for job_grow in job['rows']:
        job_data.append({
            'jobId' : job['jobId'],
            'jobGrowId' : job_grow['jobGrowId']
        })



metadata['params_for_seed_character_fame'] = [
    {**item, 'serverId': server_id}
    for server_id in SERVER_ID_LIST
    for item in job_data
]      

# === 파일 생성하기 ===
def generate_metadata_file(metadata):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"[+] {OUTPUT_FILE} 파일이 성공적으로 생성되었습니다.")

# === 실행 ===
if __name__ == "__main__":
    generate_metadata_file(metadata)
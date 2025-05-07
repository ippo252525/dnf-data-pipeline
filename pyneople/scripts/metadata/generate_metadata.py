import psycopg2
import os
import pickle
import requests
from pyneople.config.config import Settings
from pyneople.metadata.metadata_constants import SERVER_ID_LIST
from pyneople.utils.api_utils.api_request_builder import build_api_request
from pyneople.utils.api_utils.url_builder import build_url

# === 설정 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, '../../metadata/metadata_generated.pkl')

metadata = dict()

# 테이블 컬럼 정보 받아오기
metadata['table_columns_map'] = dict()
DB_CONFIG = {
    'database': Settings.POSTGRES_DB,
    'user': Settings.POSTGRES_USER,
    'password': Settings.POSTGRES_PASSWORD,
    'host': Settings.POSTGRES_HOST,
    'port': Settings.POSTGRES_PORT
}
SCHEMA = Settings.POSTGRES_SCHEMA
conn = psycopg2.connect(**DB_CONFIG)
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
conn.close()

for table_name, column_name in rows:
    metadata['table_columns_map'].setdefault(table_name, []).append(column_name)
    
# 직업 정보 받아오기
metadata['params_for_seed_character_fame'] = list()
response = requests.get(build_url(build_api_request('job_info', apikey=Settings.API_KEYS[0])))
data = response.json()
data = data['rows']
job_data = []
for job in data:
    job_id = job['jobId']
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
    with open(OUTPUT_FILE, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"[+] {OUTPUT_FILE} 파일이 성공적으로 생성되었습니다.")

# === 실행 ===
if __name__ == "__main__":
    generate_metadata_file(metadata)
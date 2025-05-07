from dotenv import load_dotenv
import os


# 환경변수 불러오기
# airflow가 아닌 local에서 test할 때는 다른 환경변수를 부른다.
if not os.getenv("AIRFLOW__CORE__EXECUTOR"):
    from dotenv import load_dotenv
    load_dotenv(".env.local")
else:
    load_dotenv()

class Settings:
    

    # API 키 설정
    API_KEYS = [key.strip() for key in os.getenv('PYNEOPLE_API_KEYS').split(',') if key.strip()]

    # MongoDB 설정
    MONGO_URL=os.getenv('PYNEOPLE_MONGO_URL')
    MONGO_DB_NAME=os.getenv('PYNEOPLE_MONGO_DB_NAME')
    MONGO_COLLECTION_NAME=os.getenv('PYNEOPLE_MONGO_COLLECTION_NAME')
    MONGO_ERROR_COLLECTION_NAME=os.getenv('PYNEOPLE_MONGO_ERROR_COLLECTION_NAME')

    # PostgreSQL 설정
    POSTGRES_HOST=os.getenv('PYNEOPLE_POSTGRES_HOST')
    POSTGRES_PORT=int(os.getenv('PYNEOPLE_POSTGRES_PORT'))
    POSTGRES_USER=os.getenv('PYNEOPLE_POSTGRES_USER')
    POSTGRES_PASSWORD=os.getenv('PYNEOPLE_POSTGRES_PASSWORD')
    POSTGRES_DB=os.getenv('PYNEOPLE_POSTGRES_DB')
    POSTGRES_SCHEMA=os.getenv('PYNEOPLE_POSTGRES_SCHEMA')

    # 디폴트 값
    
    # Seeder가 SQL을 사용 할 경우 cursor에 필요한 batch size
    DEFAULT_SEEDER_BATCH_SIZE = 2

    # API 요청을 보내는 워커의 개수
    DEFAULT_NUM_API_FETCH_WORKERS = 100

    # API 요청에 필요한 정보를 담는 Queue의 max size
    DEFAULT_API_REQUEST_QUEUE_SIZE = 1000

    # api request queue의 get에 대한 timeout
    DEFAULT_API_FETCH_WORKER_TIMEOUT = 1.0

    # API로부터 받은 데이터를 담는 Queue의 max size
    DEFAULT_DATA_QUEUE_SIZE = 1000

    # 데이터를 MongoDB에 저장하는 워커의 개수
    DEFAULT_NUM_MONGO_STORE_WORKERS = 10

    # data queue의 get에 대한 timeout
    DEFAULT_MONGO_STORE_WORKER_TIMEOUT = 1.0

    # 한번에 MongoDB에 저장하는 데이터 개수
    DEFAULT_MONGO_STORE_BATCH_SIZE = 2000

    # MongoDB에서 데이터를 각 엔드포인트 Queue에 분배하는 워커의 개수
    DEFAULT_NUM_MONGO_ROUTERS = 8

    # MongoDB 라우터의 batch size
    DEFAULT_MONGO_ROUTER_BATCH_SIZE = 3000

    # 각 엔트포인트 Queue의 max size
    DEFAULT_MONGO_TO_PSQL_QUEUE_SIZE = 1000

    # 각 엔트포인트 Queue에 붙어서 데이터를 PostgreSQL에 저장하는 워커 개수
    DEFAULT_NUM_QUEUE_TO_PSQL_WORKERS = 10

    # PostgreSQL에 저장할 때 batch size
    DEFAULT_QUEUE_TO_PSQL_BATCH_SIZE = 2000

    # 각 엔트포인트 Queue.get에 대한 timeout
    DEFAULT_QUEUE_TO_PSQL_WORKER_TIMEOUT = 1.0

    # API 요청이 timeout으로 실패 한 경우 최대 재시도 횟수
    DEFAULT_API_FETCH_WORKER_MAX_RETRIES = 3
    
    # Seeder 전용 PSQL 연결 풀 최대 크기
    DEFAULT_SEEDER_PSQL_POOL_MAX_SIZE = 10

    # Mongo → PSQL 작업용 연결 풀 최대 크기
    DEFAULT_MONGO_TO_PSQL_POOL_MAX_SIZE = 20
    
    # 초당 api 요청 횟수를 측정하기 위한 변수
    request_count = 0

    # 데이터 마킹을 위한 샘플 케이스
    SAMPLE_SERVER_ID = os.getenv('SAMPLE_SERVER_ID')
    SAMPLE_CHARACTER_ID = os.getenv('SAMPLE_CHARACTER_ID')
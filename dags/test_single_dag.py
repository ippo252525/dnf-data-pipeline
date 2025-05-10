from airflow import DAG
# from airflow.operators import PythonOperator
# from airflow.operators
from airflow.providers.standard.operators.python import PythonOperator
from pyneople.api_to_mongo import api_to_mongo
from datetime import datetime, timedelta

from pyneople.mongo_to_psql import mongo_to_psql


# Python 함수 정의
def hello_world():
    print("Hello from DAG")

# DAG 기본 설정
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

query = """
SELECT character_id, server_id 
FROM characters
LIMIT 1000;
"""
endpoints = [
    'character_info',
    'character_timeline',
    'character_status',
    'character_equipment',
    'character_avatar',
    'character_creature',
    'character_flag',
    'character_buff_equipment'
]

# DAG 정의
with DAG(
    dag_id='test_hello_world_dag',
    default_args=default_args,
    description='A simple test DAG',
    schedule=None,  # 매 1분마다
    start_date=datetime(2024, 4, 28),
    catchup=False,  # 과거 스케줄에 대해 실행하지 않음
    tags=['test'],
) as dag:

    to_mongo = PythonOperator(
        task_id='to_mongo',
        python_callable=api_to_mongo,
        op_kwargs = {'endpoints' : endpoints, 'sql' : query}
    )
    to_psql = PythonOperator(
        task_id='to_psql',
        python_callable=mongo_to_psql,
        op_kwargs = {'endpoints' : endpoints, 
                     'character_info_endpoints' : ['character_equipment'], 
                     'num_queue_to_psql_workers' : 2,
                     'mongo_to_psql_pool_max_size' : 20}
    )


    to_mongo >> to_psql
from airflow import DAG
# from airflow.operators import PythonOperator
# from airflow.operators
from airflow.providers.standard.operators.python import PythonOperator
from pyneople.api_to_mongo import api_to_mongo
from datetime import datetime, timedelta


# Python 함수 정의
def hello_world():
    print("Hello from DAG")

# DAG 기본 설정
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

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

    hello_task = PythonOperator(
        task_id='say_hello',
        python_callable=api_to_mongo,
        op_kwargs = {'endpoints' : ['character_fame'], 'max_fame' : 10000}
    )

    hello_task
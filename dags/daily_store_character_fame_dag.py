"""
캐릭터 명성 검색을 기반으로 캐릭터 정보를 저장하는 DAG

캐릭터 명성 검색을 기반으로 캐릭터 정보를 업데이트 함
staging_character_fame 에 스테이징 후 clickhouse insert 와 character 테이블을 업데이트 한다.
"""
# airflow
from asyncio import Task
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.python import PythonOperator

# python
from datetime import datetime, date
from pathlib import Path
from httpx import delete
import pendulum

# pyneople
from pyneople.config.config import Settings
import pyneople.api.registry.endpoint_class
from pyneople.api.registry.endpoint_registry import EndpointRegistry
from pyneople.api_to_mongo import api_to_mongo
from pyneople.mongo_to_psql import mongo_to_psql
from pyneople.psql_to_clickhouse import psql_to_clickhouse
from pyneople.psql_batch_upsert import psql_batch_upsert
from pyneople.utils.common import read_sql
from pyneople.utils.db_utils.mongo_db import drop_collection
from pyneople.utils.db_utils.postgresql import truncate_tables
from pyneople.utils.monitoring import slack_notify_on_failure, slack_notify_on_success, slack_notify_on_excute
from pyneople.utils.db_utils.get_mongo_split_filters import get_split_filters_for_task
from pyneople.mongo_to_psql_with_filter import mongo_to_psql_with_filter

# KST timezone 설정
kst = pendulum.timezone("Asia/Seoul")
now_kst = datetime.now(tz=kst)

# MongoDB collection name 따로 지정
mongo_collection_name = Settings.MONGO_COLLECTION_NAME
error_collection_name = Settings.MONGO_ERROR_COLLECTION_NAME

# 병렬 task 수
num_parallel_tasks = 6

# MongoDB에서 사용할 필터 생성
mongo_filters = get_split_filters_for_task(num_parallel_tasks)

# 조회를 시작 할 최고 명성
max_fame = 1000000

# 캐릭터 명성 검색만 이용
endpoint = 'character_fame'
endpoints = ['character_fame']

# 스테이징 테이블 이름
staging_table_name = EndpointRegistry.get_class(endpoint).staging_table_name
staging_table_names = [EndpointRegistry.get_class(endpoint).staging_table_name for endpoint in endpoints]

# PostgreSQL 스테이징에서 각 queue에 사용 할 worker 수
num_queue_to_psql_workers = 10

# INSERT SQL Query Root
insert_sql_query_root = Path(__file__).resolve().parent.parent / 'pyneople' / 'db' / 'query' / 'insert'

# SELECT SQL Query Root
select_sql_query_root = Path(__file__).resolve().parent.parent / 'pyneople' / 'db' / 'query' / 'select'

# DELETE SQL Query Root
delete_sql_query_root = Path(__file__).resolve().parent.parent / 'pyneople' / 'db' / 'query' / 'delete'

# Slack 알림을 위해 Operator에서 사용할 default_args 설정
default_args = {
    'on_failure_callback' : slack_notify_on_failure,
    'on_success_callback' : slack_notify_on_success,
    'on_execute_callback' : slack_notify_on_excute
}

# DAG 선언
with DAG(
    dag_id='store_character_fame',
    description='캐릭터 명성 검색을 기반으로 캐릭터 정보를 저장하는 DAG',
    schedule=None,  
    start_date=datetime(2025, 5, 17, tzinfo=kst),
    catchup=False,  
    on_failure_callback=slack_notify_on_failure,
    on_success_callback=slack_notify_on_success,
    default_args=default_args,
    tags=['update', 'daily', 'characters']
) as dag:
    
    # # 사용 해야 할 Mongo Collection 비우기(삭제)
    # drop_mongo_collections = PythonOperator(
    #     task_id='drop_mongo_collections',
    #     python_callable=drop_collection,
    #     op_kwargs={
    #         'collection_names' : [mongo_collection_name, error_collection_name]
    #     }
    # )

    # # 사용 해야 할 PostgreSQL staging table 비우기
    # clear_staging_tables = PythonOperator(
    #     task_id = 'clear_staging_tables',
    #     python_callable=truncate_tables,
    #     op_kwargs={
    #         'table_names' : staging_table_names
    #     }
    # )

    # # 캐릭터 명성 검색 API를 통해 MongoDB에 저장
    # to_mongo = PythonOperator(
    #     task_id='to_mongo',
    #     python_callable=api_to_mongo,
    #     op_kwargs = {
    #         'endpoints' : endpoints, 
    #         'check_rate_limit' : True,
    #         'mongo_collection_name' : mongo_collection_name,
    #         'error_collection_name' : error_collection_name,
    #         'max_fame' : max_fame,
    #         'num_api_fetch_workers' : 50
    #     }
    # )
    # # MongoDB에서 가져온 데이터를 PostgreSQL로 저장
    # to_psql_tasks = []
    # for index, mongo_filter in enumerate(mongo_filters):
    #     to_psql = PythonOperator(
    #         task_id=f'to_psql_{index}',
    #         python_callable=mongo_to_psql_with_filter,
    #         op_kwargs={
    #             'filter': mongo_filter,
    #             'psql_table_name': staging_table_name,
    #             'batch_size': 5000,
    #             'preprocess': EndpointRegistry.get_class(endpoint).preprocess
    #         }
    #     )
    #     to_psql_tasks.append(to_psql)

    # # staging_character_fame 테이블의 중복 제거를 위한 인덱스 생성
    # create_index_staging_character_fmae = SQLExecuteQueryOperator(
    #     task_id = 'create_index_staging_character_fmae',
    #     conn_id = 'pyneople-postgres',
    #     sql='''CREATE INDEX idx_staging_character_fame_server_char_fetched ON staging_character_fame (server_id, character_id, fetched_at DESC);''',
    # )    

    # # staging_character_fame 테이블의 중복 제거
    # delete_duplicates_staging_character_fame = SQLExecuteQueryOperator(
    #     task_id = 'delete_duplicates_staging_character_fame',
    #     conn_id = 'pyneople-postgres',
    #     sql=read_sql(delete_sql_query_root / 'delete_duplicates_staging_character_fame.sql'),
    # )

    # staging_character_fame 테이블의 데이터를 character 테이블에 batch upsert
    # staging_to_main_tasks = []
    # for index in range(num_parallel_tasks):
    staging_to_main = PythonOperator(
            task_id=f'staging_to_main',
            python_callable=psql_batch_upsert,
            op_kwargs={
                'worker_id': 1,
                'n_partitions': num_parallel_tasks,
                'batch_size': 10000
            }
        )
        # staging_to_main_tasks.append(staging_to_main_task)

    (
        # drop_mongo_collections
        # >> clear_staging_tables
        # >> to_mongo 
        # >> to_psql_tasks
        # >> 
        # create_index_staging_character_fmae
        # >> delete_duplicates_staging_character_fame
        #>> 
        staging_to_main
    #    >> [to_clickhouse, staging_character_fmae_to_character_table]
    )
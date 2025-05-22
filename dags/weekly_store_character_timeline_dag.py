"""
1주일에 한번씩 캐릭터 데이터 타임라인 데이터를 저장하는 DAG
매주 목요일 점검 직후 실행, 수집하는 범위는 목요일부터 1까지
"""
# airflow
import re
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.python import PythonOperator

# python
from datetime import datetime
from pathlib import Path
import pendulum

# pyneople
from pyneople.config.config import Settings
import pyneople.api.registry.endpoint_class
from pyneople.api.registry.endpoint_registry import EndpointRegistry
from pyneople.api_to_mongo import api_to_mongo
from pyneople.mongo_to_psql import mongo_to_psql
from pyneople.psql_to_clickhouse import psql_to_clickhouse
from pyneople.mongo_to_clickhouse import mongo_to_clickhouse_timeline
from pyneople.mongo_to_clickhouse_with_filter import mongo_to_clickhouse_with_filter
from pyneople.utils.db_utils.get_mongo_split_filters import get_split_filters_for_task
from pyneople.scripts.db.deactivate_characters import deactivate_characters
from pyneople.utils.common import read_sql
from pyneople.api.preprocessors.character_timeline_preprocessor import flatten_character_timeline, preprocess_character_timeline_clickhouse_batch
from pyneople.metadata.metadata_generated import CLICKHOUSE_TABLE_COLUMNS_MAP
from pyneople.utils.db_utils.mongo_db import drop_collection
from pyneople.utils.db_utils.postgresql import truncate_tables
from pyneople.utils.monitoring import slack_notify_on_failure, slack_notify_on_success, slack_notify_on_excute

# KST timezone 설정
kst = pendulum.timezone("Asia/Seoul")
now_kst = datetime.now(tz=kst)
timeline_start_date = '2025-01-09 12:00'

now = pendulum.now("Asia/Seoul")
if now.day_of_week == pendulum.THURSDAY and now.hour >= 6:
    # 오늘이 목요일이고 오전 6시 이후라면 오늘 오전 6시 기준
    end = now.replace(hour=6, minute=0, second=0, microsecond=0)
else:
    # 아니면 직전 목요일 오전 6시 기준
    end = now.previous(pendulum.THURSDAY).replace(hour=6, minute=0, second=0, microsecond=0)

timeline_end_date = end.format("YYYY-MM-DD HH:mm")
snapshot_date = end.date()

# MongoDB collection name 따로 지정
mongo_collection_name = Settings.MONGO_COLLECTION_NAME
error_collection_name = Settings.MONGO_ERROR_COLLECTION_NAME

# 병렬 task 수
num_parallel_tasks = 6



# 수집하려는 데이터의 엔드포인트 목록
endpoints = [
    'character_timeline'
]

# 스테이징 테이블 이름
staging_table_names = [EndpointRegistry.get_class(endpoint).staging_table_name for endpoint in endpoints]

# PostgreSQL 스테이징에서 각 queue에 사용 할 worker 수
num_queue_to_psql_workers = 10

# INSERT SQL Query Root
insert_sql_query_root = Path(__file__).resolve().parent.parent / 'pyneople' / 'db' / 'query' / 'insert'

# SELECT SQL Query Root
select_sql_query_root = Path(__file__).resolve().parent.parent / 'pyneople' / 'db' / 'query' / 'select'

# Slack 알림을 위해 Operator에서 사용할 default_args 설정
default_args = {
    'on_failure_callback' : slack_notify_on_failure,
    'on_success_callback' : slack_notify_on_success,
    'on_execute_callback' : slack_notify_on_excute
}

import pickle
def read_pickle():
    with open(Path(__file__).resolve().parent.parent / 'pyneople' / 'mongo_filters.pkl', 'rb') as f:
        return pickle.load(f)

# DAG 선언
with DAG(
    dag_id='store_character_timeline',
    description='캐릭터 타임라인 데이터 수집 DAG',
    schedule=None,  
    start_date=datetime(2024, 5, 17, tzinfo=kst),
    catchup=False,  
    on_success_callback=slack_notify_on_success,
    on_failure_callback=slack_notify_on_failure,
    # default_args = default_args,
    tags=['store', 'character_data']
) as dag:
    
    # # 사용 해야 할 Mongo Collection 비우기(삭제)
    # drop_mongo_collections = PythonOperator(
    #     task_id='drop_mongo_collections',
    #     python_callable=drop_collection,
    #     op_kwargs={
    #         'collection_names' : [mongo_collection_name, error_collection_name]
    #     }
    # )

    

    # # API에서 MongoDB로 데이터 수집
    # to_mongo = PythonOperator(
    #     task_id='to_mongo',
    #     python_callable=api_to_mongo,
    #     op_kwargs = {
    #         'endpoints' : endpoints, 
    #         'check_rate_limit' : False,
    #         'sql' : read_sql(select_sql_query_root / 'get_activated_characters_from_character_table.sql'),
    #         'num_api_fetch_workers' : 50,
    #         'timeline_start_date' : timeline_start_date,
    #         'timeline_end_date' : timeline_end_date
    #     }
    # )

    # # MongoDB Error Collection에서 404 Not Found Character Error 인 캐릭터들 character table에서 is_active 변수 False로 처리
    # deactivate_not_found_characters = PythonOperator(
    #     task_id="deactivate_not_found_characters",
    #     python_callable=deactivate_characters,
    #     op_kwargs={
    #         'error_collection_name' : error_collection_name
    #     }
    # )
    # MongoDB에서 사용할 필터 생성

    # 스테이징 테이블에서 clickhouse 테이블로 데이터 이동
    to_clickhouse_tasks = []
    for index in range(num_parallel_tasks): 
        to_clickhouse_task = PythonOperator(
            task_id=f'to_clickhouse_{index}',
            python_callable=mongo_to_clickhouse_with_filter,
            op_kwargs={
                'filter': read_pickle()[index],
                'clickhouse_table_name' : 'character_timeline',
                'snapshot_date' : snapshot_date,
                'batch_size' : 10000,
                'preprocess' : preprocess_character_timeline_clickhouse_batch
            }
        )
        to_clickhouse_tasks.append(to_clickhouse_task)

    (
        to_clickhouse_tasks
        # drop_mongo_collections
        # >> to_mongo
        # >> deactivate_not_found_characters
    )
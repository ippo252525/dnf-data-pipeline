"""
character 테이블에서 모험단 별 가장 명성이 높은 캐릭터를 이용해서 모험단에 대응되는 정보를 저장한다.

character 테이블에서 모험단 별 가장 명성이 높은 캐릭터를 이용해서 휘장 정보를 저장한다.
404 Not Found Character Error가 발생한 캐릭터는 모험단에 속한 다른 캐릭터를 이용해서 다시 요청한다.
"""
# airflow
from airflow import DAG
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
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
from pyneople.scripts.db.deactivate_characters import deactivate_characters
from pyneople.utils.common import read_sql
from pyneople.utils.db_utils.mongo_db import drop_collection
from pyneople.utils.db_utils.postgresql import truncate_tables
from pyneople.utils.monitoring import slack_notify_on_failure, slack_notify_on_success, slack_notify_on_excute
from pyneople.retry_not_found_characters_adventure_flag import retry_not_found_characters_adventure_flag

# KST timezone 설정
kst = pendulum.timezone("Asia/Seoul")
now_kst = datetime.now(tz=kst)

# MongoDB collection name
mongo_collection_name = Settings.MONGO_COLLECTION_NAME
error_collection_name = Settings.MONGO_ERROR_COLLECTION_NAME

# 수집하려는 데이터의 엔드포인트 목록
endpoints = [
    'character_flag'
]

staging_table_names = [EndpointRegistry.get_class(endpoint).staging_table_name for endpoint in endpoints]

# PostgreSQL 스테이징에서 각 queue에 사용 할 worker 수
num_queue_to_psql_workers = 10

# INSERT SQL Query Root
insert_sql_query_root = Path(__file__).resolve().parent.parent / 'pyneople' / 'db' / 'query' / 'insert'

# SELECT SQL Query Root
select_sql_query_root = Path(__file__).resolve().parent.parent / 'pyneople' / 'db' / 'query' / 'select'

# DDL SQL Query Root
ddl_sql_query_root = Path(__file__).resolve().parent.parent / 'pyneople' / 'db' / 'query' / 'ddl'

# Slack 알림을 위해 Operator에서 사용할 default_args 설정
default_args = {
    'on_failure_callback' : slack_notify_on_failure,
    'on_success_callback' : slack_notify_on_success,
    'on_execute_callback' : slack_notify_on_excute
}

# DAG 선언
with DAG(
    dag_id='store_adventure_data',
    description='모험단 기반 정보를 저장하는 DAG',
    schedule=None,
    start_date=datetime(2024, 5, 17, tzinfo=kst),
    catchup=False,  
    on_failure_callback=slack_notify_on_failure,
    on_success_callback=slack_notify_on_success,
    default_args = default_args,
    tags=['store', 'adventure']
) as dag:
    
    # 사용 해야 할 Mongo Collection 비우기(삭제)
    drop_mongo_collections = PythonOperator(
        task_id='drop_mongo_collections',
        python_callable=drop_collection,
        op_kwargs={
            'collection_names' : [mongo_collection_name, error_collection_name]
        }
    )

    # 사용 해야 할 PostgreSQL staging table 비우기
    clear_staging_tables = PythonOperator(
        task_id = 'clear_staging_tables',
        python_callable=truncate_tables,
        op_kwargs={
            'table_names' : staging_table_names
        }
    )

    # character table 인덱스 생성
    create_index = SQLExecuteQueryOperator(
        task_id="create_index",
        conn_id = 'pyneople-postgres',
        sql = read_sql(ddl_sql_query_root / 'create_character_adventure_fame_id_index.sql')
    )

    # MongoDB에 API 데이터 수집
    to_mongo = PythonOperator(
        task_id='to_mongo',
        python_callable=api_to_mongo,
        op_kwargs={
            'endpoints' : endpoints,            
            'check_rate_limit' : True,
            'sql' : read_sql(select_sql_query_root / 'get_adventure_top_fame_character.sql'),
            'num_api_fetch_workers' : 50
        }
    )

    # MongoDB Error Collection에서 404 Not Found Character Error 인 캐릭터들 character table에서 is_active 변수 False로 처리
    deactivate_not_found_characters = PythonOperator(
        task_id="deactivate_not_found_characters",
        python_callable=deactivate_characters,
        op_kwargs={
            'error_collection_name' : error_collection_name
        }
    )

    # 404 Not Found Character Error 인 캐릭터의 모험단의 다른 캐릭터를 가지고 와서 다시 요청
    retry_not_found_characters = PythonOperator(
        task_id="retry_not_found_characters",
        python_callable=retry_not_found_characters_adventure_flag,
        op_kwargs={
            'error_collection_name' : error_collection_name
        }
    )

    # MongoDB의 데이터 PostgreSQL 스테이징 테이블로 이동
    to_psql = PythonOperator(
        task_id='to_psql',
        python_callable=mongo_to_psql,
        op_kwargs={
            'endpoints' : endpoints,
            'num_queue_to_psql_workers' : num_queue_to_psql_workers,
            'mongo_to_psql_pool_max_size' : num_queue_to_psql_workers
        }
    )

    # PostgreSQL 스테이징 테이블에서 main 테이블로 데이터 이동
    staging_to_main = SQLExecuteQueryOperator(
        task_id="staging_to_main",
        conn_id = 'pyneople-postgres',
        sql = read_sql(insert_sql_query_root / 'staging_character_flag_to_character_flag_table.sql')
    )

    # 태스크 의존성 설정
    (
        drop_mongo_collections
        >> clear_staging_tables
        >> create_index
        >> to_mongo
        >> deactivate_not_found_characters
        >> retry_not_found_characters
        >> to_psql
        >> staging_to_main
    )
    
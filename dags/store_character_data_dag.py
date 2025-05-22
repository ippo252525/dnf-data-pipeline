"""
원하는 캐릭터의 캐릭터 정보를 수집하여 PostgreSQL main 테이블에 적재하는 DAG

1. 데이터가 거쳐 갈 컴포넌트 (MongoDB, PostgreSQL staging table) 정리
2. character 테이블에 적재된 character_id와 server_id를 기반으로 원하는 데이터 조회 
3. 404 Not Found Character Error가 발생하는 경우 character table에서 해당 캐릭터 is_activate = False로 update
4. 조회를 바탕으로 각각의 스테이징 테이블에 스테이징
5. 스테이징 테이블을 바탕으로 메인 테이블에 삽입 (삽입 전 메인 테이블 TRUNCATE 하므로 주의)
"""
# airflow
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
from pyneople.scripts.db.deactivate_characters import deactivate_characters
from pyneople.utils.common import read_sql
from pyneople.utils.db_utils.mongo_db import drop_collection
from pyneople.utils.db_utils.postgresql import truncate_tables
from pyneople.utils.monitoring import slack_notify_on_failure, slack_notify_on_success, slack_notify_on_excute

# KST timezone 설정
kst = pendulum.timezone("Asia/Seoul")
now_kst = datetime.now(tz=kst)

# MongoDB collection name 따로 지정
mongo_collection_name = Settings.MONGO_COLLECTION_NAME
error_collection_name = Settings.MONGO_ERROR_COLLECTION_NAME

# 수집하려는 데이터의 엔드포인트 목록
endpoints = [
    'character_equipment',
    'character_avatar',
    'character_creature',
    'character_buff_equipment'
]

# 캐릭터 정보를 수집하는데 사용 할 엔드포인트
character_info_endpoints = [endpoints[0]]

# 스테이징 테이블 이름
staging_table_names = [EndpointRegistry.get_class(endpoint).staging_table_name for endpoint in endpoints]

# PostgreSQL 스테이징에서 각 queue에 사용 할 worker 수
num_queue_to_psql_workers = 3

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

# DAG 선언
with DAG(
    dag_id='store_character_data',
    description='캐릭터 정보 수집 DAG',
    schedule=None,  
    start_date=datetime(2024, 5, 17, tzinfo=kst),
    catchup=False,  
    on_success_callback=slack_notify_on_success,
    on_failure_callback=slack_notify_on_failure,
    default_args = default_args,
    tags=['store', 'character_data']
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
            'table_names' : staging_table_names + ['staging_character_info']
        }
    )

    # API에서 MongoDB로 데이터 수집
    to_mongo = PythonOperator(
        task_id='to_mongo',
        python_callable=api_to_mongo,
        op_kwargs = {
            'endpoints' : endpoints, 
            'check_rate_limit' : True,
            'sql' : read_sql(select_sql_query_root / 'get_activated_characters_from_character_table.sql'),
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

    # MongoDB의 데이터 PostgreSQL 스테이징 테이블로 이동
    to_psql = PythonOperator(
        task_id='to_psql',
        python_callable=mongo_to_psql,
        op_kwargs = {
            'endpoints' : endpoints,
            'character_info_endpoints' : [endpoints[0]],
            'num_queue_to_psql_workers' : num_queue_to_psql_workers,
            'mongo_to_psql_pool_max_size' : num_queue_to_psql_workers * len(endpoints) + 1
        }
    )


    # staging_character_info 테이블의 데이터를 통해 character 테이블 정보 갱신(upsert)
    staging_character_info_to_character_table = SQLExecuteQueryOperator(
        task_id="staging_character_info_to_character_table",
        conn_id = 'pyneople-postgres',
        sql=read_sql(insert_sql_query_root / 'staging_character_info_to_character_table.sql')
    )

    # 스테이징 테이블에서 메인 테이블로 데이터 이동 (drop and insert)
    staging_to_main_tasks = []
    for staging_table_name in staging_table_names:
        main_table_name = staging_table_name.replace("staging_", "")
        staging_to_main_task = SQLExecuteQueryOperator(
            task_id=f"{staging_table_name}_to_{main_table_name}_table",
            conn_id='pyneople-postgres',
            sql=read_sql(insert_sql_query_root / f'{staging_table_name}_to_{main_table_name}_table.sql')
        )
        staging_to_main_tasks.append(staging_to_main_task)

    (
        drop_mongo_collections
        >> clear_staging_tables
        >> to_mongo
        >> deactivate_not_found_characters
        >> to_psql 
        >> staging_character_info_to_character_table
        >> staging_to_main_tasks
    )
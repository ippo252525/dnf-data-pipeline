"""
원하는 캐릭터의 캐릭터 정보를 업데이트 하는 DAG

0. 데이터가 거쳐 갈 컴포넌트 정리
1. character table에 적재된 character_id와 server_id를 기반으로 원하는 데이터 조회 <- 원하는 캐릭터를 조회 할 수 있도록 유연하게
1-1. 404 Not Found Character Error가 발생하는 경우 character table에서 해당 캐릭터 is_activate = False로 update
2. 조회를 바탕으로 각각의 스테이징 테이블에 스테이징 <- 일단 스테이징 까지만
3. 스테이징 테이블을 바탕으로 메인 테이블에 삽입 
"""

"""
캐릭터 명성 검색을 기반으로 캐릭터 정보를 저장하는 DAG

Neople Open API의 15. 캐릭터 명성 검색을 기반으로 캐릭터 정보를 업데이트 함
"""
from airflow import DAG

from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.python import PythonOperator

from datetime import datetime, date
from pathlib import Path
import pendulum

from pyneople.api_to_mongo import api_to_mongo
from pyneople.mongo_to_psql import mongo_to_psql
from pyneople.scripts.db.truncate_tables import truncate_tables
from pyneople.scripts.db.reset_mongo import clear_collection
from pyneople.scripts.db.deactivate_characters import deactivate_characters
from pyneople.config.config import Settings
import pyneople.api.registry.endpoint_class
from pyneople.api.registry.endpoint_registry import EndpointRegistry


kst = pendulum.timezone("Asia/Seoul")
now_kst = datetime.now(tz=kst)

# sql 파일 가져오기
sql_path = Path(__file__).resolve().parent.parent / 'pyneople' / 'db' / 'query' / 'get_activated_characters_from_character_table.sql'
with open(sql_path, 'r') as f:
    get_activated_characters_from_character_table_sql = f.read()

# sql 파일 가져오기
sql_path = Path(__file__).resolve().parent.parent / 'pyneople' / 'db' / 'query' / 'staging_character_info_to_character_table.sql'
with open(sql_path, 'r') as f:
    staging_character_info_to_character_table_sql = f.read()

# sql_path = Path(__file__).resolve().parent.parent / 'pyneople' / 'db' / 'query' / 'character_to_adventure_table.sql'
# with open(sql_path, 'r') as f:
#     character_to_adventure_table_sql = f.read()



# 조회를 시작 할 최고 명성
max_fame = 1000000

# MongoDB collection name 따로 지정
mongo_collection_name = Settings.MONGO_COLLECTION_NAME
error_collection_name = Settings.MONGO_ERROR_COLLECTION_NAME

# PostgreSQL Staging Table 이름
psql_staging_table_name = 'staging_character_fame'

# 수집하려는 데이터의 엔드포인트 목록
endpoints = [
    'character_equipment',
    'character_avatar',
    'character_creature',
    'character_buff_equipment'
]

staging_table_names = [EndpointRegistry.get_class(endpoint).staging_table_name for endpoint in endpoints]

# DAG 선언
with DAG(
    dag_id='update_character_data',
    description='Update character_data',
    schedule=None,  
    start_date=datetime(2024, 5, 13, 0, 0, tzinfo=kst),
    catchup=False,  
    tags=['update', 'characters', 'equipment']
) as dag:
    
    send_start_message_to_slack = SlackWebhookOperator(
        task_id="send_start_message_to_slack",
        slack_webhook_conn_id="pyneople-slack",
        message=f"Start DAG : update_character_data\nStart time : {now_kst.strftime("%Y-%m-%d %H:%M:%S")}"
    )
    
    clear_mongo_collections = PythonOperator(
        task_id='clear_mongo_collections',
        python_callable=clear_collection,
        op_kwargs={
            'collection_names' : [mongo_collection_name, error_collection_name]
        }
    )

    to_mongo = PythonOperator(
        task_id='to_mongo',
        python_callable=api_to_mongo,
        op_kwargs = {
            'endpoints' : endpoints, 
            'check_rate_limit' : True,
            'sql' : get_activated_characters_from_character_table_sql
        }
    )

    send_complete_api_to_mongo_message_to_slack = SlackWebhookOperator(
        task_id="send_complete_api_to_mongo_message_to_slack",
        slack_webhook_conn_id="pyneople-slack",
        message=f"캐릭터 정보 MongoDB에 저장 완료"
    )

    deactivate_not_found_characters = PythonOperator(
        task_id="deactivate_not_found_characters",
        python_callable=deactivate_characters,
        op_kwargs={
            'error_collection_name' : error_collection_name
        }
    )

    clear_staging_tables = PythonOperator(
        task_id = 'clear_staging_tables',
        python_callable=truncate_tables,
        op_kwargs={
            'table_names' : staging_table_names + ['staging_character_info']
        }
    )

    to_psql = PythonOperator(
        task_id='to_psql',
        python_callable=mongo_to_psql,
        op_kwargs = {
            'endpoints' : endpoints,
            'character_info_endpoints' : [endpoints[0]],
            'num_queue_to_psql_workers' : 3,
            'mongo_to_psql_pool_max_size' : 3 * len(endpoints)
        }
    )

    send_complete_mongo_to_psql_message_to_slack = SlackWebhookOperator(
        task_id="send_complete_mongo_to_psql_message_to_slack",
        slack_webhook_conn_id="pyneople-slack",
        message=f"캐릭터 정보 PostgreSQL staging table에 스테이징 완료"
    )

    staging_character_info_to_character_table = SQLExecuteQueryOperator(
        task_id="staging_character_info_to_character_table",
        conn_id = 'pyneople-postgres',
        sql=staging_character_info_to_character_table_sql
    )

    send_complete_message_to_slack = SlackWebhookOperator(
        task_id="send_complete_message_to_slack",
        slack_webhook_conn_id="pyneople-slack",
        message=f"character_data DAG 실행 완료"
    )

    (
        send_start_message_to_slack 
        >> clear_mongo_collections
        >> to_mongo
        >> send_complete_api_to_mongo_message_to_slack 
        >> deactivate_not_found_characters
        >> clear_staging_tables
        >> to_psql 
        >> send_complete_mongo_to_psql_message_to_slack 
        >> staging_character_info_to_character_table
        >> send_complete_message_to_slack
    )

#TODO : adventure name 업데이트 해당 테이블 기반으로 flag정보 조회, 모험단 메인 테이블 설정
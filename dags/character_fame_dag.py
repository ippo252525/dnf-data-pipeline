"""
캐릭터 명성 검색을 기반으로 캐릭터 정보를 저장하는 DAG

Neople Open API의 15. 캐릭터 명성 검색을 기반으로 캐릭터 정보를 업데이트 함
staging_character_fame 에 스테이징 후 clickhouse insert 와 character 테이블을 업데이트 한다.
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
from pyneople.psql_to_clickhouse import psql_to_clickhouse
from pyneople.scripts.db.reset_mongo import clear_collection


kst = pendulum.timezone("Asia/Seoul")
now_kst = datetime.now(tz=kst)

# sql 파일 가져오기
sql_path = Path(__file__).resolve().parent.parent / 'pyneople' / 'db' / 'query' / 'extract_latest_character_fame.sql'
with open(sql_path, 'r') as f:
    sql = f.read()

sql_path = Path(__file__).resolve().parent.parent / 'pyneople' / 'db' / 'query' / 'staging_character_fame_to_character.sql'
with open(sql_path, 'r') as f:
    staging_character_fame_to_charater_sql = f.read()


# 조회를 시작 할 최고 명성
max_fame = 1000000

# 캐릭터 명성 검색만 이용
endpoints = ['character_fame']

# MongoDB collection name 따로 지정
mongo_collection_name = 'character_fame'
error_collection_name = 'character_fame_error'

# PostgreSQL Staging Table 이름
psql_staging_table_name = 'staging_character_fame'

# DAG 선언
with DAG(
    dag_id='character_fame_to_clickhouse',
    description='Update the character_fame_history table using the character fame endpoint.',
    schedule='@daily',  
    start_date=datetime(2024, 5, 12, 0, 0, tzinfo=kst),
    catchup=False,  
    tags=['update', 'daily', 'characters']
) as dag:
    
    send_start_message_to_slack = SlackWebhookOperator(
        task_id="send_start_message_to_slack",
        slack_webhook_conn_id="pyneople-slack",
        message=f"Start DAG : update_characters_table\nStart time : {now_kst.strftime("%Y-%m-%d %H:%M:%S")}"
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
            'mongo_collection_name' : mongo_collection_name,
            'error_collection_name' : error_collection_name,
            'max_fame' : max_fame
        }
    )

    send_complete_api_to_mongo_message_to_slack = SlackWebhookOperator(
        task_id="send_complete_api_to_mongo_message_to_slack",
        slack_webhook_conn_id="pyneople-slack",
        message=f"캐릭터 명성 정보 MongoDB에 저장 완료"
    )

    clear_staging_table = SQLExecuteQueryOperator(
        task_id = 'clear_staging_table',
        conn_id = 'pyneople-postgres',
        sql=f"TRUNCATE TABLE {psql_staging_table_name};",
    )

    to_psql = PythonOperator(
        task_id='to_psql',
        python_callable=mongo_to_psql,
        op_kwargs = {
            'endpoints' : endpoints, 
            'mongo_collection_name' : mongo_collection_name,
            'error_collection_name' : error_collection_name,
            'num_queue_to_psql_workers' : 10
        }
    )

    send_complete_mongo_to_psql_message_to_slack = SlackWebhookOperator(
        task_id="send_complete_mongo_to_psql_message_to_slack",
        slack_webhook_conn_id="pyneople-slack",
        message=f"캐릭터 명성 정보 PostgreSQL staging_character_fame table에 스테이징 완료"
    )

    to_clickhouse = PythonOperator(
        task_id='to_clickhouse',
        python_callable=psql_to_clickhouse,
        op_kwargs={
            'sql' : sql,
            'snapshot_date' : date.today(),
            'click_house_table_name': 'character_fame_history',
        }
    )

    staging_character_fmae_to_character_table = SQLExecuteQueryOperator(
        task_id = 'staging_character_fame_to_charater_table',
        conn_id = 'pyneople-postgres',
        sql=staging_character_fame_to_charater_sql,
    )    

    send_complete_message_to_slack = SlackWebhookOperator(
        task_id="send_complete_message_to_slack",
        slack_webhook_conn_id="pyneople-slack",
        message=f"character_fame DAG 실행 완료"
    )

    (
        send_start_message_to_slack 
        >> clear_mongo_collections
        >> to_mongo 
        >> send_complete_api_to_mongo_message_to_slack 
        >> clear_staging_table
        >> to_psql 
        >> send_complete_mongo_to_psql_message_to_slack 
        >> [to_clickhouse, staging_character_fmae_to_character_table]
        >> send_complete_message_to_slack
    )
import asyncio
from pyneople.config.config import Settings
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from motor.motor_asyncio import AsyncIOMotorCollection
import aiohttp
import requests
import pendulum
import logging
logger = logging.getLogger(__name__)

async def count_requests_per_second(shutdown_event : asyncio.Event):
    """
    1초에 얼마나 많은 요청을 하는지 확인하는 함수
    """
    while not shutdown_event.is_set():
        await asyncio.sleep(1)
        logger.info(f"초당 요청 수: {Settings.request_count}")
        Settings.request_count = 0

async def send_slack_alert(session : aiohttp.ClientSession, message : str):
    """
    Slack 알림을 보내는 비동기 함수
    """
    try:
        message = str(message)
        async with session.post(Settings.SLACK_WEBHOOK_URL, json={"text": message}) as resp:
            if resp.status != 200:
                error_detail = await resp.text()
                logger.error(f'Slack 알림 실패: {resp.status} - {error_detail}')
    except Exception as e:
        logger.error(f'Slack 알림 중 예외 발생: {e}')  

def send_slack_alert_sync(message : str):
    """
    Slack 알림을 보내는 동기 함수
    """
    try:
        message = str(message)
        response = requests.post(Settings.SLACK_WEBHOOK_URL, json={"text": message})
        if response.status_code != 200:
            logger.error(f'Slack 알림 실패: {response.status_code} - {response.text}')
    except Exception as e:
        logger.error(f'Slack 알림 중 예외 발생: {e}')

async def monitoring_error_collection(
    shutdown_event:asyncio.Event,
    error_collection: AsyncIOMotorCollection,
    threshold: int = 60,
    interval: int = 60,
):
    """
    MongoDB Error Collection을 주기적으로 감시해서 
    특정 에러가 interval초 내에 threshold회 이상 발생하면 경고를 출력

    Args:
        collection: MongoDB 컬렉션 (motor)
        error_type: 감시할 에러 타입 이름 (ex: "RetryableError")
        threshold: 에러 발생 허용 횟수
        interval: 에러 발생을 감시할 시간 범위 (초 단위)
        check_interval: 몇 초마다 감시할지 (주기)
    """
    while True:
        try:
            now = datetime.now(timezone.utc)
            since = now - timedelta(seconds=interval)

            count = await error_collection.count_documents({
                "timestamp": {"$gte": since},
                'error_data.error.code' : {"$ne": 'DNF001'}
            })

            if count >= threshold:
                logger.warning(
                    f"[ALERT] {interval}초 내에 에러가 {count}회 발생했습니다! (임계값: {threshold})"
                )
                shutdown_event.set()
                break
        except Exception as e:
            logger.error(f"예외 발생: {e}")

        await asyncio.sleep(interval)



def _slack_notify(context, task_type):
    """
    Airflow DAG deafault argument에서 사용되는 함수
    """
    kst = pendulum.timezone("Asia/Seoul")
    now_str = datetime.now(tz=kst).strftime("%Y-%m-%d %H:%M:%S")
    if not context:
        requests.post(Settings.SLACK_WEBHOOK_URL, json={'text' : f'context is empty dict DAG {task_type} \n{task_type} 시각 : {now_str}'})
    else:
        try:
            dag_id = context['dag'].dag_id
            task_id = context['task'].task_id
            execution_date = context['dag_run'].logical_date.astimezone(kst).strftime("%Y-%m-%d %H:%M:%S")      
        except Exception as e:
            requests.post(Settings.SLACK_WEBHOOK_URL, json={'text' : f'context error : {str(e)}'})
        
        message = f"""
        Airflow Task {task_type}
        DAG ID : {dag_id}
        Task ID : {task_id}
        실행 시각 : {execution_date}
        """    
        requests.post(Settings.SLACK_WEBHOOK_URL, json={'text' : message})

def slack_notify_on_success(context):
    """
    Airflow DAG deafault argument에서 사용되는 함수
    """
    _slack_notify(context, '성공')
def slack_notify_on_failure(context):
    """
    Airflow DAG deafault argument에서 사용되는 함수
    """
    _slack_notify(context, '실패')
def slack_notify_on_excute(context):
    """
    Airflow DAG deafault argument에서 사용되는 함수
    """
    _slack_notify(context, '실행')
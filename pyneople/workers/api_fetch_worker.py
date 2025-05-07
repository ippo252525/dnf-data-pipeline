import asyncio
import aiohttp
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorCollection
from pyneople.utils.api_utils.url_builder import build_url
from pyneople.api.registry.endpoint_registry import EndpointRegistry
from pyneople.config.config import Settings
from pyneople.utils.common import NotFoundCharacterError
import logging

logger = logging.getLogger(__name__)

class APIFetchWorker:
    
    def __init__(self, api_request_queue: asyncio.Queue, 
                 data_queue: asyncio.Queue, 
                 session : aiohttp.ClientSession, 
                 shutdown_event : asyncio.Event, 
                 error_collection : AsyncIOMotorCollection,
                 max_retries : int = Settings.DEFAULT_API_FETCH_WORKER_MAX_RETRIES,
                 timeout : float = Settings.DEFAULT_API_FETCH_WORKER_TIMEOUT,
                 name : str = 'APIFetchWorker'):
        self.api_request_queue = api_request_queue
        self.data_queue = data_queue
        self.session = session
        self.shutdown_event = shutdown_event
        self.error_collection = error_collection
        self.max_retries = max_retries
        self.timeout = timeout
        self.name = name
    
    async def run(self):
        while not self.shutdown_event.is_set():
            api_request = None
            try:
                api_request = await self.get_api_request()
                if api_request is None:
                    continue
                data = await self.fetch_with_retries(api_request)
                endpoint = api_request['endpoint']
                endpoint_class = EndpointRegistry.get_class(endpoint)
                if endpoint_class.has_next:
                    next_parameter = endpoint_class.build_next_api_request(data, api_request)
                    if next_parameter:
                        await self.api_request_queue.put(next_parameter)
                data.update({'fetched_at' : datetime.now(timezone.utc)})
                data = {'endpoint' : api_request['endpoint'], 'data' : data}
                await self.data_queue.put(data)   
            
            except(asyncio.TimeoutError, NotFoundCharacterError):
                pass  
            
            except Exception as e:
                logger.error(f"API 요청 중 오류 발생: {e}")
                self.shutdown_event.set()
                break
            
            finally:
                if api_request is not None:
                    self.api_request_queue.task_done()
    
    async def get_api_request(self):
                try:
                    api_request = self.api_request_queue.get_nowait()
                except asyncio.QueueEmpty:
                    try:
                        api_request = await asyncio.wait_for(self.api_request_queue.get(), timeout=self.timeout)
                    except asyncio.TimeoutError:
                        api_request = None
                return api_request
            
    async def fetch_with_retries(self, api_request: dict):
        url = build_url(api_request)
        attempt = 0
        
        while attempt <= self.max_retries:
            Settings.request_count += 1
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        try:
                            error_data = await response.json()
                            await self.save_error_log(api_request, error_data, datetime.now(timezone.utc))
                            error_code = error_data.get("error", {}).get("code")
                        except Exception:
                            error_code = None
                        
                        if error_code == "DNF001":
                            logger.warning(f"해당 캐릭터 없음")
                            raise NotFoundCharacterError()
                        else:
                            response.raise_for_status()
            except asyncio.TimeoutError as e:
                attempt += 1
                if attempt > self.max_retries:
                    logger.warning(f"요청 실패, 재시도 {self.max_retries}회 초과")
                    await self.save_error_log(api_request, e.__class__.__name__, datetime.now(timezone.utc))
                    raise e
                else:
                    logger.warning(f"요청 실패: {url} (재시도 {attempt}/{self.max_retries}) - {e}")
                    backoff_time = min(2 ** attempt, 30)
                    await asyncio.sleep(backoff_time)

    async def flush_queue(self):
        while not self.api_request_queue.empty():
            try:
                _ = self.api_request_queue.get_nowait()
                self.api_request_queue.task_done()
            except asyncio.QueueEmpty:
                break           

    async def save_error_log(self, api_request, error_data, fetched_at):
        error_doc = {
            'api_request' : api_request,
            'error_data' : error_data,
            'fetched_at' : fetched_at
        }
        await self.error_collection.insert_one(error_doc)        
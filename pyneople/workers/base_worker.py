from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import asyncio

class BaseWorker(ABC):
    def __init__(self, 
                 queue: Any, 
                 batch_size: int,
                 shutdown_event: asyncio.Event):
        self.queue = queue
        self.batch_size = batch_size
        self.shutdown_event = shutdown_event

    async def run(self):
        """
        Worker의 메인 루프를 실행합니다.
        """
        while not self.shutdown_event.is_set():
            batch = []
            try:
                batch = await self._collect_batch()
                await self._process_batch(batch)
            except Exception as e:
                print(f"Error processing batch: {e}")
                self.shutdown_event.set()
                break
            finally:
                for _ in batch:
                    self.queue.task_done()

    async def _collect_batch(self):
        """
        큐에서 배치를 수집합니다.
        """
        batch = []
        
        while len(batch) < self.batch_size:
            
            try:
                data = self.queue.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.01)
                continue
            batch.append(data)

        if any(isinstance(item, list) for item in batch):
            pass
    
    @abstractmethod
    def _process_batch(self, batch: List[Dict[str, Any]]):
        """
        수집된 배치를 처리합니다.
        """
        pass
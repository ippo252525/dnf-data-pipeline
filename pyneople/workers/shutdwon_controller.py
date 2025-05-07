import asyncio
import logging

logger = logging.getLogger(__name__)

class ShutdownController:
    """
    shutdown 이벤트 발생 시 모든 워커 태스크를 종료하고 큐를 정리하는 컨트롤러 클래스

    Attributes:
        queues (list[asyncio.Queue]): 비워야 할 asyncio.Queue 리스트
        shutdown_event (asyncio.Event): shutdown 신호를 감지하는 이벤트
        worker_tasks (list[asyncio.Task]): 종료 대상 asyncio 태스크 리스트
        name (str): 컨트롤러 이름
    """    
    def __init__(self,
                 queues: list[asyncio.Queue],
                 shutdown_event: asyncio.Event,
                 worker_tasks: list[asyncio.Task],
                 name: str = "ShutdownController"):
        self.queues = queues
        self.shutdown_event = shutdown_event
        self.worker_tasks = worker_tasks
        self.name = name

    async def run(self):
        """
        shutdown_event 발생을 대기하고 워커 종료 및 큐 정리를 수행하는 메서드

        shutdown 이벤트가 감지되면 다음을 순차적으로 수행함:
        1. 모든 워커 태스크를 cancel
        2. 모든 큐를 비움 (queue.get_nowait + task_done)
        3. 모든 태스크의 종료를 await

        예외 발생 여부와 관계없이 안전한 shutdown 절차 보장을 목표로 함
        """        
        logger.info(f"[{self.name}] shutdown 이벤트 대기 중")
        await self.shutdown_event.wait()
        logger.warning(f"[{self.name}] shutdown 감지 — 모든 워커 종료 및 큐 정리 시작")

        # 워커 태스크 취소
        for task in self.worker_tasks:
            if not task.done():
                task.cancel()
                logger.info(f"[{self.name}] 취소된 task: {task.get_name()}")

        # 큐 정리
        for idx, queue in enumerate(self.queues):
            while not queue.empty():
                try:
                    queue.get_nowait()
                    queue.task_done()
                except asyncio.QueueEmpty:
                    break
            logger.info(f"[{self.name}] 큐 {idx} 비우기 완료 — 남은 항목 수: {queue.qsize()}")
        logger.warning(f"[{self.name}] 모든 워커 종료 및 큐 정리 완료")

        # 모든 태스크 완료 대기
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)

"""
Celery tasks for background processing.

These are example tasks that demonstrate how to use Celery.
Add your custom tasks here.
"""
import logging
import time
from typing import Dict, Any

from app.worker.main import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.worker.tasks.add_numbers")
def add_numbers(x: int, y: int) -> int:
    """
    Simple task that adds two numbers.
    
    Args:
        x: First number
        y: Second number
    
    Returns:
        Sum of x and y
    """
    logger.info(f"Adding {x} + {y}")
    result = x + y
    logger.info(f"Result: {result}")
    return result


@celery_app.task(name="app.worker.tasks.process_data")
def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example task that processes some data.
    
    Args:
        data: Dictionary of data to process
    
    Returns:
        Processed data dictionary
    """
    logger.info(f"Processing data: {data}")
    
    # Simulate some processing
    time.sleep(2)
    
    processed = {
        "status": "processed",
        "original_data": data,
        "processed_at": time.time(),
    }
    
    logger.info(f"Data processed: {processed}")
    return processed


@celery_app.task(name="app.worker.tasks.long_running_task", bind=True)
def long_running_task(self, duration: int = 10) -> Dict[str, Any]:
    """
    Example long-running task that updates progress.
    
    Args:
        self: Task instance (auto-injected when bind=True)
        duration: How long to run (in seconds)
    
    Returns:
        Result dictionary with task metadata
    """
    logger.info(f"Starting long running task for {duration} seconds")
    
    for i in range(duration):
        # Update task state with progress
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': duration,
                'status': f'Processing step {i + 1} of {duration}'
            }
        )
        time.sleep(1)
    
    result = {
        "status": "completed",
        "duration": duration,
        "task_id": self.request.id,
    }
    
    logger.info(f"Long running task completed: {result}")
    return result


@celery_app.task(name="app.worker.tasks.task_with_retry", bind=True, max_retries=3)
def task_with_retry(self, should_fail: bool = False) -> Dict[str, Any]:
    """
    Example task that demonstrates retry logic.
    
    Args:
        self: Task instance (auto-injected when bind=True)
        should_fail: Whether to simulate a failure
    
    Returns:
        Result dictionary
    
    Raises:
        Exception: If should_fail is True and retries exhausted
    """
    logger.info(f"Running task_with_retry (attempt {self.request.retries + 1})")
    
    if should_fail and self.request.retries < 2:
        logger.warning(f"Task failed, retrying... (attempt {self.request.retries + 1})")
        raise self.retry(countdown=5)  # Retry after 5 seconds
    
    result = {
        "status": "success",
        "attempts": self.request.retries + 1,
        "task_id": self.request.id,
    }
    
    logger.info(f"Task completed successfully: {result}")
    return result


__all__ = [
    "add_numbers",
    "process_data",
    "long_running_task",
    "task_with_retry",
]


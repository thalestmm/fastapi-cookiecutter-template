"""
Celery client utilities for submitting and monitoring tasks.

This module provides helper functions to interact with Celery tasks
from your FastAPI application.
"""
import logging
from typing import Optional, Dict, Any
from celery.result import AsyncResult

from app.worker.main import celery_app

logger = logging.getLogger(__name__)


def submit_task(task_name: str, *args, **kwargs) -> AsyncResult:
    """
    Submit a task to the Celery worker.
    
    Args:
        task_name: Name of the task to execute
        *args: Positional arguments for the task
        **kwargs: Keyword arguments for the task
    
    Returns:
        AsyncResult object for tracking the task
    
    Example:
        >>> result = submit_task('app.worker.tasks.add_numbers', 5, 3)
        >>> print(result.id)
        >>> print(result.status)
    """
    logger.info(f"Submitting task: {task_name} with args={args}, kwargs={kwargs}")
    result = celery_app.send_task(task_name, args=args, kwargs=kwargs)
    logger.info(f"Task submitted with ID: {result.id}")
    return result


def get_task_result(task_id: str) -> AsyncResult:
    """
    Get the result object for a task by its ID.
    
    Args:
        task_id: The task ID to look up
    
    Returns:
        AsyncResult object for the task
    
    Example:
        >>> result = get_task_result('some-task-id')
        >>> if result.ready():
        >>>     print(result.result)
    """
    return AsyncResult(task_id, app=celery_app)


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status and result of a task.
    
    Args:
        task_id: The task ID to check
    
    Returns:
        Dictionary containing task status information
    
    Example:
        >>> status = get_task_status('some-task-id')
        >>> print(status['state'])
        >>> print(status['result'])
    """
    result = get_task_result(task_id)
    
    response = {
        "task_id": task_id,
        "state": result.state,
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else None,
        "result": None,
        "error": None,
    }
    
    if result.ready():
        if result.successful():
            response["result"] = result.result
        else:
            response["error"] = str(result.info)
    elif result.state == 'PROGRESS':
        response["result"] = result.info
    
    return response


def revoke_task(task_id: str, terminate: bool = False) -> Dict[str, str]:
    """
    Revoke/cancel a task.
    
    Args:
        task_id: The task ID to revoke
        terminate: If True, terminate the task if it's already running
    
    Returns:
        Dictionary with revocation status
    
    Example:
        >>> revoke_task('some-task-id', terminate=True)
    """
    logger.info(f"Revoking task: {task_id} (terminate={terminate})")
    celery_app.control.revoke(task_id, terminate=terminate)
    return {"task_id": task_id, "status": "revoked"}


def get_active_tasks() -> Dict[str, Any]:
    """
    Get list of currently active tasks.
    
    Returns:
        Dictionary containing active tasks information
    """
    inspect = celery_app.control.inspect()
    active = inspect.active()
    return {"active_tasks": active or {}}


def get_worker_stats() -> Dict[str, Any]:
    """
    Get statistics about active workers.
    
    Returns:
        Dictionary containing worker statistics
    """
    inspect = celery_app.control.inspect()
    stats = inspect.stats()
    return {"worker_stats": stats or {}}


__all__ = [
    "submit_task",
    "get_task_result",
    "get_task_status",
    "revoke_task",
    "get_active_tasks",
    "get_worker_stats",
]

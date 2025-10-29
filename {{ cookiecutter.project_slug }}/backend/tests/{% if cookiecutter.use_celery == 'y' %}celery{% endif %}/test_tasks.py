"""
Tests for Celery tasks.
"""
import pytest
from unittest.mock import patch, MagicMock

from app.worker.tasks import (
    add_numbers,
    process_data,
    long_running_task,
    task_with_retry,
)
from app.worker.client import (
    submit_task,
    get_task_status,
    get_task_result,
)


@pytest.mark.celery
class TestCeleryTasks:
    """Test cases for Celery tasks."""
    
    def test_add_numbers_task(self, celery_test_app):
        """
        Test the add_numbers task.
        """
        result = add_numbers.apply(args=[5, 3])
        assert result.get() == 8
    
    def test_add_numbers_with_negative(self, celery_test_app):
        """
        Test add_numbers with negative numbers.
        """
        result = add_numbers.apply(args=[-5, 3])
        assert result.get() == -2
    
    def test_process_data_task(self, celery_test_app):
        """
        Test the process_data task.
        """
        test_data = {"key": "value", "number": 42}
        result = process_data.apply(args=[test_data])
        
        output = result.get()
        assert output["status"] == "processed"
        assert output["original_data"] == test_data
        assert "processed_at" in output
    
    def test_long_running_task(self, celery_test_app):
        """
        Test the long_running_task.
        
        Note: With task_always_eager=True, this runs synchronously
        and doesn't actually test progress updates.
        """
        result = long_running_task.apply(kwargs={"duration": 2})
        
        output = result.get()
        assert output["status"] == "completed"
        assert output["duration"] == 2
        assert "task_id" in output
    
    def test_task_with_retry_success(self, celery_test_app):
        """
        Test task_with_retry when it succeeds.
        """
        result = task_with_retry.apply(kwargs={"should_fail": False})
        
        output = result.get()
        assert output["status"] == "success"
        assert output["attempts"] == 1


@pytest.mark.celery
class TestCeleryClient:
    """Test cases for Celery client utilities."""
    
    @patch('app.worker.client.celery_app')
    def test_submit_task(self, mock_celery_app):
        """
        Test task submission via client.
        """
        mock_result = MagicMock()
        mock_result.id = "test-task-id"
        mock_celery_app.send_task.return_value = mock_result
        
        result = submit_task("app.worker.tasks.add_numbers", 5, 3)
        
        assert result.id == "test-task-id"
        mock_celery_app.send_task.assert_called_once()
    
    @patch('app.worker.client.AsyncResult')
    def test_get_task_result(self, mock_async_result):
        """
        Test getting task result by ID.
        """
        mock_result = MagicMock()
        mock_async_result.return_value = mock_result
        
        result = get_task_result("test-task-id")
        
        assert result == mock_result
        mock_async_result.assert_called_once_with("test-task-id", app=None)
    
    @patch('app.worker.client.get_task_result')
    def test_get_task_status_pending(self, mock_get_result):
        """
        Test getting status of a pending task.
        """
        mock_result = MagicMock()
        mock_result.state = "PENDING"
        mock_result.ready.return_value = False
        mock_get_result.return_value = mock_result
        
        status = get_task_status("test-task-id")
        
        assert status["task_id"] == "test-task-id"
        assert status["state"] == "PENDING"
        assert status["ready"] is False
        assert status["result"] is None
    
    @patch('app.worker.client.get_task_result')
    def test_get_task_status_success(self, mock_get_result):
        """
        Test getting status of a successful task.
        """
        mock_result = MagicMock()
        mock_result.state = "SUCCESS"
        mock_result.ready.return_value = True
        mock_result.successful.return_value = True
        mock_result.result = 42
        mock_get_result.return_value = mock_result
        
        status = get_task_status("test-task-id")
        
        assert status["task_id"] == "test-task-id"
        assert status["state"] == "SUCCESS"
        assert status["ready"] is True
        assert status["successful"] is True
        assert status["result"] == 42
    
    @patch('app.worker.client.get_task_result')
    def test_get_task_status_failure(self, mock_get_result):
        """
        Test getting status of a failed task.
        """
        mock_result = MagicMock()
        mock_result.state = "FAILURE"
        mock_result.ready.return_value = True
        mock_result.successful.return_value = False
        mock_result.info = Exception("Task failed")
        mock_get_result.return_value = mock_result
        
        status = get_task_status("test-task-id")
        
        assert status["task_id"] == "test-task-id"
        assert status["state"] == "FAILURE"
        assert status["ready"] is True
        assert status["successful"] is False
        assert "Task failed" in str(status["error"])


@pytest.mark.unit
class TestTaskLogic:
    """Unit tests for task logic without Celery."""
    
    def test_add_numbers_logic(self):
        """
        Test the add_numbers function logic directly.
        """
        # Import the function and test it directly
        from app.worker.tasks import add_numbers
        
        # Test with task_always_eager
        result = add_numbers.apply(args=[10, 20])
        assert result.get() == 30
    
    def test_process_data_logic(self):
        """
        Test the process_data function logic directly.
        """
        from app.worker.tasks import process_data
        
        test_data = {"test": "data"}
        result = process_data.apply(args=[test_data])
        output = result.get()
        
        assert "status" in output
        assert "original_data" in output
        assert output["original_data"] == test_data


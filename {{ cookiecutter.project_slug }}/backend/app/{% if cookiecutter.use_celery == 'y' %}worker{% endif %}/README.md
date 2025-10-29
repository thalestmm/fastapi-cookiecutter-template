# Celery Worker Documentation

This directory contains the Celery worker configuration for background task processing.

## Overview

The application uses **Celery** with **RabbitMQ** as the message broker and **Redis** as the result backend for asynchronous task processing.

## Architecture

- **Message Broker**: RabbitMQ (handles task queuing)
- **Result Backend**: Redis (stores task results)
- **Worker**: Celery worker that processes tasks

## Files

- `main.py` - Celery application configuration
- `tasks.py` - Task definitions
- `client.py` - Client utilities for task submission and monitoring
- `__init__.py` - Package initialization

## Running the Worker

### Using Docker Compose (Recommended)

```bash
docker-compose up celery_worker
```

### Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start RabbitMQ and Redis:
```bash
docker-compose up rabbitmq redis
```

3. Set environment variables:
```bash
export CELERY_BROKER_URL="amqp://admin:password@localhost:5672//"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
```

4. Start the worker:
```bash
celery -A app.worker.main worker --loglevel=info
```

## Creating Tasks

### Basic Task

```python
from app.worker.main import celery_app

@celery_app.task(name="app.worker.tasks.my_task")
def my_task(arg1, arg2):
    """Your task logic here."""
    result = arg1 + arg2
    return result
```

### Task with Progress Updates

```python
@celery_app.task(name="app.worker.tasks.long_task", bind=True)
def long_task(self, total_steps):
    """Task that reports progress."""
    for i in range(total_steps):
        self.update_state(
            state='PROGRESS',
            meta={'current': i, 'total': total_steps}
        )
        # Do work...
    return {'status': 'completed'}
```

### Task with Retry Logic

```python
@celery_app.task(name="app.worker.tasks.retry_task", bind=True, max_retries=3)
def retry_task(self, data):
    """Task with automatic retry on failure."""
    try:
        # Do something that might fail
        result = process_data(data)
        return result
    except Exception as exc:
        # Retry after 60 seconds
        raise self.retry(exc=exc, countdown=60)
```

## Using Tasks via API

### Submit a Task

```bash
POST /api/v1/tasks/submit
{
    "task_name": "app.worker.tasks.add_numbers",
    "args": [5, 3],
    "kwargs": {}
}
```

Response:
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "submitted"
}
```

### Check Task Status

```bash
GET /api/v1/tasks/{task_id}
```

Response:
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "state": "SUCCESS",
    "ready": true,
    "successful": true,
    "result": 8,
    "error": null
}
```

### Monitor Active Tasks

```bash
GET /api/v1/tasks/monitoring/active
```

### Get Worker Statistics

```bash
GET /api/v1/tasks/monitoring/workers
```

## Using Tasks in Python Code

### Submit a Task

```python
from app.worker.client import submit_task

# Submit task
result = submit_task('app.worker.tasks.add_numbers', 5, 3)
print(f"Task ID: {result.id}")

# Wait for result
output = result.get(timeout=10)
print(f"Result: {output}")
```

### Check Task Status

```python
from app.worker.client import get_task_status

status = get_task_status(task_id)
print(f"State: {status['state']}")
print(f"Result: {status['result']}")
```

### Import and Call Task Directly

```python
from app.worker.tasks import add_numbers

# Submit asynchronously
result = add_numbers.delay(5, 3)

# Or apply async with options
result = add_numbers.apply_async(
    args=[5, 3],
    countdown=10,  # Execute after 10 seconds
    expires=3600,  # Task expires after 1 hour
)
```

## Configuration

### Celery Settings (main.py)

Key configuration options:

- `task_serializer`: JSON (secure)
- `task_time_limit`: 30 minutes (hard limit)
- `task_soft_time_limit`: 25 minutes (soft limit)
- `task_acks_late`: True (acknowledge after completion)
- `worker_prefetch_multiplier`: 1 (fetch one task at a time)
- `result_expires`: 3600 seconds (1 hour)

### Environment Variables

```bash
# RabbitMQ Configuration
RABBITMQ_USER=admin
RABBITMQ_PASS=your-password
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Celery URLs
CELERY_BROKER_URL=amqp://admin:password@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## Monitoring

### RabbitMQ Management UI

Access the RabbitMQ management interface at:
- URL: http://localhost:15672
- Default credentials: See `.env` file

### Celery Flower (Optional)

Install and run Flower for advanced monitoring:

```bash
pip install flower
celery -A app.worker.main flower
```

Access at: http://localhost:5555

## Task States

- `PENDING` - Task is waiting to be executed
- `STARTED` - Task has been started
- `PROGRESS` - Task is running and reporting progress
- `SUCCESS` - Task completed successfully
- `FAILURE` - Task failed with an error
- `RETRY` - Task is being retried
- `REVOKED` - Task was cancelled

## Best Practices

1. **Keep tasks idempotent** - Tasks should be safe to retry
2. **Use timeouts** - Set appropriate time limits for tasks
3. **Handle failures gracefully** - Implement proper error handling
4. **Log appropriately** - Use logging for debugging
5. **Test tasks** - Write unit tests for your tasks
6. **Monitor workers** - Keep an eye on worker health and performance
7. **Use task names** - Always name your tasks explicitly
8. **Avoid long-running tasks** - Break them into smaller chunks if possible

## Troubleshooting

### Worker Not Connecting

- Check RabbitMQ is running: `docker-compose ps rabbitmq`
- Verify environment variables are set correctly
- Check RabbitMQ logs: `docker-compose logs rabbitmq`

### Tasks Not Executing

- Ensure worker is running: `docker-compose ps celery_worker`
- Check worker logs: `docker-compose logs celery_worker`
- Verify task name is correct
- Check RabbitMQ has the task queue

### Results Not Available

- Verify Redis is running: `docker-compose ps redis`
- Check Redis connection: `redis-cli ping`
- Ensure `CELERY_RESULT_BACKEND` is configured

## Example Tasks

The template includes several example tasks in `tasks.py`:

1. `add_numbers` - Simple addition task
2. `process_data` - Data processing with delay
3. `long_running_task` - Task with progress updates
4. `task_with_retry` - Task with retry logic

Feel free to modify or remove these examples for your use case.

## Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Redis Documentation](https://redis.io/documentation)


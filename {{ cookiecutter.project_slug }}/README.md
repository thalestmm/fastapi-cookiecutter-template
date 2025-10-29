# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Getting Started

### Prerequisites

- Python {{ cookiecutter.python_version }}+
{% if cookiecutter.use_docker == 'y' %}- Docker and Docker Compose{% endif %}
{% if cookiecutter.use_celery == 'y' %}- RabbitMQ and Redis (included in Docker Compose){% endif %}

### Setup

{% if cookiecutter.use_docker == 'y' %}
#### Using Docker Compose (Recommended)

1. Copy the environment file and configure:
```bash
cp .env.example .env.local
# Edit .env.local with your settings
```

2. Start all services:
```bash
docker-compose up -d
```

3. Access the application:
- Backend API: http://localhost:{{ cookiecutter.backend_port }}
- API Documentation: http://localhost:{{ cookiecutter.backend_port }}/docs
{% if cookiecutter.use_celery == 'y' %}- RabbitMQ Management: http://localhost:15672{% endif %}

{% endif %}
#### Local Development

1. Create and activate virtual environment:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp ../.env.example .env.local
# Edit .env.local with your settings
```

4. Run the application:
```bash
uvicorn app.main:app --reload --port {{ cookiecutter.backend_port }}
```

{% if cookiecutter.use_celery == 'y' %}
5. Start Celery worker (in a separate terminal):
```bash
celery -A app.worker.main worker --loglevel=info
```
{% endif %}

## Project Structure

```
{{ cookiecutter.project_slug }}/
├── backend/
│   ├── app/
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Settings management
│   │   │   └── logging_config.py
{% if cookiecutter.use_celery == 'y' %}│   │   ├── worker/            # Celery workers
│   │   │   ├── main.py        # Celery app
│   │   │   ├── tasks.py       # Task definitions
│   │   │   └── client.py      # Task utilities
{% endif %}│   │   ├── routers/           # API routes
│   │   ├── schemas/           # Pydantic models
│   │   ├── services/          # Business logic
│   │   ├── security/          # Auth logic
│   │   └── main.py            # FastAPI app
│   ├── requirements.txt
{% if cookiecutter.use_docker == 'y' %}│   └── Dockerfile
├── docker-compose.yml
{% endif %}└── .env.example
```

## API Documentation

Interactive API documentation is available in development mode:
- Swagger UI: http://localhost:{{ cookiecutter.backend_port }}/docs
- ReDoc: http://localhost:{{ cookiecutter.backend_port }}/redoc

## Available Endpoints

### Health Check
- `GET /` - Root endpoint (redirects to docs in development)
- `GET /health` - Basic health check
- `GET /health/live` - Kubernetes liveness probe
- `GET /health/ready` - Kubernetes readiness probe (checks dependencies)
- `GET /health/startup` - Kubernetes startup probe

**Note:** Health endpoints are at root level (not versioned under `/api/v1/`) for infrastructure stability.

{% if cookiecutter.use_celery == 'y' %}
### Task Management (Celery)
- `POST /api/v1/tasks/submit` - Submit a background task
- `GET /api/v1/tasks/{task_id}` - Check task status
- `DELETE /api/v1/tasks/{task_id}` - Cancel a task
- `GET /api/v1/tasks/monitoring/active` - List active tasks
- `GET /api/v1/tasks/monitoring/workers` - Worker statistics

#### Example Tasks
- `POST /api/v1/tasks/examples/add?x=5&y=3` - Add two numbers
- `POST /api/v1/tasks/examples/process` - Process data
- `POST /api/v1/tasks/examples/long-running?duration=10` - Long-running task

For more details, see [backend/app/worker/README.md](backend/app/worker/README.md)

#### Flower Monitoring
- URL: http://localhost:5555
- Credentials: `FLOWER_USER` and `FLOWER_PASS` from `.env.local`
{% endif %}

{% if cookiecutter.ai_project == 'y' %}
### AI Agent (LangGraph)
- `POST /api/v1/agent/query` - Simple query without history
- `POST /api/v1/agent/chat` - Chat with conversation history

#### Example Usage
```bash
# Simple query
curl -X POST "http://localhost:{{ cookiecutter.backend_port }}/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 15 * 8?"}'

# Chat with history
curl -X POST "http://localhost:{{ cookiecutter.backend_port }}/api/v1/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about Python",
    "conversation_history": []
  }'
```

For more details, see [backend/app/graphs/README.md](backend/app/graphs/README.md)
{% endif %}

{% if cookiecutter.use_celery == 'y' %}
## Using Celery Tasks

### Submit a Task
```python
from app.worker.client import submit_task

# Submit task
result = submit_task('app.worker.tasks.add_numbers', 5, 3)
task_id = result.id

# Check status
from app.worker.client import get_task_status
status = get_task_status(task_id)
print(status)
```

### Create New Tasks

Add tasks to `backend/app/worker/tasks.py`:
```python
from app.worker.main import celery_app

@celery_app.task(name="app.worker.tasks.my_custom_task")
def my_custom_task(data):
    # Your logic here
    return result
```
{% endif %}

## Configuration

Environment variables are loaded from `.env.local`. Available settings:

```bash
# Environment
ENVIRONMENT=development
LOG_LEVEL=DEBUG

{% if cookiecutter.use_celery == 'y' %}
# Celery
RABBITMQ_USER=admin
RABBITMQ_PASS=your-password
CELERY_BROKER_URL=amqp://admin:password@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0
{% endif %}

{% if cookiecutter.ai_project == 'y' %}
# LLM / AI
LLM_MODEL=gpt-4
OPENAI_API_KEY=your-api-key
{% endif %}

{% if cookiecutter.use_supabase == 'y' %}
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key
{% endif %}
```

## Development

### Running Tests

The project includes a comprehensive test suite with pytest.

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests

# Run specific test file
pytest tests/test_main.py

# Run with verbose output
pytest -v
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

For more details, see [backend/tests/README.md](backend/tests/README.md)

### Code Formatting
```bash
black app/
isort app/
```

### Type Checking
```bash
mypy app/
```

{% if cookiecutter.use_docker == 'y' %}
### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
{% if cookiecutter.use_celery == 'y' %}docker-compose logs -f celery_worker{% endif %}
```

### Rebuilding Containers
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```
{% endif %}

## Deployment

### Production Checklist

1. Set `ENVIRONMENT=production` in `.env`
2. Use strong passwords for all services
3. Configure CORS origins properly
4. Set up proper logging and monitoring
5. Use HTTPS/TLS
6. Set up database backups
{% if cookiecutter.use_celery == 'y' %}7. Monitor Celery workers with Flower or similar{% endif %}

## Troubleshooting

### Common Issues

{% if cookiecutter.use_docker == 'y' %}
**Services not starting:**
```bash
docker-compose down -v
docker-compose up --build
```
{% endif %}

{% if cookiecutter.use_celery == 'y' %}
**Celery worker not processing tasks:**
- Check worker is running: `docker-compose ps celery_worker`
- View worker logs: `docker-compose logs celery_worker`
- Verify RabbitMQ connection: `docker-compose logs rabbitmq`

**Tasks stuck in pending:**
- Ensure task name matches exactly
- Check worker is subscribed to the correct queue
- Verify broker URL is correct
{% endif %}

**Port already in use:**
```bash
# Find process using port {{ cookiecutter.backend_port }}
lsof -i :{{ cookiecutter.backend_port }}
# Kill process or change port in docker-compose.yml
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

[Your License Here]

## Author

{{ cookiecutter.author }} ({{ cookiecutter.email }})


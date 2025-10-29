# TM - FastAPI Template

A comprehensive FastAPI project template with optional support for Celery workers, Supabase, and AI integrations.

This project uses Python `cookiecutter` as the template manager to generate production-ready FastAPI applications.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **Docker & Docker Compose** - Containerized development and deployment
- **Celery** (optional) - Distributed task queue for background processing
  - RabbitMQ as message broker
  - Redis as result backend
  - Pre-configured worker setup with example tasks
  - Task management API endpoints
  - Flower monitoring UI
- **LangGraph AI Agent** (optional) - LangChain + LangGraph integration
  - Pre-built agent workflow with tool calling
  - Example tools (calculator, search)
  - Conversational API endpoints
  - Extensible node and tool system
- **Comprehensive Testing** - Full test suite with pytest
  - Unit and integration tests
  - API endpoint tests
  - Celery task tests
  - Coverage reporting
  - Test fixtures and configurations
- **Middleware Stack**
  - Request logging with unique IDs
  - Error handling and standardized responses
  - Security headers
  - Rate limiting (optional)
- **PostgreSQL** (optional) - Production-ready database setup
  - SQLAlchemy ORM configuration
  - Connection pooling and health checks
  - Alembic migrations ready
  - Docker Compose integration
- **Health Checks** - Kubernetes-ready health endpoints
  - Liveness probe
  - Readiness probe  
  - Startup probe
  - Service dependency checks (DB, Redis, Celery)
- **Supabase** (optional) - Backend-as-a-Service integration
- **Structured Logging** - Production-ready logging configuration
- **API Versioning** - Organized router structure with v1 API
- **Development Tools** - Hot reload, linting, type checking

## Quick Start

### Method 1: Interactive Generator (Recommended)

If you've cloned this repository, you can use the beautiful interactive generator:

**Quick start with Make** (easiest)
```bash
make run
```

Or build and run manually:
```bash
go build -o fastapi-generator main.go
./fastapi-generator
```

The interactive generator will guide you through:
- Project name and description
- Author information
- Python version and backend port
- Feature selection (Docker, PostgreSQL, Supabase, AI, Celery)
- Automatic virtual environment setup
- Automatic cookiecutter execution

📖 For a detailed guide with screenshots and troubleshooting, see [GENERATOR_GUIDE.md](GENERATOR_GUIDE.md)

### Method 2: Using Cookiecutter Directly

#### 1. Install Cookiecutter

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install cookiecutter
```

#### 2. Generate Your Project

```bash
cookiecutter https://github.com/thalestmm/fastapi-cookiecutter-template.git
```

You'll be prompted to configure:
- Project name and description
- Author information
- Python version
- Whether to include Docker support
- Whether to include PostgreSQL database
- Whether to include Celery workers
- Whether to include Supabase integration
- Whether to set up AI project structure

## Running Your Project

### Using Docker Compose (Recommended)

```bash
cd your-project-name

# Copy and configure environment variables
cp .env.example .env.local
# Edit .env.local with your settings

# Start all services (backend, celery worker, rabbitmq, redis)
docker-compose up
```

The API will be available at:
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- PostgreSQL: localhost:5432 (if PostgreSQL is enabled)
- RabbitMQ Management: http://localhost:15672 (if Celery is enabled)
- Flower Monitoring: http://localhost:5555 (if Celery is enabled)

### Running Locally

```bash
cd your-project-name/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn app.main:app --reload --port 8000
```

If you enabled Celery, also start the worker:

```bash
# In a separate terminal
celery -A app.worker.main worker --loglevel=info
```

## Project Structure

```
your-project-name/
├── backend/
│   ├── app/
│   │   ├── core/              # Core configuration and utilities
│   │   │   ├── config.py      # Settings management
│   │   │   ├── logging_config.py
│   │   │   ├── middleware.py  # Custom middleware
│   │   │   ├── redis.py       # Redis connection (if Celery enabled)
│   │   │   └── supabase.py    # Supabase client (if enabled)
│   │   ├── routers/           # API endpoints
│   │   │   └── api/
│   │   │       └── v1/        # Version 1 API
│   │   │           ├── health.py   # Health check endpoints
│   │   │           ├── tasks.py    # Celery task endpoints (if enabled)
│   │   │           └── agent.py    # LangGraph agent endpoints (if AI enabled)
│   │   ├── schemas/           # Pydantic models
│   │   ├── services/          # Business logic
│   │   ├── security/          # Authentication & authorization
│   │   ├── worker/            # Celery configuration (if enabled)
│   │   │   ├── main.py        # Celery app
│   │   │   ├── tasks.py       # Task definitions
│   │   │   ├── client.py      # Task client utilities
│   │   │   └── README.md      # Celery documentation
│   │   ├── graphs/            # LangGraph workflows (if AI enabled)
│   │   │   ├── workflow.py    # Main workflow definition
│   │   │   ├── nodes/         # Graph nodes
│   │   │   ├── tools/         # LangChain tools
│   │   │   └── README.md      # LangGraph documentation
│   │   └── main.py            # FastAPI application
│   ├── tests/                 # Test suite
│   │   ├── conftest.py        # Test fixtures
│   │   ├── test_main.py       # API tests
│   │   ├── test_celery_tasks.py    # Celery tests (if enabled)
│   │   ├── test_celery_api.py      # Celery API tests (if enabled)
│   │   └── README.md          # Testing documentation
│   ├── pytest.ini             # Pytest configuration
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Using Celery (If Enabled)

### Submit a Task via API

```bash
curl -X POST "http://localhost:8000/api/v1/tasks/examples/add?x=5&y=3"
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
curl "http://localhost:8000/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000"
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

For more details, see the [Celery Worker Documentation](backend/app/worker/README.md).

## Using LangGraph Agent (If AI Project Enabled)

### Simple Query

```bash
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 25 * 4?"}'
```

Response:
```json
{
  "answer": "25 multiplied by 4 equals 100."
}
```

### Chat with Conversation History

```bash
curl -X POST "http://localhost:8000/api/v1/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate the square of 12",
    "conversation_history": []
  }'
```

The agent has access to tools like:
- **Calculator**: For mathematical operations
- **Search**: For finding information (implement actual search)

For more details, see the [LangGraph Documentation](backend/app/graphs/README.md).

## Health Checks

The template includes Kubernetes-ready health check endpoints at the root level (not versioned):

### Basic Health Check
```bash
curl http://localhost:8000/health
```

### Liveness Probe
```bash
curl http://localhost:8000/health/live
```

### Readiness Probe (checks dependencies)
```bash
curl http://localhost:8000/health/ready
```

### Startup Probe
```bash
curl http://localhost:8000/health/startup
```

**Note:** Health endpoints are at the root level (`/health/*`) rather than versioned (`/api/v1/health/*`) to ensure infrastructure tools (Kubernetes probes, load balancers, monitoring) have stable, unchanging URLs.

## Running Tests

### Run All Tests
```bash
cd backend
pytest
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test Types
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

For more details, see the [Testing Documentation](backend/tests/README.md).

## Configuration

All configuration is managed through environment variables. Copy `.env.example` to `.env.local` and customize:

```bash
# Environment
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# PostgreSQL (if enabled)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=your_project_db
DATABASE_URL=postgresql://postgres:password@localhost:5432/your_project_db

# Celery (if enabled)
RABBITMQ_USER=admin
RABBITMQ_PASS=your-secure-password
CELERY_BROKER_URL=amqp://admin:password@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Supabase (if enabled)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

## Development

### API Documentation

When running in development mode, interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Hot Reload

The backend automatically reloads when you make changes to the code (when using `--reload` flag or Docker Compose).

### Adding New Tasks (Celery)

1. Define your task in `backend/app/worker/tasks.py`:
```python
@celery_app.task(name="app.worker.tasks.my_task")
def my_task(arg1, arg2):
    # Your logic here
    return result
```

2. Submit from your API:
```python
from app.worker.client import submit_task
result = submit_task('app.worker.tasks.my_task', arg1, arg2)
```

## Monitoring

### Application Health
- Health endpoints: http://localhost:8000/health/*
- Request logging with unique IDs in application logs

### RabbitMQ Management Console
- URL: http://localhost:15672
- Credentials: See your `.env.local` file
- Monitor queues, exchanges, and message rates

### Flower (Celery Monitoring)
- URL: http://localhost:5555
- Credentials: See `FLOWER_USER` and `FLOWER_PASS` in `.env.local`
- Real-time task monitoring
- Worker statistics
- Task history and details

All monitoring services are automatically started with `docker-compose up`.

## Database (PostgreSQL)

If you enabled PostgreSQL, the template includes:

### SQLAlchemy Setup
- Pre-configured engine and session management
- Connection pooling
- Health checks
- Context managers for non-FastAPI code

### Usage Example

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

@app.get("/items")
def get_items(db: Session = Depends(get_db)):
    # Use db session here
    return {"items": []}
```

### Migrations

Initialize Alembic:
```bash
cd backend
alembic init alembic
# Configure alembic.ini and alembic/env.py
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Interactive Generator

The interactive generator (`main.go`) provides a beautiful, user-friendly interface for creating new FastAPI projects. Built with Go and [Bubble Tea](https://github.com/charmbracelet/bubbletea), it offers:

### Features

- **Step-by-step guidance**: Clear, focused prompts for each configuration option
- **Beautiful UI**: Color-coded interface with progress indicators
- **Smart defaults**: Pre-filled values based on best practices
- **Feature selection**: Interactive checkboxes for optional components
- **Validation**: Ensures all required fields are completed
- **Automated setup**: Creates virtual environment and runs cookiecutter automatically
- **Real-time feedback**: Shows progress and helpful next steps

### Requirements

- Go 1.25 or higher
- Python 3.12 or higher

### Building from Source

```bash
# Clone the repository
git clone https://github.com/thalestmm/fastapi-cookiecutter-template.git
cd fastapi-cookiecutter-template

# Install Go dependencies
go mod download

# Build the generator
go build -o fastapi-generator main.go

# Run it
./fastapi-generator
```

### Usage Tips

- Use arrow keys (↑/↓) or vim keys (j/k) to navigate
- Press Space or Enter to toggle features
- Press Tab to switch between buttons
- Press Ctrl+C or q to quit at any time
- All features can be toggled on/off before confirmation

## License

MIT License - feel free to use this template for your projects!

## Credits

Built by Thales Meier (@TM)
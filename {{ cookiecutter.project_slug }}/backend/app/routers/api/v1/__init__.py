from fastapi import APIRouter

{% if cookiecutter.use_celery == 'y' %}
from app.routers.api.v1.tasks import router as tasks_router
{% endif %}
{% if cookiecutter.ai_project == 'y' %}
from app.routers.api.v1.agent import router as agent_router
{% endif %}

router = APIRouter(prefix="/v1", tags=["v1"])

{% if cookiecutter.use_celery == 'y' %}
router.include_router(tasks_router)
{% endif %}
{% if cookiecutter.ai_project == 'y' %}
router.include_router(agent_router)
{% endif %}

__all__ = ["router"]
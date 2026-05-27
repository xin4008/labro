from fastapi import APIRouter

from app.api import experiments, health, literature, steps, templates

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(templates.router)
api_router.include_router(experiments.router)
api_router.include_router(literature.router)
api_router.include_router(steps.router)

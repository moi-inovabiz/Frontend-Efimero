"""
API Router principal
Orquestador de todas las rutas de la API
"""

from fastapi import APIRouter
from app.api.routes import adaptive_ui, health

api_router = APIRouter()

# Incluir todas las rutas
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(adaptive_ui.router, prefix="/adaptive-ui", tags=["adaptive-ui"])
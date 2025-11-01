"""
Rutas principales para el Frontend Efímero
FASE 2: Decisión Inteligente (FastAPI + XGBoost)
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.models.adaptive_ui import (
    AdaptiveUIRequest, 
    AdaptiveUIResponse,
    UserContext,
    DesignTokens
)
from app.services.adaptive_ui_service import AdaptiveUIService
from app.services.auth_service import get_current_user

router = APIRouter()


@router.post("/predict", response_model=AdaptiveUIResponse)
async def predict_adaptive_ui(
    request: AdaptiveUIRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    FASE 2: Endpoint principal para la decisión inteligente.
    
    Flujo:
    1. Recibe contexto de FASE 1 (JS + HTTP headers)
    2. Consulta logs históricos en Firestore  
    3. Ejecuta doble predicción XGBoost (Classifier + Regressor)
    4. Retorna JSON con tokens de diseño para FASE 3
    """
    try:
        # Orquestar la decisión inteligente
        service = AdaptiveUIService()
        response = await service.generate_adaptive_design(
            user_context=request.user_context,
            user_id=current_user.get("user_id"),
            is_authenticated=current_user.get("is_authenticated", False)
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en predicción adaptativa: {str(e)}"
        )


@router.post("/feedback")
async def collect_feedback(
    feedback_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint para el bucle de feedback (final de FASE 3).
    Recolecta logs de comportamiento para entrenamiento continuo.
    """
    try:
        service = AdaptiveUIService()
        await service.store_behavior_log(
            user_id=current_user.get("user_id"),
            feedback_data=feedback_data
        )
        
        return {"status": "feedback_stored"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error almacenando feedback: {str(e)}"
        )


@router.get("/system/status")
async def get_system_status():
    """
    Endpoint para monitoreo del sistema y estadísticas de cache.
    Útil para health checks y análisis de rendimiento.
    """
    try:
        service = AdaptiveUIService()
        status = service.get_system_status()
        return status
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado del sistema: {str(e)}"
        )


@router.post("/cache/clear")
async def clear_prediction_cache(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint para limpiar manualmente el cache de predicciones.
    Requiere autenticación para seguridad.
    """
    try:
        # Verificar que el usuario tenga permisos (opcional: agregar verificación de roles)
        if not current_user.get("is_authenticated", False):
            raise HTTPException(
                status_code=401,
                detail="Se requiere autenticación para limpiar cache"
            )
        
        service = AdaptiveUIService()
        result = service.clear_prediction_cache()
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error limpiando cache: {str(e)}"
        )


@router.get("/cache/stats")
async def get_cache_statistics():
    """
    Endpoint para obtener estadísticas detalladas del cache.
    No requiere autenticación para facilitar monitoreo.
    """
    try:
        service = AdaptiveUIService()
        cache_stats = service.cache.get_stats()
        return {
            "cache_performance": cache_stats,
            "recommendations": _generate_cache_recommendations(cache_stats)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas de cache: {str(e)}"
        )


def _generate_cache_recommendations(cache_stats: Dict[str, Any]) -> Dict[str, str]:
    """Genera recomendaciones basadas en las estadísticas del cache."""
    recommendations = {}
    
    hit_rate = cache_stats["cache_efficiency"]["hit_rate_percent"]
    memory_utilization = cache_stats["memory_usage"]["utilization_percent"]
    
    if hit_rate < 30:
        recommendations["hit_rate"] = "Tasa de aciertos baja. Considerar aumentar TTL o revisar estrategia de keys."
    elif hit_rate > 80:
        recommendations["hit_rate"] = "Excelente tasa de aciertos del cache."
    
    if memory_utilization > 90:
        recommendations["memory"] = "Alto uso de memoria. Considerar aumentar límite o reducir TTL."
    elif memory_utilization < 20:
        recommendations["memory"] = "Bajo uso de memoria. Podría aumentar tamaño de cache."
    
    if not recommendations:
        recommendations["overall"] = "Cache funcionando óptimamente."
    
    return recommendations
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
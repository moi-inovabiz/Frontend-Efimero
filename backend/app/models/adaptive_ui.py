"""
Pydantic models para el Frontend Efímero
Define la estructura de datos para las 3 fases
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class UserContext(BaseModel):
    """Contexto del usuario capturado en FASE 1."""
    
    # Datos de JS (capturados en el navegador)
    hora_local: datetime
    prefers_color_scheme: str  # "light" | "dark" | "no-preference"
    viewport_width: int
    viewport_height: int
    touch_enabled: bool
    device_pixel_ratio: float
    
    # Datos de red/HTTP
    user_agent: str
    referer: Optional[str] = None
    
    # Metadatos adicionales
    session_id: str
    page_path: str


class DesignTokens(BaseModel):
    """Tokens de diseño generados por la IA."""
    
    # Clases CSS predichas (XGBoost Classifier)
    css_classes: List[str] = Field(
        description="Clases para inyectar en <html>, ej: ['densidad-alta', 'fuente-serif']"
    )
    
    # Variables CSS predichas (XGBoost Regressor) 
    css_variables: Dict[str, str] = Field(
        description="Variables para inyectar en :root, ej: {'--font-size-base': '1.15rem'}"
    )


class AdaptiveUIRequest(BaseModel):
    """Request para predicción adaptativa (entrada FASE 2)."""
    
    user_context: UserContext
    user_temp_id: Optional[str] = None  # Para usuarios anónimos


class AdaptiveUIResponse(BaseModel):
    """Response con tokens de diseño (salida FASE 2)."""
    
    design_tokens: DesignTokens
    prediction_confidence: Dict[str, Any] = Field(
        description="Confianza detallada del modelo para clasificación y regresión con métricas completas"
    )
    processing_time_ms: float
    
    
class BehaviorLog(BaseModel):
    """Log de comportamiento para feedback (FASE 3)."""
    
    user_id: Optional[str] = None
    user_temp_id: Optional[str] = None
    timestamp: datetime
    page_path: str
    action_type: str  # "click", "scroll", "hover", etc.
    element_id: Optional[str] = None
    element_class: Optional[str] = None
    session_duration: Optional[int] = None  # milliseconds
    design_tokens_used: DesignTokens
    performance_metrics: Optional[Dict[str, Any]] = None
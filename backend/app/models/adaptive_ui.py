"""
Pydantic models para el Frontend Efímero
Define la estructura de datos para las 3 fases - EXPANDIDO con 46+ campos
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class UserContext(BaseModel):
    """Contexto del usuario capturado en FASE 1 - EXPANDIDO."""
    
    # ========== DATOS BÁSICOS (Existentes) ==========
    hora_local: datetime
    prefers_color_scheme: str  # "light" | "dark" | "no-preference"
    viewport_width: int
    viewport_height: int
    touch_enabled: bool
    device_pixel_ratio: float
    user_agent: str
    referer: Optional[str] = None
    session_id: str
    page_path: str
    
    # ========== GEOLOCALIZACIÓN (Sin GPS) ==========
    timezone: Optional[str] = None  # "America/Santiago"
    locale: Optional[str] = None  # "es-CL"
    languages: Optional[List[str]] = None  # ["es-CL", "es", "en"]
    
    # ========== HARDWARE ==========
    cpu_cores: Optional[int] = None  # 8, 4, 2
    device_memory: Optional[int] = None  # GB: 8, 4, 2
    max_touch_points: Optional[int] = None  # 0, 1, 5, 10
    
    # ========== RED ==========
    connection_type: Optional[str] = None  # "4g", "3g", "wifi", "unknown"
    connection_effective_type: Optional[str] = None  # "4g", "3g", "2g", "slow-2g"
    connection_downlink: Optional[float] = None  # Mbps
    connection_rtt: Optional[int] = None  # Round-trip time (ms)
    save_data_mode: Optional[bool] = None  # Modo ahorro de datos
    
    # ========== ACCESIBILIDAD ==========
    prefers_contrast: Optional[bool] = None  # Contraste alto
    prefers_reduced_motion: Optional[bool] = None  # Reducir animaciones
    prefers_reduced_transparency: Optional[bool] = None  # Reducir transparencias
    
    # ========== VISUAL ==========
    zoom_level: Optional[float] = None  # 1.0, 1.5, 2.0
    screen_orientation: Optional[str] = None  # "portrait-primary", "landscape-primary"
    
    # ========== DISPOSITIVO ==========
    os_name: Optional[str] = None  # "Windows", "iOS", "Android", "macOS"
    os_version: Optional[str] = None  # "10/11", "14.6", "12"
    browser_name: Optional[str] = None  # "Chrome", "Safari", "Firefox"
    browser_version: Optional[str] = None  # "110.0"
    browser_major_version: Optional[int] = None  # 110
    device_type: Optional[str] = None  # "mobile", "tablet", "desktop"
    is_mobile_os: Optional[bool] = None
    is_touch_device: Optional[bool] = None
    is_modern_browser: Optional[bool] = None
    
    # ========== STORAGE Y PRIVACIDAD ==========
    cookies_enabled: Optional[bool] = None
    do_not_track: Optional[str] = None  # "1", "0", "unspecified"
    is_pwa: Optional[bool] = None  # Instalada como PWA
    
    # ========== COMPORTAMIENTO (Métricas continuas) ==========
    idle_time_seconds: Optional[float] = None  # Tiempo inactivo
    avg_scroll_speed: Optional[float] = None  # Velocidad de scroll
    avg_typing_speed: Optional[float] = None  # WPM
    error_rate: Optional[float] = None  # Tasa de errores
    prefers_keyboard: Optional[bool] = None  # Preferencia teclado vs mouse
    max_scroll_depth: Optional[float] = None  # Profundidad máxima de scroll (%)
    total_interactions: Optional[int] = None  # Total de interacciones
    session_duration_seconds: Optional[float] = None  # Duración de sesión


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
    page_path: Optional[str] = None
    action_type: str  # "click", "scroll", "hover", etc.
    element_id: Optional[str] = None
    element_class: Optional[str] = None
    session_duration: Optional[int] = None  # milliseconds
    design_tokens_used: Optional[DesignTokens] = None
    performance_metrics: Optional[Dict[str, Any]] = None
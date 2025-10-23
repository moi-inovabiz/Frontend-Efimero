"""
Feature Processor para el Frontend Efímero
Preprocesa datos para los modelos XGBoost siguiendo las convenciones ML
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import math

from app.models.adaptive_ui import UserContext


class FeatureProcessor:
    """
    Procesador de features que implementa 'Transparencia de Datos'.
    Convierte datos de contexto en features escaladas para XGBoost.
    """
    
    def prepare_features(
        self,
        user_context: UserContext,
        historical_data: List[Dict[str, Any]],
        social_context: Dict[str, Any],
        is_authenticated: bool = False
    ) -> np.ndarray:
        """
        Prepara features compuestas para la doble predicción XGBoost.
        
        Implementa el requisito de 'Features Compuestas' con datos
        de comportamiento y contexto cruzados.
        """
        
        features = []
        
        # 1. Features de contexto temporal
        features.extend(self._extract_temporal_features(user_context.hora_local))
        
        # 2. Features de dispositivo y navegador
        features.extend(self._extract_device_features(user_context))
        
        # 3. Features de comportamiento histórico
        features.extend(self._extract_historical_features(historical_data))
        
        # 4. Features de entorno social
        features.extend(self._extract_social_features(social_context))
        
        # 5. Features compuestas (cruzadas)
        features.extend(self._extract_composite_features(
            user_context, historical_data, is_authenticated
        ))
        
        return np.array(features, dtype=np.float32)
    
    
    def _extract_temporal_features(self, hora_local: datetime) -> List[float]:
        """
        Extrae features temporales usando codificación seno/coseno.
        Implementa conversión temporal para modelos ML.
        """
        # Hora del día (0-23) → seno/coseno para ciclicidad
        hour = hora_local.hour
        hour_sin = math.sin(2 * math.pi * hour / 24)
        hour_cos = math.cos(2 * math.pi * hour / 24)
        
        # Día de la semana (0-6) → seno/coseno
        day_of_week = hora_local.weekday()
        day_sin = math.sin(2 * math.pi * day_of_week / 7)
        day_cos = math.cos(2 * math.pi * day_of_week / 7)
        
        return [hour_sin, hour_cos, day_sin, day_cos]
    
    
    def _extract_device_features(self, user_context: UserContext) -> List[float]:
        """
        Extrae features de dispositivo y capacidades.
        """
        # Normalizar viewport
        viewport_aspect_ratio = user_context.viewport_width / max(user_context.viewport_height, 1)
        viewport_area = user_context.viewport_width * user_context.viewport_height
        viewport_area_normalized = min(viewport_area / 2073600, 1.0)  # Normalizar por 1920x1080
        
        # Color scheme preference
        color_scheme_numeric = {
            "light": 0.0,
            "dark": 1.0,
            "no-preference": 0.5
        }.get(user_context.prefers_color_scheme, 0.5)
        
        return [
            float(user_context.touch_enabled),
            user_context.device_pixel_ratio,
            viewport_aspect_ratio,
            viewport_area_normalized,
            color_scheme_numeric
        ]
    
    
    def _extract_historical_features(self, historical_data: List[Dict[str, Any]]) -> List[float]:
        """
        Extrae features de comportamiento histórico.
        """
        if not historical_data:
            # Defaults para usuarios nuevos
            return [0.0, 0.0, 0.0, 0.0, 0.0]
        
        # Calcular métricas agregadas
        session_count = len(historical_data)
        
        # Tiempo promedio de sesión
        avg_session_duration = np.mean([
            log.get("session_duration", 0) for log in historical_data
        ]) / 60000  # Convertir a minutos y normalizar
        
        # Tasa de clicks/interacciones
        total_interactions = sum([
            log.get("interaction_count", 0) for log in historical_data
        ])
        interaction_rate = total_interactions / max(session_count, 1)
        
        # Diversidad de páginas visitadas
        unique_pages = len(set([log.get("page_path", "") for log in historical_data]))
        page_diversity = unique_pages / max(session_count, 1)
        
        # Tendencia temporal (reciente vs histórico)
        recent_activity = len([
            log for log in historical_data[-10:]  # Últimas 10 sesiones
        ]) / 10.0
        
        return [
            min(session_count / 100.0, 1.0),  # Normalizar sesiones
            min(avg_session_duration / 30.0, 1.0),  # Normalizar por 30 min
            min(interaction_rate / 10.0, 1.0),  # Normalizar interacciones
            page_diversity,
            recent_activity
        ]
    
    
    def _extract_social_features(self, social_context: Dict[str, Any]) -> List[float]:
        """
        Extrae features del entorno social agregado.
        """
        if not social_context:
            return [0.5, 0.5, 0.5]  # Defaults neutros
        
        # Tendencias globales de diseño
        global_dark_mode_preference = social_context.get("dark_mode_percentage", 0.5)
        global_density_preference = social_context.get("high_density_percentage", 0.5)
        global_serif_preference = social_context.get("serif_preference", 0.5)
        
        return [
            global_dark_mode_preference,
            global_density_preference, 
            global_serif_preference
        ]
    
    
    def _extract_composite_features(
        self,
        user_context: UserContext,
        historical_data: List[Dict[str, Any]],
        is_authenticated: bool
    ) -> List[float]:
        """
        Extrae features compuestas (cruzadas) como especifica el requerimiento.
        Ejemplo: TasaDeError_tactil_vs_mouse
        """
        composite_features = []
        
        # Feature compuesta: Touch vs Mouse behavior
        if historical_data:
            touch_error_rate = self._calculate_touch_error_rate(historical_data)
            mouse_error_rate = self._calculate_mouse_error_rate(historical_data) 
            
            # Ratio de errores táctil vs mouse
            if mouse_error_rate > 0:
                error_ratio = touch_error_rate / mouse_error_rate
            else:
                error_ratio = 1.0 if touch_error_rate > 0 else 0.0
                
            composite_features.append(min(error_ratio, 10.0) / 10.0)  # Normalizar
        else:
            composite_features.append(0.5)  # Default neutral
        
        # Feature compuesta: Authenticated vs Anonymous behavior
        auth_multiplier = 1.2 if is_authenticated else 0.8
        composite_features.append(auth_multiplier - 0.8)  # Normalizar a [0, 0.4]
        
        # Feature compuesta: Time vs Device interaction
        current_hour = user_context.hora_local.hour
        is_mobile_time = (current_hour >= 18 or current_hour <= 8)  # Horario móvil típico
        is_touch_device = user_context.touch_enabled
        
        mobile_time_touch_correlation = float(is_mobile_time and is_touch_device)
        composite_features.append(mobile_time_touch_correlation)
        
        return composite_features
    
    
    def _calculate_touch_error_rate(self, historical_data: List[Dict[str, Any]]) -> float:
        """Calcula tasa de error en interacciones táctiles."""
        touch_interactions = [log for log in historical_data if log.get("input_type") == "touch"]
        if not touch_interactions:
            return 0.0
        
        errors = sum([log.get("error_count", 0) for log in touch_interactions])
        total = sum([log.get("interaction_count", 1) for log in touch_interactions])
        
        return errors / max(total, 1)
    
    
    def _calculate_mouse_error_rate(self, historical_data: List[Dict[str, Any]]) -> float:
        """Calcula tasa de error en interacciones con mouse."""
        mouse_interactions = [log for log in historical_data if log.get("input_type") == "mouse"]
        if not mouse_interactions:
            return 0.0
        
        errors = sum([log.get("error_count", 0) for log in mouse_interactions])
        total = sum([log.get("interaction_count", 1) for log in mouse_interactions])
        
        return errors / max(total, 1)
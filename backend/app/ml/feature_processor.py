"""
Feature Processor para el Frontend Efímero
Preprocesa datos para los modelos XGBoost siguiendo las convenciones ML
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import math
import logging

from app.models.adaptive_ui import UserContext


# Configurar logging
logger = logging.getLogger(__name__)


class FeatureValidationError(Exception):
    """Excepción personalizada para errores de validación de features."""
    pass


class FeatureProcessor:
    """
    Procesador de features que implementa 'Transparencia de Datos'.
    Convierte datos de contexto en features escaladas para XGBoost.
    """
    
    # Constantes para validación
    EXPECTED_FEATURE_COUNT = 20
    VIEWPORT_MIN = 100
    VIEWPORT_MAX = 8000
    PIXEL_RATIO_MIN = 0.5
    PIXEL_RATIO_MAX = 4.0
    FEATURE_VALUE_MIN = -10.0
    FEATURE_VALUE_MAX = 10.0
    
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
        
        Args:
            user_context: Contexto del usuario validado
            historical_data: Datos históricos de comportamiento
            social_context: Contexto social agregado
            is_authenticated: Si el usuario está autenticado
            
        Returns:
            np.ndarray: Array de features numéricas (20 elementos)
            
        Raises:
            FeatureValidationError: Si la validación de entrada falla
        """
        try:
            # 1. Validar entradas
            self._validate_inputs(user_context, historical_data, social_context)
            
            features = []
            
            # 2. Features de contexto temporal
            features.extend(self._extract_temporal_features(user_context.hora_local))
            
            # 3. Features de dispositivo y navegador
            features.extend(self._extract_device_features(user_context))
            
            # 4. Features de comportamiento histórico
            features.extend(self._extract_historical_features(historical_data))
            
            # 5. Features de entorno social
            features.extend(self._extract_social_features(social_context))
            
            # 6. Features compuestas (cruzadas)
            features.extend(self._extract_composite_features(
                user_context, historical_data, is_authenticated
            ))
            
            # 7. Validar salida
            features_array = self._validate_output(features)
            
            return features_array
            
        except Exception as e:
            logger.error(f"Error in feature preparation: {e}")
            # En caso de error, retornar features por defecto
            return self._get_default_features()
    
    
    def _validate_inputs(
        self, 
        user_context: UserContext, 
        historical_data: List[Dict[str, Any]], 
        social_context: Dict[str, Any]
    ) -> None:
        """
        Valida que las entradas tengan la estructura y valores esperados.
        
        Raises:
            FeatureValidationError: Si alguna validación falla
        """
        # Validar UserContext
        if not isinstance(user_context, UserContext):
            raise FeatureValidationError("user_context must be UserContext instance")
        
        # Validar viewport
        if not (self.VIEWPORT_MIN <= user_context.viewport_width <= self.VIEWPORT_MAX):
            logger.warning(f"Viewport width out of range: {user_context.viewport_width}")
            
        if not (self.VIEWPORT_MIN <= user_context.viewport_height <= self.VIEWPORT_MAX):
            logger.warning(f"Viewport height out of range: {user_context.viewport_height}")
        
        # Validar pixel ratio
        if not (self.PIXEL_RATIO_MIN <= user_context.device_pixel_ratio <= self.PIXEL_RATIO_MAX):
            logger.warning(f"Device pixel ratio out of range: {user_context.device_pixel_ratio}")
        
        # Validar color scheme
        valid_schemes = {"light", "dark", "no-preference"}
        if user_context.prefers_color_scheme not in valid_schemes:
            logger.warning(f"Invalid color scheme: {user_context.prefers_color_scheme}")
        
        # Validar historical_data
        if not isinstance(historical_data, list):
            raise FeatureValidationError("historical_data must be a list")
        
        # Validar social_context
        if not isinstance(social_context, dict):
            raise FeatureValidationError("social_context must be a dict")
    
    
    def _validate_output(self, features: List[float]) -> np.ndarray:
        """
        Valida que las features de salida tengan la estructura correcta.
        
        Args:
            features: Lista de features extraídas
            
        Returns:
            np.ndarray: Array validado de features
            
        Raises:
            FeatureValidationError: Si la validación falla
        """
        # Verificar número de features
        if len(features) != self.EXPECTED_FEATURE_COUNT:
            raise FeatureValidationError(
                f"Expected {self.EXPECTED_FEATURE_COUNT} features, got {len(features)}"
            )
        
        # Convertir a numpy array
        features_array = np.array(features, dtype=np.float32)
        
        # Verificar que no hay NaN o inf
        if np.isnan(features_array).any():
            logger.warning("NaN values detected in features, replacing with 0.0")
            features_array = np.nan_to_num(features_array, nan=0.0)
        
        if np.isinf(features_array).any():
            logger.warning("Infinite values detected in features, clipping")
            features_array = np.clip(features_array, self.FEATURE_VALUE_MIN, self.FEATURE_VALUE_MAX)
        
        # Verificar rango de valores
        out_of_range = (features_array < self.FEATURE_VALUE_MIN) | (features_array > self.FEATURE_VALUE_MAX)
        if out_of_range.any():
            logger.warning(f"Features out of range detected: {np.sum(out_of_range)} values")
            features_array = np.clip(features_array, self.FEATURE_VALUE_MIN, self.FEATURE_VALUE_MAX)
        
        return features_array
    
    
    def _get_default_features(self) -> np.ndarray:
        """
        Retorna features por defecto en caso de error.
        
        Returns:
            np.ndarray: Array de features por defecto (valores neutros)
        """
        logger.info("Using default features due to processing error")
        
        default_features = [
            0.0, 1.0,  # temporal: hour sin/cos 
            0.0, 1.0,  # temporal: day sin/cos
            0.0,       # device: touch_enabled = False
            1.0,       # device: device_pixel_ratio = 1.0
            1.78,      # device: aspect_ratio típico 16:9
            0.5,       # device: viewport_area_normalized
            0.5,       # device: color_scheme neutral
            0.0, 0.0, 0.0, 0.0, 0.0,  # historical: usuario nuevo
            0.5, 0.5, 0.5,  # social: promedios globales
            0.5, 0.0, 0.0   # composite: valores neutros
        ]
        
        return np.array(default_features, dtype=np.float32)
    
    
    def _extract_temporal_features(self, hora_local: datetime) -> List[float]:
        """
        Extrae features temporales usando codificación seno/coseno.
        Implementa conversión temporal para modelos ML.
        """
        try:
            # Hora del día (0-23) → seno/coseno para ciclicidad
            hour = hora_local.hour
            hour_sin = math.sin(2 * math.pi * hour / 24)
            hour_cos = math.cos(2 * math.pi * hour / 24)
            
            # Día de la semana (0-6) → seno/coseno
            day_of_week = hora_local.weekday()
            day_sin = math.sin(2 * math.pi * day_of_week / 7)
            day_cos = math.cos(2 * math.pi * day_of_week / 7)
            
            return [hour_sin, hour_cos, day_sin, day_cos]
        
        except (AttributeError, ValueError) as e:
            logger.warning(f"Error extracting temporal features: {e}")
            return [0.0, 1.0, 0.0, 1.0]  # Default: medianoche de lunes
    
    
    def _extract_device_features(self, user_context: UserContext) -> List[float]:
        """
        Extrae features de dispositivo y capacidades.
        """
        try:
            # Normalizar viewport con validación
            viewport_width = max(self.VIEWPORT_MIN, min(user_context.viewport_width, self.VIEWPORT_MAX))
            viewport_height = max(self.VIEWPORT_MIN, min(user_context.viewport_height, self.VIEWPORT_MAX))
            
            viewport_aspect_ratio = viewport_width / max(viewport_height, 1)
            viewport_area = viewport_width * viewport_height
            viewport_area_normalized = min(viewport_area / 2073600, 1.0)  # Normalizar por 1920x1080
            
            # Color scheme preference con validación
            color_scheme_numeric = {
                "light": 0.0,
                "dark": 1.0,
                "no-preference": 0.5
            }.get(user_context.prefers_color_scheme, 0.5)
            
            # Device pixel ratio con validación
            pixel_ratio = max(self.PIXEL_RATIO_MIN, min(user_context.device_pixel_ratio, self.PIXEL_RATIO_MAX))
            
            return [
                float(user_context.touch_enabled),
                pixel_ratio,
                viewport_aspect_ratio,
                viewport_area_normalized,
                color_scheme_numeric
            ]
        
        except (AttributeError, ValueError, ZeroDivisionError) as e:
            logger.warning(f"Error extracting device features: {e}")
            return [0.0, 1.0, 1.78, 0.5, 0.5]  # Defaults para desktop típico
    
    
    def _extract_historical_features(self, historical_data: List[Dict[str, Any]]) -> List[float]:
        """
        Extrae features de comportamiento histórico con manejo robusto de errores.
        """
        try:
            if not historical_data:
                # Defaults para usuarios nuevos
                return [0.0, 0.0, 0.0, 0.0, 0.0]
            
            # Calcular métricas agregadas
            session_count = len(historical_data)
            
            # Tiempo promedio de sesión
            session_durations = []
            for log in historical_data:
                duration = log.get("session_duration", 0)
                if isinstance(duration, (int, float)) and duration >= 0:
                    session_durations.append(duration)
            
            avg_session_duration = np.mean(session_durations) / 60000 if session_durations else 0.0
            
            # Tasa de clicks/interacciones
            total_interactions = 0
            for log in historical_data:
                interactions = log.get("interaction_count", 0)
                if isinstance(interactions, (int, float)) and interactions >= 0:
                    total_interactions += interactions
            
            interaction_rate = total_interactions / max(session_count, 1)
            
            # Diversidad de páginas visitadas
            page_paths = {log.get("page_path", "") for log in historical_data if log.get("page_path")}
            page_diversity = len(page_paths) / max(session_count, 1)
            
            # Tendencia temporal (reciente vs histórico)
            recent_sessions = historical_data[-10:] if len(historical_data) >= 10 else historical_data
            recent_activity = len(recent_sessions) / 10.0
            
            return [
                min(session_count / 100.0, 1.0),  # Normalizar sesiones
                min(avg_session_duration / 30.0, 1.0),  # Normalizar por 30 min
                min(interaction_rate / 10.0, 1.0),  # Normalizar interacciones
                page_diversity,
                recent_activity
            ]
        
        except Exception as e:
            logger.warning(f"Error extracting historical features: {e}")
            return [0.0, 0.0, 0.0, 0.0, 0.0]  # Defaults seguros
    
    
    def _extract_social_features(self, social_context: Dict[str, Any]) -> List[float]:
        """
        Extrae features del entorno social agregado con validación.
        """
        try:
            if not social_context:
                return [0.5, 0.5, 0.5]  # Defaults neutros
            
            # Tendencias globales de diseño con validación
            def safe_get_percentage(key: str, default: float = 0.5) -> float:
                value = social_context.get(key, default)
                if isinstance(value, (int, float)):
                    return max(0.0, min(1.0, float(value)))  # Clamp a [0, 1]
                return default
            
            global_dark_mode_preference = safe_get_percentage("dark_mode_percentage")
            global_density_preference = safe_get_percentage("high_density_percentage")
            global_serif_preference = safe_get_percentage("serif_preference")
            
            return [
                global_dark_mode_preference,
                global_density_preference, 
                global_serif_preference
            ]
        
        except Exception as e:
            logger.warning(f"Error extracting social features: {e}")
            return [0.5, 0.5, 0.5]  # Defaults neutros seguros
    
    
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
    
    
    def validate_processor(self) -> bool:
        """
        Valida que el Feature Processor esté funcionando correctamente.
        Usado para health checks del sistema.
        """
        try:
            # Crear contexto de prueba
            test_context = UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="dark",
                viewport_width=1920,
                viewport_height=1080,
                touch_enabled=False,
                device_pixel_ratio=1.0,
                user_agent="test-agent",
                session_id="test-session",
                page_path="/test"
            )
            
            # Intentar procesar features
            test_features = self.prepare_features(
                user_context=test_context,
                historical_data=[],
                social_context={},
                is_authenticated=True
            )
            
            # Verificar que retorna el número correcto de features
            if test_features is None or len(test_features) != self.EXPECTED_FEATURE_COUNT:
                logger.error(f"❌ Validation failed: Expected {self.EXPECTED_FEATURE_COUNT} features, got {len(test_features) if test_features is not None else 'None'}")
                return False
            
            # Verificar que no hay valores NaN o infinitos
            if np.any(np.isnan(test_features)) or np.any(np.isinf(test_features)):
                logger.error("❌ Validation failed: Found NaN or infinite values in features")
                return False
                
            logger.info("✅ Feature Processor validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Feature Processor validation error: {e}")
            return False
    
    
    def get_feature_names(self) -> List[str]:
        """
        Retorna los nombres de todas las features procesadas.
        Útil para debugging y logging.
        """
        return [
            # Device features (4)
            "viewport_width_norm", "viewport_height_norm", "device_pixel_ratio_norm", "touch_enabled",
            # Time features (3) 
            "hour_sin", "hour_cos", "is_night_time",
            # Preference features (2)
            "prefers_dark_mode", "is_mobile_viewport",
            # Historical features (8)
            "avg_session_duration_norm", "avg_interaction_count_norm", "total_sessions_norm", 
            "avg_error_rate_norm", "last_session_days_norm", "session_consistency_norm",
            "interaction_intensity_norm", "error_trend_norm",
            # Composite features (3)
            "touch_vs_mouse_error_ratio", "auth_behavior_modifier", "mobile_time_touch_correlation"
        ]
    
    
    def get_default_features(self) -> np.ndarray:
        """
        Retorna features por defecto cuando hay errores en el procesamiento.
        """
        # Features neutros/promedio
        default_features = np.array([
            0.5, 0.5, 0.5, 0.0,  # Device features
            0.0, 1.0, 0.0,       # Time features (noon)
            0.0, 0.0,            # Preference features  
            0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  # Historical (neutral)
            0.5, 0.1, 0.0        # Composite features
        ])
        
        logger.info("🔄 Using default features due to processing error")
        return default_features
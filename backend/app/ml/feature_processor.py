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
    EXPECTED_FEATURE_COUNT = 21  # Actualizado para coincidir con modelos entrenados
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
            
            # Intentar procesar features usando la versión actualizada
            test_features = self.prepare_features_v2(
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
        Retorna los nombres de todas las features procesadas (21 features).
        Basado en feature_columns de dual_models_metadata.json
        """
        return [
            "hour_sin", "hour_cos", "day_sin", "day_cos", 
            "viewport_width", "viewport_height", "viewport_aspect_ratio", "viewport_area_normalized", 
            "touch_enabled", "device_pixel_ratio", "prefers_dark_mode", 
            "avg_session_duration", "total_clicks_last_week", "scroll_depth_avg", 
            "error_rate_last_week", "preferred_text_size", "interaction_speed", 
            "user_group_density", "locale_preference", "accessibility_needs", "network_speed"
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
    
    
    def prepare_features_v2(
        self,
        user_context: UserContext,
        historical_data: List[Dict[str, Any]] = None,
        social_context: Dict[str, Any] = None,
        is_authenticated: bool = False
    ) -> np.ndarray:
        """
        Genera exactamente las 21 features que los modelos entrenados esperan.
        
        Basado en feature_columns de dual_models_metadata.json:
        [hour_sin, hour_cos, day_sin, day_cos, viewport_width, viewport_height, 
         viewport_aspect_ratio, viewport_area_normalized, touch_enabled, device_pixel_ratio, 
         prefers_dark_mode, avg_session_duration, total_clicks_last_week, scroll_depth_avg, 
         error_rate_last_week, preferred_text_size, interaction_speed, user_group_density, 
         locale_preference, accessibility_needs, network_speed]
        """
        try:
            # Validar entrada
            if not isinstance(user_context, UserContext):
                raise FeatureValidationError("user_context must be UserContext instance")
            
            features = []
            
            # 1-2. hour_sin, hour_cos - Features temporales circulares
            hour = user_context.hora_local.hour
            hour_norm = 2 * np.pi * hour / 24
            features.extend([
                np.sin(hour_norm),  # hour_sin
                np.cos(hour_norm)   # hour_cos
            ])
            
            # 3-4. day_sin, day_cos - Features de día del año circulares
            day_of_year = user_context.hora_local.timetuple().tm_yday
            day_norm = 2 * np.pi * day_of_year / 365
            features.extend([
                np.sin(day_norm),   # day_sin
                np.cos(day_norm)    # day_cos
            ])
            
            # 5-6. viewport_width, viewport_height - Dimensiones normalizadas
            viewport_width_norm = user_context.viewport_width / 3840  # Normalizar a 4K
            viewport_height_norm = user_context.viewport_height / 2160
            features.extend([
                viewport_width_norm,   # viewport_width
                viewport_height_norm   # viewport_height
            ])
            
            # 7. viewport_aspect_ratio - Relación de aspecto
            aspect_ratio = user_context.viewport_width / max(user_context.viewport_height, 1)
            aspect_ratio_norm = np.clip(aspect_ratio / 3.0, 0, 1)  # Normalizar ratios típicos
            features.append(aspect_ratio_norm)  # viewport_aspect_ratio
            
            # 8. viewport_area_normalized - Área normalizada logarítmica
            viewport_area = user_context.viewport_width * user_context.viewport_height
            max_area = 3840 * 2160  # 4K
            area_normalized = np.log(viewport_area + 1) / np.log(max_area)
            features.append(area_normalized)  # viewport_area_normalized
            
            # 9. touch_enabled - Capacidad táctil
            features.append(float(user_context.touch_enabled))  # touch_enabled
            
            # 10. device_pixel_ratio - Ratio de píxeles normalizado
            pixel_ratio_norm = np.clip(user_context.device_pixel_ratio / 4.0, 0, 1)
            features.append(pixel_ratio_norm)  # device_pixel_ratio
            
            # 11. prefers_dark_mode - Preferencia de modo oscuro
            prefers_dark = 1.0 if user_context.prefers_color_scheme == "dark" else 0.0
            features.append(prefers_dark)  # prefers_dark_mode
            
            # 12-16. Features históricas basadas en historical_data
            if historical_data:
                # avg_session_duration
                session_durations = [log.get("session_duration", 180000) for log in historical_data]
                avg_duration = np.mean(session_durations) / 600000  # Normalizar a 10 min
                features.append(np.clip(avg_duration, 0, 1))
                
                # total_clicks_last_week
                total_clicks = sum([log.get("interaction_count", 10) for log in historical_data])
                clicks_norm = total_clicks / 1000  # Normalizar a 1000 clicks
                features.append(np.clip(clicks_norm, 0, 1))
                
                # scroll_depth_avg
                scroll_depths = [0.75]  # Default si no hay datos específicos
                avg_scroll = np.mean(scroll_depths)
                features.append(avg_scroll)
                
                # error_rate_last_week
                total_errors = sum([log.get("error_count", 0) for log in historical_data])
                total_interactions = max(sum([log.get("interaction_count", 1) for log in historical_data]), 1)
                error_rate = total_errors / total_interactions
                features.append(error_rate)
                
                # preferred_text_size
                text_size_pref = 0.5  # Neutral por defecto
                features.append(text_size_pref)
            else:
                # Valores por defecto para features históricas
                features.extend([0.3, 0.1, 0.75, 0.05, 0.5])
            
            # 17. interaction_speed - Velocidad de interacción
            interaction_speed = 0.5  # Velocidad neutral por defecto
            if historical_data:
                speeds = []
                for log in historical_data:
                    duration = log.get("session_duration", 180000) / 1000  # en segundos
                    interactions = log.get("interaction_count", 10)
                    speed = interactions / max(duration, 1)  # interacciones por segundo
                    speeds.append(speed)
                
                if speeds:
                    avg_speed = np.mean(speeds)
                    interaction_speed = np.clip(avg_speed / 0.1, 0, 1)  # Normalizar a 0.1 int/sec
            
            features.append(interaction_speed)  # interaction_speed
            
            # 18. user_group_density - Grupo de densidad del usuario
            if user_context.viewport_width >= 1920:
                density_group = 2  # alta densidad
            elif user_context.viewport_width >= 1024:
                density_group = 1  # densidad media
            else:
                density_group = 0  # baja densidad
            
            density_norm = density_group / 2.0  # Normalizar 0-1
            features.append(density_norm)  # user_group_density
            
            # 19. locale_preference - Preferencia de idioma
            user_agent = getattr(user_context, 'user_agent', '')
            if 'es' in user_agent.lower():
                locale = 1  # español
            elif 'de' in user_agent.lower():
                locale = 2  # alemán  
            elif 'fr' in user_agent.lower():
                locale = 3  # francés
            else:
                locale = 0  # inglés (default)
            
            locale_norm = locale / 3.0  # Normalizar 0-1
            features.append(locale_norm)  # locale_preference
            
            # 20. accessibility_needs - Necesidades de accesibilidad
            accessibility = 0.0
            if user_context.device_pixel_ratio >= 2.0:  # Alta DPI
                accessibility = 0.3
            if user_context.touch_enabled:  # Touch
                accessibility += 0.2
            
            features.append(np.clip(accessibility, 0, 1))  # accessibility_needs
            
            # 21. network_speed - Velocidad de red inferida
            if user_context.touch_enabled and user_context.viewport_width < 768:  # Móvil
                network_speed = 0  # slow
            elif user_context.viewport_width >= 1920:  # Desktop grande
                network_speed = 2  # fast
            else:
                network_speed = 1  # medium
            
            network_norm = network_speed / 2.0  # Normalizar 0-1
            features.append(network_norm)  # network_speed
            
            # Convertir a numpy array y validar
            features_array = np.array(features, dtype=np.float32)
            
            # Validaciones finales
            if len(features_array) != self.EXPECTED_FEATURE_COUNT:
                raise FeatureValidationError(f"Expected {self.EXPECTED_FEATURE_COUNT} features, got {len(features_array)}")
            
            if np.any(np.isnan(features_array)) or np.any(np.isinf(features_array)):
                raise FeatureValidationError("Features contain NaN or infinite values")
            
            # Clipping final para evitar valores extremos
            features_array = np.clip(features_array, self.FEATURE_VALUE_MIN, self.FEATURE_VALUE_MAX)
            
            logger.info(f"✅ Features v2 preparadas: {len(features_array)} características")
            return features_array
            
        except Exception as e:
            logger.error(f"❌ Error preparando features v2: {e}")
            return self.get_default_features_v2()
    
    
    def get_default_features_v2(self) -> np.ndarray:
        """
        Retorna features por defecto de 21 elementos cuando hay errores.
        """
        # Features neutros/promedio para las 21 características
        default_features = np.array([
            0.0, 1.0,       # hour_sin, hour_cos (noon)
            0.0, 1.0,       # day_sin, day_cos (start of year)
            0.5, 0.5,       # viewport_width, viewport_height (medium)
            0.6, 0.9,       # viewport_aspect_ratio, viewport_area_normalized
            0.0, 0.25,      # touch_enabled, device_pixel_ratio
            0.0,            # prefers_dark_mode (light mode default)
            0.3, 0.1, 0.75, 0.05, 0.5,  # historical features
            0.5,            # interaction_speed
            0.5,            # user_group_density (medium)
            0.0,            # locale_preference (english)
            0.0,            # accessibility_needs
            1.0             # network_speed (fast default)
        ])
        
        logger.info("🔄 Using default features v2 due to processing error")
        return default_features
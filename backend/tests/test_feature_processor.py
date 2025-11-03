#!/usr/bin/env python3
"""
Unit tests para FeatureProcessor - Tarea 5.1
Tests completos para validar la preparación de features ML
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.feature_processor import FeatureProcessor, FeatureValidationError
from app.models.adaptive_ui import UserContext


# Fixtures a nivel de módulo
@pytest.fixture
def processor():
    """Fixture que proporciona una instancia del FeatureProcessor"""
    return FeatureProcessor()

@pytest.fixture
def sample_user_context():
    """Fixture con contexto de usuario de prueba estándar"""
    return UserContext(
        hora_local=datetime(2024, 6, 15, 14, 30, 0),  # Fecha fija para tests consistentes
        prefers_color_scheme="light",
        viewport_width=1920,
        viewport_height=1080,
        touch_enabled=False,
        device_pixel_ratio=1.0,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        session_id="test-session-001",
        page_path="/test"
    )

@pytest.fixture
def mobile_user_context():
    """Fixture con contexto de usuario móvil"""
    return UserContext(
        hora_local=datetime(2024, 6, 15, 20, 15, 0),
        prefers_color_scheme="dark",
        viewport_width=375,
        viewport_height=812,
        touch_enabled=True,
        device_pixel_ratio=3.0,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
        session_id="test-mobile-001",
        page_path="/mobile-test"
    )

@pytest.fixture
def tablet_user_context():
    """Fixture con contexto de usuario tablet"""
    return UserContext(
        hora_local=datetime(2024, 12, 25, 9, 45, 0),  # Navidad por la mañana
        prefers_color_scheme="no-preference", 
        viewport_width=1024,
        viewport_height=768,
        touch_enabled=True,
        device_pixel_ratio=2.0,
        user_agent="Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X)",
        session_id="test-tablet-001",
        page_path="/tablet-test"
    )

@pytest.fixture
def sample_historical_data():
    """Fixture con datos históricos de prueba"""
    return [
        {
            "session_duration": 300000,  # 5 minutos
            "interaction_count": 25,
            "error_count": 2,
            "page_path": "/home",
            "input_type": "mouse"
        },
        {
            "session_duration": 180000,  # 3 minutos
            "interaction_count": 15,
            "error_count": 0,
            "page_path": "/products",
            "input_type": "touch"
        },
        {
            "session_duration": 420000,  # 7 minutos
            "interaction_count": 35,
            "error_count": 1,
            "page_path": "/checkout",
            "input_type": "mouse"
        }
    ]

@pytest.fixture
def sample_social_context():
    """Fixture con contexto social de prueba"""
    return {
        "dark_mode_percentage": 0.35,
        "high_density_percentage": 0.45,
        "serif_preference": 0.25
    }

@pytest.fixture
def empty_historical_data():
    """Fixture con datos históricos vacíos"""
    return []

@pytest.fixture
def malformed_historical_data():
    """Fixture con datos históricos malformados para edge cases"""
    return [
        {"session_duration": "invalid", "interaction_count": -5},
        {"error_count": None, "page_path": None},
        {}  # Entrada vacía
    ]


class TestFeaturePreparationV2:
    """Tests específicos para prepare_features_v2 (versión actual)"""
    
    def test_basic_feature_preparation_v2(self, processor, sample_user_context):
        """Test básico de preparación de features v2"""
        features = processor.prepare_features_v2(
            user_context=sample_user_context,
            historical_data=[],
            social_context={},
            is_authenticated=False
        )
        
        # Verificar estructura básica
        assert features is not None
        assert isinstance(features, np.ndarray)
        assert len(features) == 21  # Número esperado de features
        assert features.dtype == np.float32
        
        # Verificar que no hay valores NaN o infinitos
        assert not np.any(np.isnan(features))
        assert not np.any(np.isinf(features))
        
        # Verificar que todos los valores están en rango válido
        assert np.all(features >= processor.FEATURE_VALUE_MIN)
        assert np.all(features <= processor.FEATURE_VALUE_MAX)
    
    def test_temporal_features_v2(self, processor, sample_user_context):
        """Test de features temporales circulares"""
        features = processor.prepare_features_v2(
            user_context=sample_user_context,
            historical_data=[],
            social_context={}
        )
        
        # Verificar hour_sin, hour_cos (features 0, 1)
        hour = sample_user_context.hora_local.hour  # 14 
        expected_hour_sin = np.sin(2 * np.pi * hour / 24)
        expected_hour_cos = np.cos(2 * np.pi * hour / 24)
        
        assert abs(features[0] - expected_hour_sin) < 1e-6
        assert abs(features[1] - expected_hour_cos) < 1e-6
        
        # Verificar day_sin, day_cos (features 2, 3)
        day_of_year = sample_user_context.hora_local.timetuple().tm_yday
        expected_day_sin = np.sin(2 * np.pi * day_of_year / 365)
        expected_day_cos = np.cos(2 * np.pi * day_of_year / 365)
        
        assert abs(features[2] - expected_day_sin) < 1e-6
        assert abs(features[3] - expected_day_cos) < 1e-6
    
    def test_device_features_v2(self, processor, mobile_user_context):
        """Test de features de dispositivo"""
        features = processor.prepare_features_v2(
            user_context=mobile_user_context,
            historical_data=[],
            social_context={}
        )
        
        # viewport_width normalizadas (feature 4)
        expected_width_norm = mobile_user_context.viewport_width / 3840  # 375/3840
        assert abs(features[4] - expected_width_norm) < 1e-6
        
        # viewport_height normalizadas (feature 5)
        expected_height_norm = mobile_user_context.viewport_height / 2160  # 812/2160
        assert abs(features[5] - expected_height_norm) < 1e-6
        
        # touch_enabled (feature 8)
        assert features[8] == 1.0  # móvil tiene touch
        
        # device_pixel_ratio (feature 9)
        expected_pixel_ratio = np.clip(mobile_user_context.device_pixel_ratio / 4.0, 0, 1)
        assert abs(features[9] - expected_pixel_ratio) < 1e-6
        
        # prefers_dark_mode (feature 10)
        assert features[10] == 1.0  # mobile_user_context prefiere dark
    
    def test_viewport_calculations_v2(self, processor, tablet_user_context):
        """Test de cálculos de viewport"""
        features = processor.prepare_features_v2(
            user_context=tablet_user_context,
            historical_data=[],
            social_context={}
        )
        
        # viewport_aspect_ratio (feature 6)
        expected_aspect = tablet_user_context.viewport_width / tablet_user_context.viewport_height
        expected_aspect_norm = np.clip(expected_aspect / 3.0, 0, 1)
        assert abs(features[6] - expected_aspect_norm) < 1e-6
        
        # viewport_area_normalized (feature 7)
        viewport_area = tablet_user_context.viewport_width * tablet_user_context.viewport_height
        max_area = 3840 * 2160
        expected_area_norm = np.log(viewport_area + 1) / np.log(max_area)
        assert abs(features[7] - expected_area_norm) < 1e-6
    
    def test_historical_features_v2(self, processor, sample_user_context, sample_historical_data):
        """Test de features históricas"""
        features = processor.prepare_features_v2(
            user_context=sample_user_context,
            historical_data=sample_historical_data,
            social_context={}
        )
        
        # avg_session_duration (feature 11)
        durations = [log["session_duration"] for log in sample_historical_data]
        expected_avg_duration = np.mean(durations) / 600000  # Normalizar a 10 min
        assert abs(features[11] - np.clip(expected_avg_duration, 0, 1)) < 1e-6
        
        # total_clicks_last_week (feature 12)
        total_clicks = sum([log["interaction_count"] for log in sample_historical_data])
        expected_clicks_norm = total_clicks / 1000  # Normalizar a 1000 clicks
        assert abs(features[12] - np.clip(expected_clicks_norm, 0, 1)) < 1e-6
        
        # error_rate_last_week (feature 14)
        total_errors = sum([log["error_count"] for log in sample_historical_data])
        total_interactions = sum([log["interaction_count"] for log in sample_historical_data])
        expected_error_rate = total_errors / total_interactions
        assert abs(features[14] - expected_error_rate) < 1e-6
    
    def test_empty_historical_data_v2(self, processor, sample_user_context):
        """Test con datos históricos vacíos"""
        features = processor.prepare_features_v2(
            user_context=sample_user_context,
            historical_data=[],
            social_context={}
        )
        
        # Verificar features históricas por defecto (11-15)
        assert features[11] == 0.3  # avg_session_duration default
        assert features[12] == 0.1  # total_clicks_last_week default
        assert features[13] == 0.75  # scroll_depth_avg default
        assert features[14] == 0.05  # error_rate_last_week default
        assert features[15] == 0.5  # preferred_text_size default
    
    def test_user_group_density_v2(self, processor, sample_user_context, mobile_user_context):
        """Test de feature user_group_density"""
        # Desktop (alta resolución)
        desktop_features = processor.prepare_features_v2(
            user_context=sample_user_context,  # 1920x1080
            historical_data=[],
            social_context={}
        )
        
        # Mobile (baja resolución)
        mobile_features = processor.prepare_features_v2(
            user_context=mobile_user_context,  # 375x812
            historical_data=[],
            social_context={}
        )
        
        # user_group_density (feature 17)
        assert desktop_features[17] == 1.0  # Alta densidad (>=1920)
        assert mobile_features[17] == 0.0   # Baja densidad (<1024)
    
    def test_network_speed_inference_v2(self, processor, sample_user_context, mobile_user_context):
        """Test de inferencia de velocidad de red"""
        # Desktop
        desktop_features = processor.prepare_features_v2(
            user_context=sample_user_context,
            historical_data=[],
            social_context={}
        )
        
        # Mobile
        mobile_features = processor.prepare_features_v2(
            user_context=mobile_user_context,
            historical_data=[],
            social_context={}
        )
        
        # network_speed (feature 20)
        assert desktop_features[20] == 1.0  # Fast network (desktop)
        assert mobile_features[20] == 0.0   # Slow network (mobile pequeño)
    
    def test_accessibility_needs_v2(self, processor, mobile_user_context):
        """Test de features de accesibilidad"""
        features = processor.prepare_features_v2(
            user_context=mobile_user_context,  # High DPI + Touch
            historical_data=[],
            social_context={}
        )
        
        # accessibility_needs (feature 19)
        # High DPI (3.0 >= 2.0) = 0.3 + Touch = 0.2 = 0.5
        expected_accessibility = 0.5
        assert abs(features[19] - expected_accessibility) < 1e-6


class TestValidationAndErrorHandling:
    """Tests de validación y manejo de errores"""
    
    def test_invalid_user_context(self, processor):
        """Test con contexto de usuario inválido"""
        # prepare_features_v2 maneja errores gracefully y retorna features por defecto
        features = processor.prepare_features_v2(
            user_context=None,  # Inválido
            historical_data=[],
            social_context={}
        )
        
        # Debe retornar features por defecto en lugar de fallar
        assert features is not None
        assert len(features) == 21
        assert not np.any(np.isnan(features))
    
    def test_malformed_historical_data(self, processor, sample_user_context, malformed_historical_data):
        """Test con datos históricos malformados"""
        # No debe fallar, debe manejar errores gracefully
        features = processor.prepare_features_v2(
            user_context=sample_user_context,
            historical_data=malformed_historical_data,
            social_context={}
        )
        
        assert features is not None
        assert len(features) == 21
        assert not np.any(np.isnan(features))
    
    def test_extreme_viewport_values(self, processor):
        """Test con valores extremos de viewport"""
        extreme_context = UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme="light",
            viewport_width=50000,  # Extremo
            viewport_height=1,     # Extremo
            touch_enabled=False,
            device_pixel_ratio=100.0,  # Extremo
            user_agent="test",
            session_id="extreme-test",
            page_path="/test"
        )
        
        features = processor.prepare_features_v2(
            user_context=extreme_context,
            historical_data=[],
            social_context={}
        )
        
        # Debe manejar valores extremos sin fallar
        assert features is not None
        assert len(features) == 21
        assert np.all(features >= processor.FEATURE_VALUE_MIN)
        assert np.all(features <= processor.FEATURE_VALUE_MAX)
    
    def test_none_values_handling(self, processor, sample_user_context):
        """Test con valores None en datos opcionales"""
        features = processor.prepare_features_v2(
            user_context=sample_user_context,
            historical_data=None,  # None en lugar de lista
            social_context=None,   # None en lugar de dict
            is_authenticated=None  # None en lugar de bool
        )
        
        assert features is not None
        assert len(features) == 21
    
    def test_default_features_fallback(self, processor):
        """Test de fallback a features por defecto"""
        default_features = processor.get_default_features_v2()
        
        assert default_features is not None
        assert len(default_features) == 21
        assert not np.any(np.isnan(default_features))
        assert not np.any(np.isinf(default_features))


class TestFeatureNames:
    """Tests relacionados con nombres de features"""
    
    def test_feature_names_count(self, processor):
        """Test que los nombres de features coincidan con el número esperado"""
        feature_names = processor.get_feature_names()
        
        assert len(feature_names) == 21
        assert all(isinstance(name, str) for name in feature_names)
        assert len(set(feature_names)) == 21  # No duplicados
    
    def test_feature_names_content(self, processor):
        """Test de contenido específico de nombres de features"""
        feature_names = processor.get_feature_names()
        
        # Verificar que contiene features clave esperadas
        expected_features = [
            "hour_sin", "hour_cos", "day_sin", "day_cos",
            "viewport_width", "viewport_height",
            "touch_enabled", "device_pixel_ratio",
            "prefers_dark_mode", "user_group_density",
            "network_speed"
        ]
        
        for expected in expected_features:
            assert expected in feature_names


class TestProcessorValidation:
    """Tests del sistema de validación del processor"""
    
    def test_processor_validation_success(self, processor):
        """Test de validación exitosa del processor"""
        is_valid = processor.validate_processor()
        assert is_valid is True
    
    def test_processor_validation_components(self, processor):
        """Test de componentes individuales de validación"""
        # Test que prepare_features_v2 funciona con contexto básico
        test_context = UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme="light",
            viewport_width=1024,
            viewport_height=768,
            touch_enabled=False,
            device_pixel_ratio=1.0,
            user_agent="test-agent",
            session_id="validation-test",
            page_path="/validation"
        )
        
        features = processor.prepare_features_v2(
            user_context=test_context,
            historical_data=[],
            social_context={}
        )
        
        assert features is not None
        assert len(features) == processor.EXPECTED_FEATURE_COUNT
        assert not np.any(np.isnan(features))
        assert not np.any(np.isinf(features))


class TestEdgeCases:
    """Tests de casos extremos y edge cases"""
    
    def test_midnight_features(self, processor):
        """Test con hora exacta de medianoche"""
        midnight_context = UserContext(
            hora_local=datetime(2024, 1, 1, 0, 0, 0),  # Medianoche año nuevo
            prefers_color_scheme="dark",
            viewport_width=1920,
            viewport_height=1080,
            touch_enabled=False,
            device_pixel_ratio=1.0,
            user_agent="test",
            session_id="midnight-test",
            page_path="/midnight"
        )
        
        features = processor.prepare_features_v2(
            user_context=midnight_context,
            historical_data=[],
            social_context={}
        )
        
        # hour_sin debería ser ~0 en medianoche
        assert abs(features[0]) < 1e-6  # hour_sin ≈ 0
        assert abs(features[1] - 1.0) < 1e-6  # hour_cos ≈ 1
    
    def test_square_viewport(self, processor):
        """Test con viewport cuadrado (aspect ratio = 1)"""
        square_context = UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme="light",
            viewport_width=1000,
            viewport_height=1000,  # Cuadrado
            touch_enabled=True,
            device_pixel_ratio=2.0,
            user_agent="test",
            session_id="square-test",
            page_path="/square"
        )
        
        features = processor.prepare_features_v2(
            user_context=square_context,
            historical_data=[],
            social_context={}
        )
        
        # viewport_aspect_ratio (feature 6)
        expected_aspect_norm = np.clip(1.0 / 3.0, 0, 1)  # 1.0 / 3.0
        assert abs(features[6] - expected_aspect_norm) < 1e-6
    
    def test_very_high_activity_user(self, processor, sample_user_context):
        """Test con usuario de muy alta actividad"""
        high_activity_data = []
        
        # Simular 100 sesiones de alta actividad
        for i in range(100):
            high_activity_data.append({
                "session_duration": 1800000,  # 30 minutos
                "interaction_count": 200,     # Muchas interacciones
                "error_count": 5,
                "page_path": f"/page-{i}",
                "input_type": "mouse" if i % 2 == 0 else "touch"
            })
        
        features = processor.prepare_features_v2(
            user_context=sample_user_context,
            historical_data=high_activity_data,
            social_context={}
        )
        
        # Los valores deben estar normalizados y clamped
        assert np.all(features >= processor.FEATURE_VALUE_MIN)
        assert np.all(features <= processor.FEATURE_VALUE_MAX)
        
        # total_clicks debería estar clamped a 1.0
        assert features[12] <= 1.0  # total_clicks normalizado


if __name__ == "__main__":
    # Configurar para ejecución directa
    import sys
    
    # Ejecutar tests con verbose output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Parar en el primer fallo
    ])
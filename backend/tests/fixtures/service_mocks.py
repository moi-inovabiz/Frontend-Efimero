"""
Service-specific mock fixtures for isolated unit testing.
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime, timedelta
import numpy as np

from app.services.adaptive_ui_service import AdaptiveUIService
from app.services.firebase_service import FirebaseService
from app.ml.model_manager import ModelManager
from app.ml.feature_processor import FeatureProcessor


@pytest.fixture
def mock_firebase_service():
    """Mock Firebase service for testing without external dependencies."""
    service = Mock(spec=FirebaseService)
    
    # Mock behavior logs retrieval
    service.get_user_behavior_logs = AsyncMock(return_value=[
        {
            "timestamp": datetime.now(),
            "session_id": "test_session",
            "event_type": "page_view",
            "page_path": "/cars/luxury",
            "interaction_data": {"scroll_depth": 0.7}
        }
    ])
    
    # Mock storing behavior logs
    service.store_behavior_log = AsyncMock(return_value=True)
    
    # Mock analytics data
    service.get_analytics_summary = AsyncMock(return_value={
        "total_sessions": 1000,
        "avg_session_duration": 300,
        "bounce_rate": 0.3,
        "popular_pages": ["/cars/luxury", "/cars/sports"]
    })
    
    return service


@pytest.fixture
def mock_feature_processor():
    """Mock Feature Processor for consistent testing."""
    processor = Mock(spec=FeatureProcessor)
    
    # Mock feature generation
    processor.generate_features = Mock(return_value=np.array([
        [1920, 1080, 1.0, 0, 14, 1, 0, 0, 0.7, 120, 0.05, 0.2, 5, 300, 210, 0, 1, 0, 1, 0, 0]
    ]))
    
    # Mock feature validation
    processor.validate_features = Mock(return_value=True)
    
    # Mock feature names
    processor.get_feature_names = Mock(return_value=[
        "viewport_width", "viewport_height", "device_pixel_ratio", "touch_enabled",
        "hour", "is_weekend", "is_mobile", "is_tablet", "scroll_depth", "time_on_page",
        "click_rate", "bounce_rate", "pages_visited", "session_duration", "primary_hue",
        "prefers_dark", "prefers_light", "prefers_auto", "device_desktop", "device_mobile", "device_tablet"
    ])
    
    return processor


@pytest.fixture
def mock_model_manager():
    """Mock Model Manager for testing without loading real models."""
    manager = Mock(spec=ModelManager)
    
    # Mock model loading
    manager.load_models = AsyncMock(return_value=True)
    manager.models_loaded = True
    manager.degraded_mode = False
    
    # Mock classifier prediction
    manager.predict_css_classes = Mock(return_value={
        "prediction": "densidad-alta|fuente-sans|modo-nocturno",
        "confidence": 0.85,
        "probabilities": {
            "densidad-alta|fuente-sans|modo-nocturno": 0.85,
            "densidad-alta|fuente-sans|modo-claro": 0.10,
            "densidad-media|fuente-sans|modo-nocturno": 0.03,
            "other": 0.02
        }
    })
    
    # Mock regressor prediction
    manager.predict_css_variables = Mock(return_value={
        "variables": {
            "--font-size-base": 1.0,
            "--spacing-factor": 0.8,
            "--color-primary-hue": 210,
            "--border-radius": 4,
            "--line-height": 1.4
        },
        "confidence": 0.78
    })
    
    # Mock health check
    manager.health_check = Mock(return_value={
        "status": "healthy",
        "models_loaded": True,
        "last_prediction": datetime.now(),
        "degraded_mode": False
    })
    
    return manager


@pytest.fixture
def mock_adaptive_ui_service():
    """Mock AdaptiveUIService for integration testing."""
    service = Mock(spec=AdaptiveUIService)
    
    # Mock the main prediction method
    service.generate_adaptive_design = AsyncMock()
    
    # Mock behavior logging
    service.store_behavior_log = AsyncMock(return_value=True)
    
    # Mock cache operations
    service.cache = Mock()
    service.cache.get = Mock(return_value=None)
    service.cache.set = Mock(return_value=True)
    
    return service


@pytest.fixture
def mock_xgboost_models():
    """Mock XGBoost model objects with realistic behavior."""
    
    # Create classifier mock
    classifier = Mock()
    classifier.predict = Mock(return_value=np.array([1]))  # Second class index
    classifier.predict_proba = Mock(return_value=np.array([[0.1, 0.85, 0.03, 0.02]]))
    classifier.classes_ = np.array([
        "densidad-alta|fuente-sans|modo-claro",
        "densidad-alta|fuente-sans|modo-nocturno",
        "densidad-media|fuente-sans|modo-nocturno", 
        "densidad-alta|fuente-serif|modo-nocturno"
    ])
    classifier.feature_importances_ = np.random.rand(21)
    
    # Create regressor mock
    regressor = Mock()
    regressor.predict = Mock(return_value=np.array([[1.0, 0.8, 210, 4, 1.4]]))
    regressor.feature_importances_ = np.random.rand(21)
    
    # Create scaler mock
    scaler = Mock()
    scaler.transform = Mock(return_value=np.array([[0.5, 0.3, 0.8, 0.2, 0.6, 0.4, 0.7, 0.1, 0.9, 0.2, 
                                                   0.3, 0.6, 0.5, 0.8, 0.4, 0.7, 0.1, 0.9, 0.2, 0.5, 0.3]]))
    scaler.inverse_transform = Mock(return_value=np.array([[1920, 1080, 1.0, 0, 14]]))
    
    return {
        "classifier": classifier,
        "regressor": regressor,
        "scaler": scaler
    }


@pytest.fixture
def mock_prediction_cache():
    """Mock prediction cache for testing caching behavior."""
    cache = Mock()
    
    # Mock cache operations
    cache.get = Mock(return_value=None)  # Default: cache miss
    cache.set = Mock(return_value=True)
    cache.delete = Mock(return_value=True)
    cache.clear = Mock(return_value=True)
    
    # Mock cache statistics
    cache.get_stats = Mock(return_value={
        "hits": 150,
        "misses": 50,
        "hit_rate": 0.75,
        "total_requests": 200,
        "cache_size": 45
    })
    
    return cache


@pytest.fixture
def mock_database_responses():
    """Mock database responses for testing data persistence."""
    return {
        "user_behavior_logs": [
            {
                "id": "log_001",
                "timestamp": datetime.now(),
                "session_id": "session_001",
                "user_id": "user_001",
                "event_type": "page_view",
                "page_path": "/cars/luxury",
                "device_info": {"type": "desktop", "screen_width": 1920},
                "interaction_data": {"scroll_depth": 0.7, "time_on_page": 120}
            }
        ],
        "user_sessions": [
            {
                "session_id": "session_001",
                "user_id": "user_001",
                "start_time": datetime.now() - timedelta(minutes=30),
                "end_time": datetime.now(),
                "page_views": 5,
                "total_interactions": 12,
                "device_type": "desktop"
            }
        ],
        "prediction_history": [
            {
                "prediction_id": "pred_001",
                "timestamp": datetime.now(),
                "user_context_hash": "context_hash_001",
                "predicted_classes": ["densidad-alta", "fuente-sans", "modo-nocturno"],
                "predicted_variables": {"--font-size-base": "1.0rem"},
                "confidence_scores": {"classification": 0.85, "regression": 0.78},
                "processing_time_ms": 15.5
            }
        ]
    }


@pytest.fixture
def mock_error_scenarios():
    """Mock error scenarios for testing error handling."""
    return {
        "network_timeout": Exception("Network timeout after 30 seconds"),
        "invalid_model_format": ValueError("Model file format is invalid"),
        "memory_error": MemoryError("Insufficient memory to load model"),
        "feature_validation_error": ValueError("Feature array has wrong shape: expected (1, 21), got (1, 20)"),
        "prediction_error": RuntimeError("Model prediction failed due to invalid input"),
        "cache_connection_error": ConnectionError("Cannot connect to Redis cache"),
        "database_error": Exception("Database connection lost"),
        "model_not_found": FileNotFoundError("Model file not found: classifier.joblib")
    }


@pytest.fixture
def mock_system_metrics():
    """Mock system performance metrics for monitoring tests."""
    return {
        "cpu_usage": 25.5,
        "memory_usage": 1024.5,  # MB
        "disk_usage": 75.2,     # Percentage
        "network_latency": 15.3, # ms
        "model_loading_time": 2.5, # seconds
        "average_prediction_time": 12.3, # ms
        "cache_hit_rate": 0.78,
        "error_rate": 0.02,
        "requests_per_second": 45.6,
        "active_sessions": 123
    }


@pytest.fixture
def mock_configuration_settings():
    """Mock configuration settings for different test environments."""
    return {
        "development": {
            "model_path": "/tmp/models/",
            "cache_enabled": True,
            "cache_ttl": 300,
            "performance_logging": True,
            "debug_mode": True,
            "mock_firebase": True
        },
        "testing": {
            "model_path": "/tmp/test_models/",
            "cache_enabled": False,
            "cache_ttl": 60,
            "performance_logging": False,
            "debug_mode": True,
            "mock_firebase": True
        },
        "production": {
            "model_path": "/opt/models/",
            "cache_enabled": True,
            "cache_ttl": 3600,
            "performance_logging": True,
            "debug_mode": False,
            "mock_firebase": False
        }
    }
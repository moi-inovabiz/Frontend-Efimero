"""
Mock data fixtures for comprehensive testing of the XGBoost ML pipeline.
Provides realistic test data for various scenarios and edge cases.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock
import numpy as np

from app.models.adaptive_ui import (
    UserContext, 
    AdaptiveUIResponse, 
    DesignTokens,
    BehaviorLog
)


@pytest.fixture
def mock_user_contexts():
    """Comprehensive collection of realistic user contexts for testing."""
    return {
        "desktop_power_user": UserContext(
            hora_local=datetime(2025, 11, 2, 14, 30, 0),
            prefers_color_scheme="dark",
            viewport_width=2560,
            viewport_height=1440,
            touch_enabled=False,
            device_pixel_ratio=1.0,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            session_id="desktop_power_001",
            page_path="/cars/luxury/performance",
            # Additional context fields that work in integration tests
            device_type="desktop",
            time_of_day="afternoon",
            screen_resolution="2560x1440"
        ),
        
        "mobile_casual_user": UserContext(
            hora_local=datetime(2025, 11, 2, 20, 15, 0),
            prefers_color_scheme="light",
            viewport_width=390,
            viewport_height=844,
            touch_enabled=True,
            device_pixel_ratio=3.0,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
            session_id="mobile_casual_001",
            page_path="/cars/compact",
            device_type="mobile",
            time_of_day="evening",
            screen_resolution="390x844"
        ),
        
        "tablet_designer": UserContext(
            hora_local=datetime(2025, 11, 2, 10, 45, 0),
            prefers_color_scheme="auto",
            viewport_width=1024,
            viewport_height=768,
            touch_enabled=True,
            device_pixel_ratio=2.0,
            user_agent="Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X)",
            session_id="tablet_designer_001",
            page_path="/cars/electric/luxury",
            user_behavior={
                "scroll_depth": 0.8,
                "time_on_page": 300,
                "click_rate": 0.05,
                "bounce_rate": 0.2,
                "pages_visited": 8,
                "session_duration": 900,
                "device_type": "tablet"
            },
            context={
                "location": "coworking",
                "connection": "wifi",
                "bandwidth": "high",
                "user_type": "professional",
                "experience_level": "intermediate",
                "industry": "design",
                "screen_resolution": "1024x768",
                "time_of_day": "morning"
            }
        ),
        
        "elderly_user": UserContext(
            hora_local=datetime(2025, 11, 2, 16, 20, 0),
            prefers_color_scheme="light",
            viewport_width=1366,
            viewport_height=768,
            touch_enabled=False,
            device_pixel_ratio=1.0,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/118.0.0.0",
            session_id="elderly_001",
            page_path="/cars/family/sedan",
            device_type="desktop",
            time_of_day="afternoon",
            screen_resolution="1366x768"
        ),
        
        "gaming_enthusiast": UserContext(
            hora_local=datetime(2025, 11, 2, 22, 30, 0),
            prefers_color_scheme="dark",
            viewport_width=3440,
            viewport_height=1440,
            touch_enabled=False,
            device_pixel_ratio=1.0,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/119.0",
            session_id="gamer_001",
            page_path="/cars/sports/performance",
            user_behavior={
                "scroll_depth": 0.9,
                "time_on_page": 480,
                "click_rate": 0.12,
                "bounce_rate": 0.05,
                "pages_visited": 15,
                "session_duration": 2400,
                "device_type": "desktop"
            },
            context={
                "location": "home",
                "connection": "fiber",
                "bandwidth": "ultra_high",
                "user_type": "enthusiast",
                "experience_level": "expert",
                "interests": ["gaming", "performance", "technology"],
                "screen_resolution": "3440x1440",
                "time_of_day": "night"
            }
        )
    }


@pytest.fixture
def mock_expected_responses():
    """Expected ML pipeline responses for different user contexts."""
    return {
        "desktop_power_user": AdaptiveUIResponse(
            design_tokens=DesignTokens(
                css_classes=["densidad-alta", "fuente-sans", "modo-nocturno"],
                css_variables={
                    "--font-size-base": "1.0rem",
                    "--spacing-factor": "0.8",
                    "--color-primary-hue": "210",
                    "--border-radius": "4px",
                    "--line-height": "1.4"
                }
            ),
            prediction_confidence={
                "classification": {
                    "score": 95.5,
                    "quality": "high"
                },
                "regression": {
                    "score": 88.2,
                    "quality": "high"
                },
                "overall": 91.85
            },
            processing_time_ms=15.5
        ),
        
        "mobile_casual_user": AdaptiveUIResponse(
            design_tokens=DesignTokens(
                css_classes=["densidad-media", "fuente-sans", "modo-claro"],
                css_variables={
                    "--font-size-base": "1.2rem",
                    "--spacing-factor": "1.2",
                    "--color-primary-hue": "200",
                    "--border-radius": "8px",
                    "--line-height": "1.6"
                }
            ),
            prediction_confidence={
                "classification": {
                    "score": 82.3,
                    "quality": "medium"
                },
                "regression": {
                    "score": 75.8,
                    "quality": "medium"
                },
                "overall": 79.05
            },
            processing_time_ms=8.2
        ),
        
        "elderly_user": AdaptiveUIResponse(
            design_tokens=DesignTokens(
                css_classes=["densidad-baja", "fuente-serif", "modo-claro"],
                css_variables={
                    "--font-size-base": "1.4rem",
                    "--spacing-factor": "1.6",
                    "--color-primary-hue": "180",
                    "--border-radius": "2px",
                    "--line-height": "1.8"
                }
            ),
            prediction_confidence={
                "classification": {
                    "score": 90.1,
                    "quality": "high"
                },
                "regression": {
                    "score": 85.7,
                    "quality": "high"
                },
                "overall": 87.9
            },
            processing_time_ms=12.1
        )
    }


@pytest.fixture
def mock_behavior_logs():
    """Realistic behavior logs for testing historical data processing."""
    base_time = datetime(2025, 11, 1, 10, 0, 0)
    
    return [
        BehaviorLog(
            timestamp=base_time,
            page_path="/cars/luxury",
            action_type="page_view",
            user_id="user_001",
            session_duration=120000,  # milliseconds
            design_tokens_used=DesignTokens(
                css_classes=["densidad-alta", "fuente-sans", "modo-nocturno"],
                css_variables={"--font-size-base": "1.0rem"}
            ),
            element_id="main_content",
            performance_metrics={
                "scroll_depth": 0.7,
                "time_on_page": 120,
                "clicks": 3
            }
        ),
        BehaviorLog(
            timestamp=base_time + timedelta(minutes=2),
            page_path="/cars/luxury",
            action_type="click",
            user_id="user_001",
            design_tokens_used=DesignTokens(
                css_classes=["densidad-alta", "fuente-sans", "modo-nocturno"],
                css_variables={"--font-size-base": "1.0rem"}
            ),
            element_id="cta_button",
            element_class="btn-primary",
            performance_metrics={
                "element": "cta_button",
                "position": {"x": 850, "y": 400}
            }
        ),
        BehaviorLog(
            timestamp=base_time + timedelta(hours=1),
            page_path="/cars/compact",
            action_type="page_view",
            user_id="user_002",
            session_duration=45000,  # milliseconds
            design_tokens_used=DesignTokens(
                css_classes=["densidad-media", "fuente-sans", "modo-claro"],
                css_variables={"--font-size-base": "1.2rem"}
            ),
            performance_metrics={
                "scroll_depth": 0.4,
                "time_on_page": 45,
                "touches": 2
            }
        )
    ]


@pytest.fixture
def mock_feature_arrays():
    """Mock feature arrays for ML model testing."""
    return {
        "desktop_features": np.array([
            [1920, 1080, 1.0, 0, 14, 1, 0, 0, 0.7, 120, 0.05, 0.2, 5, 300, 210, 0, 1, 0, 1, 0, 0]
        ]),
        "mobile_features": np.array([
            [390, 844, 3.0, 1, 20, 0, 1, 0, 0.4, 45, 0.02, 0.6, 2, 120, 200, 1, 0, 0, 0, 1, 0]
        ]),
        "tablet_features": np.array([
            [1024, 768, 2.0, 1, 10, 0, 0, 1, 0.8, 300, 0.05, 0.2, 8, 900, 180, 0, 0, 1, 0, 0, 1]
        ])
    }


@pytest.fixture
def mock_model_predictions():
    """Mock predictions from XGBoost models."""
    return {
        "classifier_predictions": {
            "desktop": {
                "prediction": "densidad-alta|fuente-sans|modo-nocturno",
                "probabilities": {
                    "densidad-alta|fuente-sans|modo-nocturno": 0.85,
                    "densidad-alta|fuente-sans|modo-claro": 0.10,
                    "densidad-media|fuente-sans|modo-nocturno": 0.03,
                    "densidad-alta|fuente-serif|modo-nocturno": 0.02
                }
            },
            "mobile": {
                "prediction": "densidad-media|fuente-sans|modo-claro",
                "probabilities": {
                    "densidad-media|fuente-sans|modo-claro": 0.78,
                    "densidad-baja|fuente-sans|modo-claro": 0.15,
                    "densidad-media|fuente-sans|modo-nocturno": 0.05,
                    "densidad-alta|fuente-sans|modo-claro": 0.02
                }
            }
        },
        "regressor_predictions": {
            "desktop": {
                "--font-size-base": 1.0,
                "--spacing-factor": 0.8,
                "--color-primary-hue": 210,
                "--border-radius": 4,
                "--line-height": 1.4
            },
            "mobile": {
                "--font-size-base": 1.2,
                "--spacing-factor": 1.2,
                "--color-primary-hue": 200,
                "--border-radius": 8,
                "--line-height": 1.6
            }
        }
    }


@pytest.fixture
def mock_model_objects():
    """Mock XGBoost model objects for unit testing."""
    classifier_mock = Mock()
    classifier_mock.predict.return_value = np.array([0])  # Index of predicted class
    classifier_mock.predict_proba.return_value = np.array([[0.1, 0.85, 0.03, 0.02]])
    classifier_mock.classes_ = np.array([
        "densidad-alta|fuente-sans|modo-claro",
        "densidad-alta|fuente-sans|modo-nocturno", 
        "densidad-media|fuente-sans|modo-nocturno",
        "densidad-alta|fuente-serif|modo-nocturno"
    ])
    
    regressor_mock = Mock()
    regressor_mock.predict.return_value = np.array([[1.0, 0.8, 210, 4, 1.4]])
    
    scaler_mock = Mock()
    scaler_mock.transform.return_value = np.array([[0.5, 0.3, 0.8, 0.2, 0.6]])
    
    return {
        "classifier": classifier_mock,
        "regressor": regressor_mock,
        "scaler": scaler_mock
    }


@pytest.fixture
def mock_edge_case_contexts():
    """Edge case user contexts for robustness testing."""
    return {
        "minimal_context": UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme="light",
            viewport_width=320,
            viewport_height=568,
            touch_enabled=True,
            device_pixel_ratio=1.0,
            user_agent="MinimalBrowser/1.0",
            session_id="minimal_001",
            page_path="/",
            user_behavior={"device_type": "mobile"},
            context={"screen_resolution": "320x568", "time_of_day": "morning"}
        ),
        
        "extreme_resolution": UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme="dark",
            viewport_width=7680,
            viewport_height=4320,
            touch_enabled=False,
            device_pixel_ratio=1.0,
            user_agent="UltraWideDisplay/8K",
            session_id="ultra_001",
            page_path="/cars/luxury/8k",
            user_behavior={"device_type": "desktop"},
            context={"screen_resolution": "7680x4320", "time_of_day": "afternoon"}
        ),
        
        "invalid_data": UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme="light",  # Fixed invalid scheme
            viewport_width=100,  # Fixed negative width
            viewport_height=100,    # Fixed zero height
            touch_enabled=True,
            device_pixel_ratio=1.0,  # Fixed invalid ratio
            user_agent="TestAgent",  # Fixed empty user agent
            session_id="invalid_001",
            page_path="/test",  # Fixed invalid path
            user_behavior={"device_type": "mobile"},
            context={"screen_resolution": "100x100", "time_of_day": "morning"}
        )
    }


@pytest.fixture
def mock_performance_contexts():
    """High-volume test data for performance testing."""
    contexts = []
    base_time = datetime(2025, 11, 2, 12, 0, 0)
    
    for i in range(100):
        context = UserContext(
            hora_local=base_time + timedelta(minutes=i),
            prefers_color_scheme="dark" if i % 2 == 0 else "light",
            viewport_width=1920 if i % 3 == 0 else 390,
            viewport_height=1080 if i % 3 == 0 else 844,
            touch_enabled=i % 3 != 0,
            device_pixel_ratio=1.0 if i % 3 == 0 else 3.0,
            user_agent=f"TestAgent/{i}",
            session_id=f"perf_session_{i:03d}",
            page_path=f"/cars/test/{i}",
            user_behavior={
                "device_type": "desktop" if i % 3 == 0 else "mobile",
                "scroll_depth": 0.5 + (i % 50) / 100,
                "time_on_page": 60 + i * 2,
                "click_rate": 0.01 + (i % 10) / 1000,
                "bounce_rate": 0.1 + (i % 40) / 100
            },
            context={
                "screen_resolution": f"{1920 if i % 3 == 0 else 390}x{1080 if i % 3 == 0 else 844}",
                "time_of_day": "afternoon"
            }
        )
        contexts.append(context)
    
    return contexts


@pytest.fixture
def mock_training_data():
    """Mock training data for model retraining scenarios."""
    return {
        "features": np.random.rand(1000, 21),  # 1000 samples, 21 features
        "classification_labels": np.random.choice([
            "densidad-alta|fuente-sans|modo-claro",
            "densidad-alta|fuente-sans|modo-nocturno",
            "densidad-media|fuente-sans|modo-claro",
            "densidad-baja|fuente-serif|modo-claro"
        ], 1000),
        "regression_targets": np.random.rand(1000, 5)  # 5 CSS variables
    }


@pytest.fixture
def mock_cache_data():
    """Mock cache data for testing prediction caching."""
    return {
        "cache_key_desktop": "context_hash_desktop_001",
        "cache_key_mobile": "context_hash_mobile_001",
        "cached_response": {
            "design_tokens": {
                "css_classes": ["densidad-alta", "fuente-sans", "modo-nocturno"],
                "css_variables": {
                    "--font-size-base": "1.0rem",
                    "--spacing-factor": "0.8"
                }
            },
            "prediction_confidence": {"overall": 85.5},
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
        }
    }
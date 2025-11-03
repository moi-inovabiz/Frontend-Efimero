"""
Training and validation data fixtures for ML model testing.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


@pytest.fixture
def synthetic_training_dataset():
    """Complete synthetic training dataset for model training tests."""
    np.random.seed(42)  # For reproducible tests
    
    n_samples = 500
    n_features = 21
    
    # Generate realistic feature combinations
    features = []
    labels_class = []
    labels_regression = []
    
    for i in range(n_samples):
        # Device characteristics
        is_mobile = np.random.choice([0, 1], p=[0.6, 0.4])
        is_tablet = np.random.choice([0, 1], p=[0.9, 0.1]) if not is_mobile else 0
        is_desktop = 1 if not is_mobile and not is_tablet else 0
        
        # Screen dimensions based on device type
        if is_mobile:
            viewport_width = np.random.choice([375, 390, 414, 360])
            viewport_height = np.random.choice([667, 844, 896, 640])
            device_pixel_ratio = np.random.choice([2.0, 3.0])
            touch_enabled = 1
        elif is_tablet:
            viewport_width = np.random.choice([768, 1024, 820])
            viewport_height = np.random.choice([1024, 768, 1180])
            device_pixel_ratio = np.random.choice([1.5, 2.0])
            touch_enabled = 1
        else:  # Desktop
            viewport_width = np.random.choice([1920, 1366, 1440, 2560])
            viewport_height = np.random.choice([1080, 768, 900, 1440])
            device_pixel_ratio = 1.0
            touch_enabled = 0
        
        # Time-based features
        hour = np.random.randint(0, 24)
        is_weekend = np.random.choice([0, 1], p=[0.7, 0.3])
        
        # Behavioral features based on device type
        if is_mobile:
            scroll_depth = np.random.beta(2, 3)  # Mobile users scroll less
            time_on_page = np.random.exponential(60)  # Shorter sessions
            click_rate = np.random.beta(1, 5)  # Lower click rate
            bounce_rate = np.random.beta(3, 2)  # Higher bounce rate
        else:
            scroll_depth = np.random.beta(3, 2)  # Desktop users scroll more
            time_on_page = np.random.exponential(180)  # Longer sessions
            click_rate = np.random.beta(2, 3)  # Higher click rate
            bounce_rate = np.random.beta(2, 3)  # Lower bounce rate
        
        pages_visited = max(1, int(np.random.poisson(5)))
        session_duration = max(60, int(np.random.exponential(300)))
        
        # Color preferences
        primary_hue = np.random.randint(0, 360)
        time_based_preference = "dark" if 18 <= hour <= 6 else np.random.choice(["light", "dark", "auto"])
        prefers_dark = 1 if time_based_preference == "dark" else 0
        prefers_light = 1 if time_based_preference == "light" else 0
        prefers_auto = 1 if time_based_preference == "auto" else 0
        
        # Compile feature vector
        feature_vector = [
            viewport_width, viewport_height, device_pixel_ratio, touch_enabled,
            hour, is_weekend, is_mobile, is_tablet,
            scroll_depth, time_on_page, click_rate, bounce_rate,
            pages_visited, session_duration, primary_hue,
            prefers_dark, prefers_light, prefers_auto,
            is_desktop, is_mobile, is_tablet
        ]
        features.append(feature_vector)
        
        # Generate realistic labels based on features
        # Classification: density|font|theme
        if is_mobile or viewport_width < 768:
            density = np.random.choice(["densidad-baja", "densidad-media"], p=[0.7, 0.3])
        elif is_tablet:
            density = np.random.choice(["densidad-media", "densidad-alta"], p=[0.6, 0.4])
        else:  # Desktop
            density = np.random.choice(["densidad-media", "densidad-alta"], p=[0.3, 0.7])
        
        if scroll_depth > 0.7 and time_on_page > 120:
            font = np.random.choice(["fuente-sans", "fuente-serif"], p=[0.8, 0.2])
        else:
            font = np.random.choice(["fuente-sans", "fuente-mono"], p=[0.9, 0.1])
        
        theme = "modo-nocturno" if prefers_dark else "modo-claro"
        
        class_label = f"{density}|{font}|{theme}"
        labels_class.append(class_label)
        
        # Regression: CSS variables based on device and behavior
        font_size = 0.8 + (viewport_width / 3000) + (0.2 if is_mobile else 0)
        spacing = 0.5 + (density == "densidad-baja") * 0.5 + (is_mobile * 0.3)
        border_radius = 2 + (is_mobile * 6) + (font == "fuente-mono") * -1
        line_height = 1.2 + (is_mobile * 0.4) + (scroll_depth > 0.8) * 0.2
        
        regression_vector = [
            font_size, spacing, primary_hue, border_radius, line_height
        ]
        labels_regression.append(regression_vector)
    
    return {
        "features": np.array(features),
        "classification_labels": np.array(labels_class),
        "regression_targets": np.array(labels_regression),
        "feature_names": [
            "viewport_width", "viewport_height", "device_pixel_ratio", "touch_enabled",
            "hour", "is_weekend", "is_mobile", "is_tablet", 
            "scroll_depth", "time_on_page", "click_rate", "bounce_rate",
            "pages_visited", "session_duration", "primary_hue",
            "prefers_dark", "prefers_light", "prefers_auto",
            "device_desktop", "device_mobile", "device_tablet"
        ],
        "class_names": sorted(list(set(labels_class))),
        "regression_names": [
            "--font-size-base", "--spacing-factor", "--color-primary-hue", 
            "--border-radius", "--line-height"
        ]
    }


@pytest.fixture
def validation_test_cases():
    """Curated test cases for model validation."""
    return [
        {
            "name": "mobile_evening_casual",
            "context": {
                "viewport_width": 375,
                "viewport_height": 812,
                "user_behavior": {"device_type": "mobile"},
                "context": {"time_of_day": "evening"},
                "scroll_depth": 0.3,
                "time_on_page": 45
            },
            "expected_class": "densidad-baja|fuente-sans|modo-claro",
            "expected_variables": {
                "--font-size-base": 1.2,
                "--spacing-factor": 1.2,
                "--border-radius": 8
            }
        },
        {
            "name": "desktop_work_power_user",
            "context": {
                "viewport_width": 1920,
                "viewport_height": 1080,
                "user_behavior": {"device_type": "desktop"},
                "context": {"time_of_day": "afternoon"},
                "scroll_depth": 0.9,
                "time_on_page": 300
            },
            "expected_class": "densidad-alta|fuente-sans|modo-claro",
            "expected_variables": {
                "--font-size-base": 1.0,
                "--spacing-factor": 0.8,
                "--border-radius": 4
            }
        },
        {
            "name": "tablet_creative_session",
            "context": {
                "viewport_width": 1024,
                "viewport_height": 768,
                "user_behavior": {"device_type": "tablet"},
                "context": {"time_of_day": "morning"},
                "scroll_depth": 0.7,
                "time_on_page": 180
            },
            "expected_class": "densidad-media|fuente-serif|modo-claro",
            "expected_variables": {
                "--font-size-base": 1.1,
                "--spacing-factor": 1.0,
                "--border-radius": 6
            }
        }
    ]


@pytest.fixture
def model_performance_benchmarks():
    """Performance benchmarks for model validation."""
    return {
        "classification": {
            "min_accuracy": 0.70,
            "min_f1_score": 0.65,
            "min_precision": 0.70,
            "min_recall": 0.60,
            "max_prediction_time_ms": 50
        },
        "regression": {
            "max_mae": 0.15,
            "min_r2_score": 0.50,
            "max_rmse": 0.25,
            "max_prediction_time_ms": 50
        },
        "system": {
            "max_memory_usage_mb": 500,
            "max_model_load_time_s": 10,
            "min_throughput_per_sec": 100
        }
    }


@pytest.fixture
def feature_importance_expectations():
    """Expected feature importance rankings for model validation."""
    return {
        "classification": {
            "high_importance": [
                "viewport_width", "viewport_height", "is_mobile", 
                "scroll_depth", "time_on_page"
            ],
            "medium_importance": [
                "hour", "click_rate", "device_pixel_ratio", "touch_enabled"
            ],
            "low_importance": [
                "is_weekend", "pages_visited"
            ]
        },
        "regression": {
            "high_importance": [
                "viewport_width", "is_mobile", "scroll_depth", "time_on_page"
            ],
            "medium_importance": [
                "viewport_height", "hour", "click_rate"
            ],
            "low_importance": [
                "is_weekend", "primary_hue"
            ]
        }
    }


@pytest.fixture
def cross_validation_splits():
    """Pre-defined cross-validation splits for reproducible testing."""
    np.random.seed(42)
    n_samples = 500
    indices = np.arange(n_samples)
    np.random.shuffle(indices)
    
    # 5-fold cross validation
    fold_size = n_samples // 5
    splits = []
    
    for i in range(5):
        start_idx = i * fold_size
        end_idx = start_idx + fold_size if i < 4 else n_samples
        
        test_indices = indices[start_idx:end_idx]
        train_indices = np.concatenate([indices[:start_idx], indices[end_idx:]])
        
        splits.append({
            "fold": i + 1,
            "train_indices": train_indices,
            "test_indices": test_indices,
            "train_size": len(train_indices),
            "test_size": len(test_indices)
        })
    
    return splits


@pytest.fixture
def hyperparameter_test_configs():
    """Hyperparameter configurations for model testing."""
    return {
        "classification": [
            {
                "name": "balanced_config",
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1,
                "subsample": 0.8,
                "colsample_bytree": 0.8
            },
            {
                "name": "conservative_config", 
                "n_estimators": 50,
                "max_depth": 4,
                "learning_rate": 0.05,
                "subsample": 0.9,
                "colsample_bytree": 0.9
            },
            {
                "name": "aggressive_config",
                "n_estimators": 200,
                "max_depth": 8,
                "learning_rate": 0.2,
                "subsample": 0.7,
                "colsample_bytree": 0.7
            }
        ],
        "regression": [
            {
                "name": "balanced_config",
                "n_estimators": 100,
                "max_depth": 5,
                "learning_rate": 0.1,
                "subsample": 0.8,
                "colsample_bytree": 0.8
            },
            {
                "name": "conservative_config",
                "n_estimators": 75,
                "max_depth": 3,
                "learning_rate": 0.05,
                "subsample": 0.9,
                "colsample_bytree": 0.9
            }
        ]
    }


@pytest.fixture
def data_quality_checks():
    """Data quality validation checks for training data."""
    return {
        "feature_checks": [
            {
                "name": "no_missing_values",
                "check": lambda X: not np.isnan(X).any(),
                "error_message": "Training data contains missing values"
            },
            {
                "name": "no_infinite_values", 
                "check": lambda X: not np.isinf(X).any(),
                "error_message": "Training data contains infinite values"
            },
            {
                "name": "correct_shape",
                "check": lambda X: X.shape[1] == 21,
                "error_message": "Feature matrix should have 21 columns"
            },
            {
                "name": "positive_viewport_dimensions",
                "check": lambda X: (X[:, 0] > 0).all() and (X[:, 1] > 0).all(),
                "error_message": "Viewport dimensions should be positive"
            }
        ],
        "label_checks": [
            {
                "name": "valid_class_format",
                "check": lambda y: all("|" in label and len(label.split("|")) == 3 for label in y),
                "error_message": "Class labels should follow 'density|font|theme' format"
            },
            {
                "name": "positive_regression_targets",
                "check": lambda y: (y >= 0).all(),
                "error_message": "Regression targets should be non-negative"
            }
        ]
    }
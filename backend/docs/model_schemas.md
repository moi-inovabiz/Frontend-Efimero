# Model Data Schemas & Formats

## Overview

This document defines the data schemas, formats, and structures used throughout the XGBoost training and inference pipeline.

## Data Schema Definitions

### 1. Feature Schema

#### Input Features (19 dimensions)

```python
# Feature vector schema
FeatureVector = np.ndarray[19, dtype=float64]

# Feature names with descriptions
FEATURE_SCHEMA = {
    # Temporal Features (0-3)
    'hour_of_day': {
        'index': 0,
        'type': 'int',
        'range': [0, 23],
        'description': 'Hour extracted from user local time'
    },
    'is_weekend': {
        'index': 1,
        'type': 'bool',
        'range': [0, 1],
        'description': 'Saturday or Sunday flag'
    },
    'is_business_hours': {
        'index': 2,
        'type': 'bool',
        'range': [0, 1],
        'description': '9AM-6PM weekday flag'
    },
    'time_intensity': {
        'index': 3,
        'type': 'float',
        'range': [0.0, 1.0],
        'description': 'Activity level by time of day'
    },
    
    # Device Features (4-8)
    'is_mobile': {
        'index': 4,
        'type': 'bool',
        'range': [0, 1],
        'description': 'Viewport width < 768px'
    },
    'is_tablet': {
        'index': 5,
        'type': 'bool',
        'range': [0, 1],
        'description': '768px <= viewport width < 1024px'
    },
    'is_desktop': {
        'index': 6,
        'type': 'bool',
        'range': [0, 1],
        'description': 'Viewport width >= 1024px'
    },
    'touch_enabled': {
        'index': 7,
        'type': 'bool',
        'range': [0, 1],
        'description': 'Touch capability from user agent'
    },
    'device_pixel_ratio': {
        'index': 8,
        'type': 'float',
        'range': [0.5, 4.0],
        'description': 'Device pixel density ratio'
    },
    
    # Viewport Features (9-12)
    'viewport_area': {
        'index': 9,
        'type': 'float',
        'range': [182400, 33177600],  # 320x568 to 7680x4320
        'description': 'Viewport width × height'
    },
    'aspect_ratio': {
        'index': 10,
        'type': 'float',
        'range': [0.3, 3.0],
        'description': 'Viewport width ÷ height'
    },
    'viewport_diagonal': {
        'index': 11,
        'type': 'float',
        'range': [412, 8640],  # Calculated diagonals
        'description': 'Viewport diagonal size in pixels'
    },
    'pixel_density': {
        'index': 12,
        'type': 'float',
        'range': [0.1, 10.0],
        'description': 'Pixels per unit area'
    },
    
    # Historical Features (13-15)
    'avg_session_duration': {
        'index': 13,
        'type': 'float',
        'range': [0, 3600000],  # 0 to 1 hour in ms
        'description': 'Average session time in milliseconds'
    },
    'total_interactions': {
        'index': 14,
        'type': 'float',
        'range': [0, 1000],
        'description': 'Total user interactions count'
    },
    'days_since_first_visit': {
        'index': 15,
        'type': 'float',
        'range': [0, 365],
        'description': 'User tenure in days'
    },
    
    # Segmentation Features (16-18)
    'user_density_group': {
        'index': 16,
        'type': 'float',
        'range': [0, 2],  # 0=low, 1=medium, 2=high
        'description': 'User activity classification'
    },
    'estimated_network_speed': {
        'index': 17,
        'type': 'float',
        'range': [0, 2],  # 0=slow, 1=medium, 2=fast
        'description': 'Inferred network speed class'
    },
    'accessibility_needs': {
        'index': 18,
        'type': 'float',
        'range': [0, 1],
        'description': 'Accessibility requirements score'
    }
}
```

### 2. Target Schema

#### CSS Classes (Classifier Targets)

```python
# CSS class categories and options
CSS_CLASS_SCHEMA = {
    'density': {
        'options': ['densidad-baja', 'densidad-media', 'densidad-alta'],
        'description': 'Information density level',
        'encoding': 'label',  # Label encoding for XGBoost
        'mapping': {
            'densidad-baja': 0,
            'densidad-media': 1,
            'densidad-alta': 2
        }
    },
    'font': {
        'options': ['fuente-sans', 'fuente-serif', 'fuente-mono'],
        'description': 'Primary font family',
        'encoding': 'label',
        'mapping': {
            'fuente-sans': 0,
            'fuente-serif': 1,
            'fuente-mono': 2
        }
    },
    'theme': {
        'options': ['tema-claro', 'tema-oscuro', 'tema-auto'],
        'description': 'Color theme preference',
        'encoding': 'label',
        'mapping': {
            'tema-claro': 0,
            'tema-oscuro': 1,
            'tema-auto': 2
        }
    }
}

# Complete classifier target structure
ClassifierTarget = Tuple[int, int, int]  # (density, font, theme)
```

#### CSS Variables (Regressor Targets)

```python
# CSS variable schema
CSS_VARIABLE_SCHEMA = {
    'font_size_base': {
        'index': 0,
        'type': 'float',
        'range': [0.8, 1.5],
        'unit': 'rem',
        'description': 'Base font size multiplier'
    },
    'line_height_base': {
        'index': 1,
        'type': 'float',
        'range': [1.2, 2.0],
        'unit': 'ratio',
        'description': 'Base line height ratio'
    },
    'spacing_base': {
        'index': 2,
        'type': 'float',
        'range': [12, 32],
        'unit': 'px',
        'description': 'Base spacing unit'
    },
    'border_radius_base': {
        'index': 3,
        'type': 'float',
        'range': [0, 16],
        'unit': 'px',
        'description': 'Base border radius'
    },
    'color_primary_h': {
        'index': 4,
        'type': 'float',
        'range': [0, 360],
        'unit': 'deg',
        'description': 'Primary color hue'
    },
    'color_primary_s': {
        'index': 5,
        'type': 'float',
        'range': [0, 100],
        'unit': '%',
        'description': 'Primary color saturation'
    },
    'color_primary_l': {
        'index': 6,
        'type': 'float',
        'range': [0, 100],
        'unit': '%',
        'description': 'Primary color lightness'
    },
    'animation_duration': {
        'index': 7,
        'type': 'float',
        'range': [0.1, 1.0],
        'unit': 's',
        'description': 'Base animation duration'
    }
}

# Complete regressor target structure
RegressorTarget = np.ndarray[8, dtype=float64]
```

### 3. Training Data Format

#### CSV Training File Structure

```python
# Complete training CSV schema
TRAINING_CSV_COLUMNS = [
    # Features (19 columns)
    'hour_of_day', 'is_weekend', 'is_business_hours', 'time_intensity',
    'is_mobile', 'is_tablet', 'is_desktop', 'touch_enabled', 'device_pixel_ratio',
    'viewport_area', 'aspect_ratio', 'viewport_diagonal', 'pixel_density',
    'avg_session_duration', 'total_interactions', 'days_since_first_visit',
    'user_density_group', 'estimated_network_speed', 'accessibility_needs',
    
    # CSS Class Targets (3 columns)
    'css_class_density', 'css_class_font', 'css_class_theme',
    
    # CSS Variable Targets (8 columns)
    'font_size_base', 'line_height_base', 'spacing_base', 'border_radius_base',
    'color_primary_h', 'color_primary_s', 'color_primary_l', 'animation_duration'
]

# Total columns: 19 + 3 + 8 = 30 columns
```

#### JSON Training File Structure

```json
{
    "metadata": {
        "version": "1.0",
        "created_at": "2025-11-02T14:30:00Z",
        "feature_count": 19,
        "sample_count": 1000,
        "data_source": "synthetic_generation",
        "feature_schema_version": "1.0"
    },
    "features": {
        "names": ["hour_of_day", "is_weekend", ...],
        "data": [[14.0, 1.0, 0.0, ...], ...]
    },
    "targets": {
        "css_classes": {
            "names": ["density", "font", "theme"],
            "data": [["densidad-alta", "fuente-sans", "tema-oscuro"], ...]
        },
        "css_variables": {
            "names": ["font_size_base", "line_height_base", ...],
            "data": [[1.15, 1.6, 24, 8, 220, 70, 45, 0.3], ...]
        }
    }
}
```

## Model File Formats

### 1. Trained Model Files

```python
# Model serialization structure
MODEL_FILES = {
    'classifier': {
        'filename': 'xgboost_classifier.joblib',
        'type': 'XGBClassifier',
        'input_shape': (None, 19),
        'output_shape': (None, 9),  # 3 classes × 3 categories
        'format': 'joblib'
    },
    'regressor': {
        'filename': 'xgboost_regressor.joblib',
        'type': 'XGBRegressor',
        'input_shape': (None, 19),
        'output_shape': (None, 8),
        'format': 'joblib'
    },
    'scaler': {
        'filename': 'feature_scaler.joblib',
        'type': 'StandardScaler',
        'input_shape': (None, 19),
        'output_shape': (None, 19),
        'format': 'joblib'
    }
}
```

### 2. Model Metadata

```json
{
    "model_version": "20251102_143000",
    "training_date": "2025-11-02T14:30:00Z",
    "feature_schema_version": "1.0",
    "target_schema_version": "1.0",
    
    "training_config": {
        "dataset_size": 5000,
        "test_split": 0.2,
        "cv_folds": 5,
        "random_state": 42
    },
    
    "model_params": {
        "classifier": {
            "objective": "multi:softprob",
            "num_class": 9,
            "learning_rate": 0.1,
            "max_depth": 6,
            "n_estimators": 100
        },
        "regressor": {
            "objective": "reg:squarederror",
            "learning_rate": 0.1,
            "max_depth": 6,
            "n_estimators": 100
        }
    },
    
    "performance_metrics": {
        "classifier": {
            "accuracy": 0.87,
            "precision": 0.85,
            "recall": 0.86,
            "f1_score": 0.85,
            "log_loss": 0.34
        },
        "regressor": {
            "mse": 0.023,
            "rmse": 0.15,
            "mae": 0.12,
            "r2_score": 0.82
        }
    },
    
    "dependencies": {
        "xgboost": "1.7.6",
        "scikit-learn": "1.3.0",
        "numpy": "1.24.3",
        "pandas": "2.0.3"
    }
}
```

## API Response Schemas

### 1. Prediction Request

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PredictionRequest(BaseModel):
    """API request for adaptive UI prediction."""
    
    user_context: UserContext
    user_temp_id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "user_context": {
                    "hora_local": "2025-11-02T14:30:00",
                    "prefers_color_scheme": "dark",
                    "viewport_width": 1920,
                    "viewport_height": 1080,
                    "touch_enabled": False,
                    "device_pixel_ratio": 2.0,
                    "user_agent": "Mozilla/5.0 Chrome/118.0.0.0",
                    "session_id": "session_123",
                    "page_path": "/cars/luxury"
                },
                "user_temp_id": "temp_user_456"
            }
        }
```

### 2. Prediction Response

```python
class PredictionResponse(BaseModel):
    """API response with design tokens."""
    
    design_tokens: DesignTokens
    prediction_confidence: Dict[str, Any]
    processing_time_ms: float
    
    class Config:
        schema_extra = {
            "example": {
                "design_tokens": {
                    "css_classes": [
                        "densidad-alta",
                        "fuente-sans", 
                        "tema-oscuro"
                    ],
                    "css_variables": {
                        "--font-size-base": "1.15rem",
                        "--line-height-base": "1.6",
                        "--spacing-base": "24px",
                        "--border-radius-base": "8px",
                        "--color-primary-h": "220deg",
                        "--color-primary-s": "70%",
                        "--color-primary-l": "45%",
                        "--animation-duration": "0.3s"
                    }
                },
                "prediction_confidence": {
                    "classifier": {
                        "density": {"densidad-alta": 0.85, "densidad-media": 0.12, "densidad-baja": 0.03},
                        "font": {"fuente-sans": 0.78, "fuente-serif": 0.15, "fuente-mono": 0.07},
                        "theme": {"tema-oscuro": 0.92, "tema-claro": 0.06, "tema-auto": 0.02}
                    },
                    "regressor": {
                        "r2_score": 0.82,
                        "prediction_std": 0.15
                    }
                },
                "processing_time_ms": 23.5
            }
        }
```

## Data Validation

### 1. Feature Validation

```python
def validate_features(features: np.ndarray) -> Dict[str, bool]:
    """Validate feature vector against schema."""
    
    validation_results = {}
    
    # Shape validation
    validation_results['correct_shape'] = features.shape == (19,)
    
    # Data type validation
    validation_results['correct_dtype'] = features.dtype == np.float64
    
    # Range validations
    for feature_name, schema in FEATURE_SCHEMA.items():
        index = schema['index']
        min_val, max_val = schema['range']
        
        validation_results[f'{feature_name}_range'] = (
            min_val <= features[index] <= max_val
        )
    
    # Special validations
    validation_results['no_nan_inf'] = np.isfinite(features).all()
    validation_results['binary_features'] = all(
        features[i] in [0.0, 1.0] for i in [1, 2, 4, 5, 6, 7]
    )
    
    return validation_results
```

### 2. Target Validation

```python
def validate_targets(css_classes: List[str], css_variables: np.ndarray) -> Dict[str, bool]:
    """Validate prediction targets against schema."""
    
    validation_results = {}
    
    # CSS Classes validation
    validation_results['css_classes_count'] = len(css_classes) == 3
    
    valid_density = css_classes[0] in CSS_CLASS_SCHEMA['density']['options']
    valid_font = css_classes[1] in CSS_CLASS_SCHEMA['font']['options']
    valid_theme = css_classes[2] in CSS_CLASS_SCHEMA['theme']['options']
    
    validation_results['valid_css_classes'] = all([valid_density, valid_font, valid_theme])
    
    # CSS Variables validation
    validation_results['css_variables_shape'] = css_variables.shape == (8,)
    validation_results['css_variables_dtype'] = css_variables.dtype == np.float64
    
    # Range validations for variables
    for var_name, schema in CSS_VARIABLE_SCHEMA.items():
        index = schema['index']
        min_val, max_val = schema['range']
        
        validation_results[f'{var_name}_range'] = (
            min_val <= css_variables[index] <= max_val
        )
    
    return validation_results
```

## Data Conversion Utilities

### 1. Format Converters

```python
def csv_to_json(csv_path: str, json_path: str) -> None:
    """Convert CSV training data to JSON format."""
    
    df = pd.read_csv(csv_path)
    
    # Separate features and targets
    feature_cols = TRAINING_CSV_COLUMNS[:19]
    class_cols = TRAINING_CSV_COLUMNS[19:22]
    variable_cols = TRAINING_CSV_COLUMNS[22:]
    
    data = {
        "metadata": {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "feature_count": len(feature_cols),
            "sample_count": len(df),
            "data_source": "csv_conversion"
        },
        "features": {
            "names": feature_cols,
            "data": df[feature_cols].values.tolist()
        },
        "targets": {
            "css_classes": {
                "names": ["density", "font", "theme"],
                "data": df[class_cols].values.tolist()
            },
            "css_variables": {
                "names": variable_cols,
                "data": df[variable_cols].values.tolist()
            }
        }
    }
    
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
```

### 2. Schema Converters

```python
def predictions_to_css(class_predictions: np.ndarray, variable_predictions: np.ndarray) -> DesignTokens:
    """Convert model predictions to CSS design tokens."""
    
    # Decode class predictions
    css_classes = [
        list(CSS_CLASS_SCHEMA['density']['options'])[int(class_predictions[0])],
        list(CSS_CLASS_SCHEMA['font']['options'])[int(class_predictions[1])],
        list(CSS_CLASS_SCHEMA['theme']['options'])[int(class_predictions[2])]
    ]
    
    # Format variable predictions
    css_variables = {}
    for var_name, schema in CSS_VARIABLE_SCHEMA.items():
        index = schema['index']
        value = variable_predictions[index]
        unit = schema['unit']
        
        if unit == 'ratio':
            css_variables[f'--{var_name.replace("_", "-")}'] = str(value)
        else:
            css_variables[f'--{var_name.replace("_", "-")}'] = f"{value}{unit}"
    
    return DesignTokens(
        css_classes=css_classes,
        css_variables=css_variables
    )
```

This comprehensive schema documentation ensures consistent data handling across the entire XGBoost pipeline.
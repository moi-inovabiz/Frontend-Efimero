# Feature Engineering Architecture

## Overview

The Feature Engineering system transforms raw user context data into numerical features suitable for XGBoost models. This document describes the complete architecture, transformations, and usage patterns.

## Architecture Components

### FeatureProcessor Class

The `FeatureProcessor` is the core component responsible for converting `UserContext` objects into numerical feature vectors.

**Location**: `app/ml/feature_processor.py`

```python
class FeatureProcessor:
    """
    Converts UserContext objects to numerical features for ML models.
    
    Features Generated: 19 numerical features covering:
    - Temporal patterns (4 features)
    - Device characteristics (5 features) 
    - Viewport calculations (4 features)
    - Historical behavior (3 features)
    - User segmentation (3 features)
    """
```

### Feature Categories

#### 1. Temporal Features (4 features)
- **hour_of_day**: Extracted from `hora_local` (0-23)
- **is_weekend**: Boolean flag for Saturday/Sunday
- **is_business_hours**: Boolean flag for 9AM-6PM weekdays
- **time_intensity**: Activity level based on hour (higher during peak times)

#### 2. Device Features (5 features)
- **is_mobile**: Inferred from viewport width (<768px)
- **is_tablet**: Inferred from viewport width (768-1024px)
- **is_desktop**: Inferred from viewport width (>1024px)
- **touch_enabled**: Direct from UserContext
- **device_pixel_ratio**: Direct from UserContext

#### 3. Viewport Features (4 features)
- **viewport_area**: Width × Height in pixels
- **aspect_ratio**: Width ÷ Height ratio
- **viewport_diagonal**: Calculated diagonal size
- **pixel_density**: Total pixels per viewport area

#### 4. Historical Features (3 features)
- **avg_session_duration**: Average time spent (from historical data)
- **total_interactions**: Cumulative interaction count
- **days_since_first_visit**: User tenure calculation

#### 5. User Segmentation Features (3 features)
- **user_density_group**: Low/Medium/High activity classification
- **estimated_network_speed**: Inferred from device and context
- **accessibility_needs**: Special requirements detection

## Feature Extraction Process

### Input Processing

```python
def prepare_features_v2(
    self, 
    user_context: UserContext, 
    historical_data: Optional[List[Dict]] = None
) -> np.ndarray:
    """
    Main feature extraction method.
    
    Args:
        user_context: Current user context
        historical_data: Optional historical behavior data
        
    Returns:
        np.ndarray: 19 numerical features ready for ML models
    """
```

### Feature Pipeline

1. **Validation**: Input validation using Pydantic models
2. **Temporal Extraction**: Time-based feature calculation
3. **Device Classification**: Device type and capability inference
4. **Viewport Analysis**: Screen dimension calculations
5. **Historical Integration**: Past behavior incorporation
6. **Segmentation**: User group classification
7. **Normalization**: Feature scaling and standardization

### Error Handling & Fallbacks

The system implements robust error handling with graceful fallbacks:

```python
# Example fallback for missing historical data
if not historical_data:
    features.extend([0.0, 0.0, 0.0])  # Default historical features
```

**Fallback Strategies**:
- Missing historical data → Default values (0.0)
- Invalid viewport → Minimum viable dimensions (320x568)
- Malformed timestamps → Current system time
- Network detection failure → Medium-speed assumption

## Feature Validation

### Input Validation

```python
def validate_user_context(user_context: UserContext) -> bool:
    """Validates UserContext before feature extraction."""
    
    # Required fields check
    required_fields = ['hora_local', 'viewport_width', 'viewport_height']
    
    # Range validation
    assert 1 <= user_context.viewport_width <= 7680, "Invalid viewport width"
    assert 1 <= user_context.viewport_height <= 4320, "Invalid viewport height"
    
    return True
```

### Feature Quality Checks

```python
def validate_features(features: np.ndarray) -> bool:
    """Validates extracted feature quality."""
    
    # Check feature count
    assert len(features) == 19, f"Expected 19 features, got {len(features)}"
    
    # Check for NaN/Inf values
    assert np.isfinite(features).all(), "Features contain NaN/Inf values"
    
    # Range checks for specific features
    assert 0 <= features[0] <= 23, "hour_of_day out of range"
    assert features[8] > 0, "viewport_area must be positive"
    
    return True
```

## Usage Patterns

### Basic Usage

```python
from app.ml.feature_processor import FeatureProcessor
from app.models.adaptive_ui import UserContext

# Initialize processor
processor = FeatureProcessor()

# Create user context
context = UserContext(
    hora_local=datetime.now(),
    prefers_color_scheme="dark",
    viewport_width=1920,
    viewport_height=1080,
    touch_enabled=False,
    device_pixel_ratio=2.0,
    user_agent="Mozilla/5.0 Chrome/118.0.0.0",
    session_id="session_123",
    page_path="/cars/luxury"
)

# Extract features
features = processor.prepare_features_v2(context)
print(f"Features shape: {features.shape}")  # (19,)
```

### With Historical Data

```python
# Include historical behavior data
historical_data = [
    {
        "timestamp": "2025-11-01T10:00:00",
        "session_duration": 120000,  # 2 minutes in ms
        "interactions": 5,
        "page_views": 3
    },
    {
        "timestamp": "2025-11-01T15:30:00", 
        "session_duration": 300000,  # 5 minutes in ms
        "interactions": 12,
        "page_views": 8
    }
]

# Extract enhanced features
features = processor.prepare_features_v2(context, historical_data)
```

### Integration with Models

```python
from app.ml.model_manager import ModelManager

# Full prediction pipeline
processor = FeatureProcessor()
model_manager = ModelManager()

# Extract features
features = processor.prepare_features_v2(user_context)

# Make predictions
css_classes = model_manager.classifier.predict([features])
css_variables = model_manager.regressor.predict([features])
```

## Performance Considerations

### Computational Complexity

- **Feature Extraction**: O(1) - constant time operations
- **Historical Processing**: O(n) where n = number of historical records
- **Memory Usage**: ~152 bytes per feature vector (19 × 8 bytes)

### Optimization Strategies

1. **Feature Caching**: Cache computed features for repeated contexts
2. **Batch Processing**: Process multiple contexts simultaneously
3. **Historical Limiting**: Limit historical data to recent N records
4. **Lazy Loading**: Load historical data only when needed

### Benchmarks

```python
# Performance targets (measured in production)
Feature Extraction Time: <1ms average
Memory Footprint: <10MB for 1000 contexts
Batch Processing: 100 contexts in <5ms
```

## Feature Engineering Best Practices

### 1. Feature Stability

- **Consistent Ranges**: Ensure features maintain stable ranges across updates
- **Backward Compatibility**: New features should not break existing models
- **Version Control**: Track feature schema versions

### 2. Data Quality

- **Validation First**: Always validate inputs before processing
- **Graceful Degradation**: Handle missing/invalid data gracefully
- **Monitoring**: Track feature distribution changes

### 3. Model Compatibility

- **Feature Order**: Maintain consistent feature ordering
- **Scaling Consistency**: Use same scaling across training/inference
- **Type Safety**: Ensure consistent data types (float64)

## Troubleshooting

### Common Issues

#### 1. Feature Dimension Mismatch
```python
# Error: Expected 19 features, got 18
# Solution: Check feature extraction logic for missing features
features = processor.prepare_features_v2(context)
assert len(features) == 19, f"Feature count mismatch: {len(features)}"
```

#### 2. NaN/Infinite Values
```python
# Error: Features contain NaN values
# Solution: Add validation and fallback logic
if np.isnan(features).any():
    logger.warning("NaN values detected, applying fallbacks")
    features = np.nan_to_num(features, nan=0.0)
```

#### 3. Historical Data Issues
```python
# Error: Historical data processing fails
# Solution: Validate historical data structure
if historical_data:
    required_keys = ['timestamp', 'session_duration', 'interactions']
    for record in historical_data:
        assert all(key in record for key in required_keys)
```

### Debugging Tools

#### Feature Inspector
```python
def inspect_features(features: np.ndarray) -> Dict[str, float]:
    """Debug helper to examine feature values."""
    
    feature_names = [
        'hour_of_day', 'is_weekend', 'is_business_hours', 'time_intensity',
        'is_mobile', 'is_tablet', 'is_desktop', 'touch_enabled', 'device_pixel_ratio',
        'viewport_area', 'aspect_ratio', 'viewport_diagonal', 'pixel_density',
        'avg_session_duration', 'total_interactions', 'days_since_first_visit',
        'user_density_group', 'estimated_network_speed', 'accessibility_needs'
    ]
    
    return dict(zip(feature_names, features))
```

#### Validation Report
```python
def validation_report(features: np.ndarray) -> Dict[str, Any]:
    """Generate comprehensive validation report."""
    
    return {
        'feature_count': len(features),
        'has_nan': np.isnan(features).any(),
        'has_inf': np.isinf(features).any(),
        'min_value': float(np.min(features)),
        'max_value': float(np.max(features)),
        'mean_value': float(np.mean(features)),
        'feature_ranges': {
            'temporal': features[0:4].tolist(),
            'device': features[4:9].tolist(),
            'viewport': features[9:13].tolist(),
            'historical': features[13:16].tolist(),
            'segmentation': features[16:19].tolist()
        }
    }
```

## Future Enhancements

### Planned Features

1. **Dynamic Feature Selection**: Automatically select relevant features per model
2. **Feature Importance Tracking**: Monitor which features drive predictions
3. **Real-time Feature Updates**: Update features based on live user behavior
4. **Cross-session Features**: Features spanning multiple user sessions

### Extensibility

The architecture supports easy extension:

```python
class EnhancedFeatureProcessor(FeatureProcessor):
    """Extended processor with additional features."""
    
    def prepare_features_v3(self, user_context: UserContext) -> np.ndarray:
        """Version 3 with new features."""
        
        base_features = super().prepare_features_v2(user_context)
        
        # Add new features
        new_features = self._extract_advanced_features(user_context)
        
        return np.concatenate([base_features, new_features])
```

## Integration Points

### Model Training
- **Data Pipeline**: Features feed directly into XGBoost training
- **Validation Sets**: Features used for model validation and testing
- **Hyperparameter Tuning**: Feature importance guides parameter selection

### API Integration
- **AdaptiveUIService**: Real-time feature extraction for predictions
- **Caching Layer**: Features cached for performance optimization
- **Monitoring**: Feature quality metrics tracked in production

### Testing Integration
- **Unit Tests**: Individual feature extraction validation
- **Integration Tests**: End-to-end pipeline validation
- **Performance Tests**: Feature extraction speed verification

---

This documentation provides a comprehensive guide to the Feature Engineering architecture. For implementation details, see the source code in `app/ml/feature_processor.py` and related test files.
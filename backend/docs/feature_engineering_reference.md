# Feature Engineering Quick Reference

## Quick Start

```python
from app.ml.feature_processor import FeatureProcessor
from app.models.adaptive_ui import UserContext
from datetime import datetime

# Initialize
processor = FeatureProcessor()

# Create context
context = UserContext(
    hora_local=datetime.now(),
    prefers_color_scheme="dark",
    viewport_width=1920,
    viewport_height=1080,
    touch_enabled=False,
    device_pixel_ratio=2.0,
    user_agent="Mozilla/5.0 Chrome/118.0.0.0",
    session_id="session_123",
    page_path="/cars"
)

# Extract features
features = processor.prepare_features_v2(context)
# Returns: np.ndarray with 19 features
```

## Feature Schema (19 features)

| Index | Feature Name | Type | Range | Description |
|-------|--------------|------|-------|-------------|
| 0 | `hour_of_day` | int | 0-23 | Hour extracted from `hora_local` |
| 1 | `is_weekend` | bool | 0,1 | Saturday or Sunday |
| 2 | `is_business_hours` | bool | 0,1 | 9AM-6PM on weekdays |
| 3 | `time_intensity` | float | 0-1 | Activity level by hour |
| 4 | `is_mobile` | bool | 0,1 | viewport_width < 768 |
| 5 | `is_tablet` | bool | 0,1 | 768 ≤ viewport_width < 1024 |
| 6 | `is_desktop` | bool | 0,1 | viewport_width ≥ 1024 |
| 7 | `touch_enabled` | bool | 0,1 | From UserContext |
| 8 | `device_pixel_ratio` | float | 0.5-4 | From UserContext |
| 9 | `viewport_area` | float | >0 | width × height |
| 10 | `aspect_ratio` | float | >0 | width ÷ height |
| 11 | `viewport_diagonal` | float | >0 | √(width² + height²) |
| 12 | `pixel_density` | float | >0 | area ÷ (width × height) |
| 13 | `avg_session_duration` | float | ≥0 | Average session time (ms) |
| 14 | `total_interactions` | float | ≥0 | Total user interactions |
| 15 | `days_since_first_visit` | float | ≥0 | User tenure in days |
| 16 | `user_density_group` | float | 0-2 | Activity classification |
| 17 | `estimated_network_speed` | float | 0-2 | Speed classification |
| 18 | `accessibility_needs` | float | 0-1 | Special needs detection |

## Common Patterns

### Basic Usage
```python
# Simple extraction
features = processor.prepare_features_v2(context)
```

### With Historical Data
```python
historical = [
    {
        "timestamp": "2025-11-01T10:00:00",
        "session_duration": 120000,
        "interactions": 5,
        "page_views": 3
    }
]
features = processor.prepare_features_v2(context, historical)
```

### Validation
```python
# Validate input
assert isinstance(context, UserContext)
assert 1 <= context.viewport_width <= 7680
assert 1 <= context.viewport_height <= 4320

# Validate output
assert len(features) == 19
assert np.isfinite(features).all()
assert 0 <= features[0] <= 23  # hour_of_day
```

### Error Handling
```python
try:
    features = processor.prepare_features_v2(context)
except Exception as e:
    logger.error(f"Feature extraction failed: {e}")
    # Use fallback or default features
```

## Device Classification

```python
def get_device_type(features):
    """Quick device classification from features."""
    if features[4] == 1.0:  # is_mobile
        return "mobile"
    elif features[5] == 1.0:  # is_tablet
        return "tablet"
    elif features[6] == 1.0:  # is_desktop
        return "desktop"
    else:
        return "unknown"
```

## Feature Interpretation

```python
def interpret_features(features):
    """Quick feature interpretation."""
    return {
        'time': {
            'hour': int(features[0]),
            'weekend': bool(features[1]),
            'business_hours': bool(features[2])
        },
        'device': {
            'type': get_device_type(features),
            'touch': bool(features[7]),
            'pixel_ratio': features[8]
        },
        'viewport': {
            'area': int(features[9]),
            'aspect_ratio': round(features[10], 2),
            'diagonal': round(features[11], 1)
        },
        'user': {
            'avg_session': int(features[13]),
            'interactions': int(features[14]),
            'days_active': int(features[15])
        }
    }
```

## Performance Tips

### Batch Processing
```python
# Process multiple contexts efficiently
contexts = [context1, context2, context3, ...]
features_batch = np.array([
    processor.prepare_features_v2(ctx) for ctx in contexts
])
```

### Caching
```python
# Cache computed features for repeated contexts
cache = {}
cache_key = (context.viewport_width, context.viewport_height, 
             context.touch_enabled, context.hora_local.hour)
if cache_key not in cache:
    cache[cache_key] = processor.prepare_features_v2(context)
features = cache[cache_key]
```

## Debugging

### Feature Inspector
```python
def debug_features(features):
    """Debug helper for feature analysis."""
    names = [
        'hour', 'weekend', 'business', 'intensity',
        'mobile', 'tablet', 'desktop', 'touch', 'pixel_ratio',
        'area', 'aspect', 'diagonal', 'density',
        'avg_session', 'interactions', 'days_active',
        'density_group', 'network_speed', 'accessibility'
    ]
    
    for i, (name, value) in enumerate(zip(names, features)):
        print(f"{i:2d}: {name:15s} = {value:8.3f}")
```

### Validation Checklist
- ✅ Features array has exactly 19 elements
- ✅ No NaN or infinite values
- ✅ hour_of_day in range [0, 23]
- ✅ Boolean features are 0.0 or 1.0
- ✅ viewport_area > 0
- ✅ aspect_ratio > 0
- ✅ Historical features ≥ 0

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Wrong feature count | Missing feature calculation | Check all 5 feature groups |
| NaN values | Division by zero | Add validation and fallbacks |
| Infinite values | Extreme inputs | Clamp values to reasonable ranges |
| Historical errors | Malformed data | Validate historical data structure |
| Performance issues | Large datasets | Use batch processing and caching |

## Testing

```python
# Unit test example
def test_feature_extraction():
    processor = FeatureProcessor()
    context = create_test_context()
    
    features = processor.prepare_features_v2(context)
    
    assert len(features) == 19
    assert np.isfinite(features).all()
    assert 0 <= features[0] <= 23
    assert features[9] > 0  # viewport_area
```

## Integration Points

- **AdaptiveUIService**: Real-time feature extraction
- **ModelManager**: Features → ML predictions
- **API Routes**: HTTP request → features → response
- **Testing**: Mock contexts → feature validation
- **Monitoring**: Feature quality tracking

---

**Files**: 
- Main: `app/ml/feature_processor.py`
- Tests: `tests/test_feature_processor.py`
- Docs: `docs/feature_engineering.md`
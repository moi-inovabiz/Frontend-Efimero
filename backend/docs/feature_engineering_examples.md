# Feature Engineering Examples & Use Cases

## Real-World Usage Examples

### Example 1: Desktop Power User
```python
from datetime import datetime
from app.models.adaptive_ui import UserContext
from app.ml.feature_processor import FeatureProcessor

# Desktop power user context
desktop_context = UserContext(
    hora_local=datetime(2025, 11, 2, 14, 30),  # Saturday afternoon
    prefers_color_scheme="dark",
    viewport_width=2560,  # 4K monitor
    viewport_height=1440,
    touch_enabled=False,
    device_pixel_ratio=2.0,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    referer=None,
    session_id="desktop_power_001",
    page_path="/cars/luxury/performance"
)

processor = FeatureProcessor()
features = processor.prepare_features_v2(desktop_context)

# Expected feature interpretation:
# features[0] = 14.0 (hour_of_day)
# features[1] = 1.0 (is_weekend)
# features[2] = 0.0 (is_business_hours - weekend)
# features[4] = 0.0 (is_mobile - large viewport)
# features[5] = 0.0 (is_tablet)
# features[6] = 1.0 (is_desktop - viewport > 1024px)
# features[7] = 0.0 (touch_enabled)
```

### Example 2: Mobile Casual User
```python
# Mobile user context
mobile_context = UserContext(
    hora_local=datetime(2025, 11, 2, 20, 15),  # Evening
    prefers_color_scheme="light",
    viewport_width=390,  # iPhone width
    viewport_height=844,
    touch_enabled=True,
    device_pixel_ratio=3.0,
    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    referer=None,
    session_id="mobile_casual_001",
    page_path="/cars/compact"
)

features = processor.prepare_features_v2(mobile_context)

# Expected feature interpretation:
# features[0] = 20.0 (hour_of_day)
# features[1] = 1.0 (is_weekend)
# features[2] = 0.0 (is_business_hours - evening)
# features[4] = 1.0 (is_mobile - viewport < 768px)
# features[5] = 0.0 (is_tablet)
# features[6] = 0.0 (is_desktop)
# features[7] = 1.0 (touch_enabled)
```

### Example 3: With Historical Data
```python
# User with historical behavior
historical_data = [
    {
        "timestamp": "2025-11-01T10:00:00",
        "session_duration": 180000,  # 3 minutes
        "interactions": 8,
        "page_views": 4
    },
    {
        "timestamp": "2025-11-01T15:30:00",
        "session_duration": 420000,  # 7 minutes
        "interactions": 15,
        "page_views": 6
    },
    {
        "timestamp": "2025-10-30T09:15:00",
        "session_duration": 240000,  # 4 minutes
        "interactions": 10,
        "page_views": 5
    }
]

features = processor.prepare_features_v2(desktop_context, historical_data)

# Historical features will be calculated:
# features[13] = avg_session_duration (300000ms = 5 minutes average)
# features[14] = total_interactions (33 total)
# features[15] = days_since_first_visit (3 days)
```

## Feature Interpretation Guide

### Temporal Features Analysis

```python
def analyze_temporal_features(features: np.ndarray) -> Dict[str, str]:
    """Analyze temporal characteristics from features."""
    
    hour = int(features[0])
    is_weekend = bool(features[1])
    is_business = bool(features[2])
    intensity = features[3]
    
    # Time classification
    if 6 <= hour <= 11:
        time_period = "Morning"
    elif 12 <= hour <= 17:
        time_period = "Afternoon"
    elif 18 <= hour <= 22:
        time_period = "Evening"
    else:
        time_period = "Night"
    
    # Activity level
    if intensity > 0.8:
        activity = "Peak"
    elif intensity > 0.5:
        activity = "High"
    elif intensity > 0.3:
        activity = "Medium"
    else:
        activity = "Low"
    
    return {
        "time_period": time_period,
        "day_type": "Weekend" if is_weekend else "Weekday",
        "business_hours": "Yes" if is_business else "No",
        "activity_level": activity
    }
```

### Device Classification

```python
def classify_device(features: np.ndarray) -> Dict[str, Any]:
    """Classify device characteristics from features."""
    
    is_mobile = bool(features[4])
    is_tablet = bool(features[5])
    is_desktop = bool(features[6])
    touch_enabled = bool(features[7])
    pixel_ratio = features[8]
    
    # Device type
    if is_mobile:
        device_type = "Mobile"
        form_factor = "Phone"
    elif is_tablet:
        device_type = "Tablet"
        form_factor = "Tablet"
    elif is_desktop:
        device_type = "Desktop"
        form_factor = "Computer"
    else:
        device_type = "Unknown"
        form_factor = "Unknown"
    
    # Display quality
    if pixel_ratio >= 3.0:
        display_quality = "Retina/High-DPI"
    elif pixel_ratio >= 2.0:
        display_quality = "High-DPI"
    else:
        display_quality = "Standard"
    
    return {
        "device_type": device_type,
        "form_factor": form_factor,
        "touch_capable": "Yes" if touch_enabled else "No",
        "display_quality": display_quality,
        "pixel_ratio": pixel_ratio
    }
```

### Viewport Analysis

```python
def analyze_viewport(features: np.ndarray) -> Dict[str, Any]:
    """Analyze viewport characteristics from features."""
    
    area = features[9]
    aspect_ratio = features[10]
    diagonal = features[11]
    pixel_density = features[12]
    
    # Screen size classification
    if area < 500000:  # < 500k pixels
        size_class = "Small"
    elif area < 2000000:  # < 2M pixels
        size_class = "Medium"
    elif area < 8000000:  # < 8M pixels
        size_class = "Large"
    else:
        size_class = "Extra Large"
    
    # Aspect ratio interpretation
    if aspect_ratio < 1.2:
        orientation = "Square"
    elif aspect_ratio < 1.5:
        orientation = "Slightly Wide"
    elif aspect_ratio < 2.0:
        orientation = "Wide"
    else:
        orientation = "Ultra Wide"
    
    return {
        "size_class": size_class,
        "total_pixels": int(area),
        "orientation": orientation,
        "aspect_ratio": round(aspect_ratio, 2),
        "diagonal_size": round(diagonal, 1),
        "pixel_density": round(pixel_density, 2)
    }
```

## Feature Validation Examples

### Input Validation
```python
def validate_context_example():
    """Example of comprehensive context validation."""
    
    # Valid context
    valid_context = UserContext(
        hora_local=datetime.now(),
        prefers_color_scheme="dark",
        viewport_width=1920,
        viewport_height=1080,
        touch_enabled=False,
        device_pixel_ratio=2.0,
        user_agent="Mozilla/5.0 Chrome/118.0.0.0",
        session_id="test_session",
        page_path="/test"
    )
    
    processor = FeatureProcessor()
    
    try:
        features = processor.prepare_features_v2(valid_context)
        print(f"✅ Valid context processed: {len(features)} features")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
    
    # Invalid context (extreme viewport)
    try:
        invalid_context = UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme="dark",
            viewport_width=10000,  # Too large
            viewport_height=10000,
            touch_enabled=False,
            device_pixel_ratio=2.0,
            user_agent="Mozilla/5.0 Chrome/118.0.0.0",
            session_id="test_session",
            page_path="/test"
        )
        
        features = processor.prepare_features_v2(invalid_context)
        print(f"⚠️ Invalid context accepted (fallback used): {len(features)} features")
    except Exception as e:
        print(f"❌ Invalid context rejected: {e}")
```

### Feature Quality Checks
```python
def feature_quality_example():
    """Example of feature quality validation."""
    
    context = UserContext(
        hora_local=datetime(2025, 11, 2, 15, 30),
        prefers_color_scheme="dark",
        viewport_width=1366,
        viewport_height=768,
        touch_enabled=False,
        device_pixel_ratio=1.0,
        user_agent="Mozilla/5.0 Safari/537.36",
        session_id="quality_test",
        page_path="/test"
    )
    
    processor = FeatureProcessor()
    features = processor.prepare_features_v2(context)
    
    # Quality checks
    checks = {
        "correct_length": len(features) == 19,
        "no_nan_values": not np.isnan(features).any(),
        "no_inf_values": not np.isinf(features).any(),
        "hour_range": 0 <= features[0] <= 23,
        "positive_area": features[9] > 0,
        "valid_aspect_ratio": features[10] > 0,
        "binary_flags": all(f in [0.0, 1.0] for f in features[1:8])
    }
    
    print("Feature Quality Report:")
    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check}: {status}")
    
    return all(checks.values())
```

## Performance Optimization Examples

### Batch Processing
```python
def batch_processing_example():
    """Example of efficient batch feature processing."""
    
    # Multiple contexts
    contexts = [
        UserContext(
            hora_local=datetime(2025, 11, 2, 10, 0),
            prefers_color_scheme="light",
            viewport_width=390, viewport_height=844,
            touch_enabled=True, device_pixel_ratio=3.0,
            user_agent="iPhone", session_id=f"mobile_{i}",
            page_path="/cars"
        )
        for i in range(100)
    ]
    
    processor = FeatureProcessor()
    
    # Sequential processing (slower)
    start_time = time.time()
    features_sequential = []
    for context in contexts:
        features = processor.prepare_features_v2(context)
        features_sequential.append(features)
    sequential_time = time.time() - start_time
    
    # Batch processing (faster)
    start_time = time.time()
    features_batch = np.array([
        processor.prepare_features_v2(context) 
        for context in contexts
    ])
    batch_time = time.time() - start_time
    
    print(f"Sequential processing: {sequential_time:.3f}s")
    print(f"Batch processing: {batch_time:.3f}s")
    print(f"Speedup: {sequential_time/batch_time:.2f}x")
    
    return features_batch
```

### Feature Caching
```python
class CachedFeatureProcessor:
    """Feature processor with caching for repeated contexts."""
    
    def __init__(self):
        self.processor = FeatureProcessor()
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def prepare_features_cached(
        self, 
        user_context: UserContext,
        historical_data: Optional[List[Dict]] = None
    ) -> np.ndarray:
        """Extract features with caching."""
        
        # Create cache key (exclude historical data for simplicity)
        cache_key = (
            user_context.hora_local.isoformat(),
            user_context.viewport_width,
            user_context.viewport_height,
            user_context.touch_enabled,
            user_context.device_pixel_ratio
        )
        
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        # Cache miss - compute features
        self.cache_misses += 1
        features = self.processor.prepare_features_v2(user_context, historical_data)
        self.cache[cache_key] = features
        
        return features
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get caching performance statistics."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "cache_size": len(self.cache)
        }
```

## Error Handling Examples

### Graceful Degradation
```python
def error_handling_example():
    """Example of robust error handling in feature processing."""
    
    processor = FeatureProcessor()
    
    # Test various error conditions
    test_cases = [
        {
            "name": "Missing Historical Data",
            "context": UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="dark",
                viewport_width=1920, viewport_height=1080,
                touch_enabled=False, device_pixel_ratio=2.0,
                user_agent="Chrome", session_id="test1", page_path="/test"
            ),
            "historical": None
        },
        {
            "name": "Extreme Viewport Values",
            "context": UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="dark",
                viewport_width=50000, viewport_height=50000,  # Extreme values
                touch_enabled=False, device_pixel_ratio=2.0,
                user_agent="Chrome", session_id="test2", page_path="/test"
            ),
            "historical": []
        },
        {
            "name": "Invalid Historical Data",
            "context": UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="dark",
                viewport_width=1366, viewport_height=768,
                touch_enabled=False, device_pixel_ratio=1.0,
                user_agent="Chrome", session_id="test3", page_path="/test"
            ),
            "historical": [{"invalid": "data"}]  # Missing required fields
        }
    ]
    
    for test_case in test_cases:
        try:
            features = processor.prepare_features_v2(
                test_case["context"], 
                test_case["historical"]
            )
            print(f"✅ {test_case['name']}: Successfully handled")
            print(f"   Features: {len(features)}, Sample: {features[:3]}")
        except Exception as e:
            print(f"❌ {test_case['name']}: Failed with error: {e}")
```

## Integration Examples

### Complete Prediction Pipeline
```python
async def complete_prediction_example():
    """Example of complete feature-to-prediction pipeline."""
    
    from app.ml.feature_processor import FeatureProcessor
    from app.ml.model_manager import ModelManager
    from app.services.adaptive_ui_service import AdaptiveUIService
    
    # Initialize components
    feature_processor = FeatureProcessor()
    model_manager = ModelManager()
    ui_service = AdaptiveUIService()
    
    # User context
    context = UserContext(
        hora_local=datetime(2025, 11, 2, 14, 30),
        prefers_color_scheme="dark",
        viewport_width=1920, viewport_height=1080,
        touch_enabled=False, device_pixel_ratio=2.0,
        user_agent="Mozilla/5.0 Chrome/118.0.0.0",
        session_id="pipeline_test",
        page_path="/cars/luxury"
    )
    
    # Step 1: Extract features
    features = feature_processor.prepare_features_v2(context)
    print(f"Extracted {len(features)} features")
    
    # Step 2: Make predictions
    if hasattr(model_manager, 'classifier') and model_manager.classifier:
        css_classes = model_manager.classifier.predict([features])
        print(f"Predicted CSS classes: {css_classes}")
    
    if hasattr(model_manager, 'regressor') and model_manager.regressor:
        css_variables = model_manager.regressor.predict([features])
        print(f"Predicted CSS variables: {css_variables}")
    
    # Step 3: Complete adaptive UI response
    try:
        response = await ui_service.get_adaptive_ui(context)
        print(f"Complete UI response generated in {response.processing_time_ms}ms")
        return response
    except Exception as e:
        print(f"UI service error: {e}")
        return None
```

This comprehensive examples document provides practical usage patterns and real-world scenarios for the Feature Engineering system.
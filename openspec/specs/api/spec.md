# API Specification

## Purpose
FastAPI backend that provides adaptive UI prediction endpoints with placeholder ML models.
## Requirements
### Requirement: Adaptive UI Prediction Endpoint
The system SHALL return real ML predictions instead of mock data.

#### Scenario: Real Prediction Response
- WHEN `/api/adaptive-ui/predict` is called with AdaptiveUIRequest
- THEN response SHALL include real XGBoost predictions in AdaptiveUIResponse format
- AND design_tokens.css_classes SHALL be from trained classifier model
- AND design_tokens.css_variables SHALL be from trained regressor model  
- AND response SHALL follow existing DesignTokens Pydantic model

```json
{
  "design_tokens": {
    "css_classes": ["densidad-alta", "fuente-serif", "modo-nocturno"],
    "css_variables": {
      "--font-size-base": "1.15rem",
      "--spacing-factor": "0.82",
      "--color-primary-hue": "210"
    }
  },
  "prediction_confidence": {
    "css_classes": 0.87,
    "css_variables": 0.92
  },
  "processing_time_ms": 45.2
}
```

#### Scenario: Feature Processing Error
- WHEN user context contains invalid or missing features in UserContext
- THEN API SHALL return HTTPException with feature validation details
- AND error SHALL include guidance for proper AdaptiveUIRequest format
- AND AdaptiveUIService SHALL provide fallback default DesignTokens

### Requirement: Health Check Endpoint
The system SHALL provide basic health monitoring.

#### Scenario: Basic Health Check
- WHEN `/health` endpoint is called
- THEN system SHALL return basic service status
- AND response SHALL indicate API availability

### Requirement: Feedback Collection Endpoint
The system SHALL collect user behavior feedback for future model training.

#### Scenario: Feedback Data Storage
- WHEN `/api/adaptive-ui/feedback` is called with behavior data
- THEN system SHALL accept feedback data
- AND feedback SHALL be prepared for future model training

### Requirement: Model Validation in Existing Health Endpoint
The system MUST extend existing health checks to include model status.

#### Scenario: Health Check with Model Status
- WHEN `/health` endpoint is called
- THEN response SHALL include model loading status
- AND response SHALL include last prediction timestamp from ModelManager
- AND response SHALL validate models are properly loaded

```json
{
  "status": "healthy",
  "models": {
    "classifier_loaded": true,
    "regressor_loaded": true,
    "last_prediction": "2025-10-24T15:30:00Z"
  },
  "feature_processor": {
    "status": "ready",
    "methods_available": ["prepare_features", "_extract_temporal_features"]
  }
}
```

### Requirement: Prediction Performance Monitoring
The system MUST track prediction performance in existing AdaptiveUIService.

#### Scenario: Performance Tracking
- WHEN model predictions are executed in AdaptiveUIService
- THEN processing time SHALL be measured and included in processing_time_ms
- AND prediction confidence SHALL be included in prediction_confidence dict
- AND slow predictions (>100ms) SHALL trigger performance warnings


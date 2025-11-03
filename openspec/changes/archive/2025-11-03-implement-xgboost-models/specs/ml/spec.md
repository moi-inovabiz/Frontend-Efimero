# Delta for ML Models Specification

## ADDED Requirements

### Requirement: XGBoost Dual Model Architecture
The system MUST implement dual XGBoost models for UI adaptation predictions.

#### Scenario: CSS Class Prediction
- WHEN user context is processed for styling
- THEN XGBoost Classifier SHALL predict CSS classes from trained categories
- AND predictions SHALL include confidence scores
- AND classes SHALL be valid Tailwind CSS compatible identifiers

#### Scenario: CSS Variable Prediction  
- WHEN user context requires continuous styling values
- THEN XGBoost Regressor SHALL predict numeric CSS variable values
- AND values SHALL be within valid CSS ranges
- AND predictions SHALL include uncertainty bounds

### Requirement: Feature Engineering Pipeline
The system MUST convert user context into ML-ready features.

#### Scenario: Context Feature Extraction
- WHEN user context data is received
- THEN Feature Processor SHALL extract numeric features using prepare_features method
- AND features SHALL include temporal, device, historical, and social features
- AND feature validation SHALL prevent invalid inputs

#### Scenario: Feature Preprocessing
- WHEN raw context includes temporal, device, and social data
- THEN preprocessing SHALL handle missing values with default fallbacks
- AND temporal features SHALL use sine/cosine encoding for cyclical data
- AND device features SHALL be normalized to standard ranges

### Requirement: Model Performance
The system MUST meet real-time inference requirements.

#### Scenario: Inference Speed
- WHEN model prediction is requested
- THEN inference MUST complete within 100ms
- AND models SHALL be memory-resident (no disk I/O during prediction)
- AND prediction pipeline SHALL include caching for repeated contexts

#### Scenario: Model Loading
- WHEN FastAPI application starts
- THEN XGBoost models SHALL load successfully from serialized files
- AND loading errors SHALL trigger fallback to default styles
- AND model health checks SHALL validate successful loading

### Requirement: Training Data Management
The system MUST support model training with synthetic and real data.

#### Scenario: Synthetic Data Generation
- WHEN training new models
- THEN synthetic data SHALL represent realistic user behavior patterns
- AND data SHALL include sufficient variance for generalization
- AND target labels SHALL map to valid CSS classes and variables

#### Scenario: Model Serialization
- WHEN models are trained successfully
- THEN models SHALL be serialized using Joblib
- AND serialized files SHALL be versioned for rollback capability
- AND model metadata SHALL include training date and performance metrics

## ADDED Components

### Component: Feature Processor
- **Purpose**: Convert user context to ML features using existing FeatureProcessor class
- **Input**: UserContext, historical_data, social_context, is_authenticated
- **Output**: Normalized numpy feature vector
- **Methods**: prepare_features, _extract_temporal_features, _extract_device_features

### Component: XGBoost Classifier
- **Purpose**: Predict CSS classes for styling (replace mock predictions)
- **Input**: Feature vector from FeatureProcessor
- **Output**: CSS class predictions: ["densidad-alta", "fuente-serif", "modo-nocturno"]
- **Integration**: Used by ModelManager.predict_css_classes()

### Component: XGBoost Regressor  
- **Purpose**: Predict continuous CSS variable values (replace mock predictions)
- **Input**: Feature vector from FeatureProcessor
- **Output**: CSS variables dict: {"--font-size-base": "1.15rem", "--spacing-factor": "0.82"}
- **Integration**: Used by ModelManager.predict_css_variables()

### Component: Model Training Pipeline
- **Purpose**: Train and validate XGBoost models offline
- **Input**: Synthetic training dataset with realistic user patterns
- **Output**: Serialized model files (.joblib) in models/ directory
- **Process**: Data generation → Feature engineering → Training → Validation → Serialization
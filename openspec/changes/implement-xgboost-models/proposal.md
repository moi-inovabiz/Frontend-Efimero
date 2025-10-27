# Proposal: Implement XGBoost Models

## Why
Currently, the Frontend Efímero system has placeholder XGBoost models that return mock predictions. The core adaptive UI functionality depends on real ML models to generate CSS class predictions (Classifier model), CSS variable values (Regressor model), and proper feature preprocessing (Feature Scaler). Without functional models, the system cannot demonstrate its primary value proposition of intelligent UI adaptation.

## What Changes
- Implement complete XGBoost ML pipeline with dual model architecture
- XGBoost Classifier for CSS class prediction (`densidad-alta`, `fuente-serif`, `modo-nocturno`)
- XGBoost Regressor for continuous CSS variables (`--font-size-base`, `--spacing-factor`)
- Feature Processor to convert user context into ML-ready features
- Generate synthetic training dataset with realistic user behavior patterns
- Joblib serialization for production model loading with <100ms inference requirement
- Model versioning and validation infrastructure

## Impact
- Affected specs: ml, api
- Affected code: backend/app/ml/model_manager.py, backend/app/ml/feature_processor.py, backend/app/services/adaptive_ui_service.py
- **BREAKING**: Changes mock prediction responses to real ML predictions
- Enables core Frontend Efímero adaptive UI functionality
- Foundation for continuous model improvement with real user data
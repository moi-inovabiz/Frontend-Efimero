# Training Scripts Documentation

## Overview

This document describes the specific training scripts used to train, validate, and deploy XGBoost models for the Frontend Efímero system.

## Script Reference

### 1. Data Generation: `generate_synthetic_data.py`

**Purpose**: Generate realistic synthetic training data for model training.

```bash
# Basic usage
python scripts/generate_synthetic_data.py --size 1000 --output data/synthetic_training_data.csv

# Advanced usage with validation
python scripts/generate_synthetic_data.py \
    --size 5000 \
    --output data/training_v2.csv \
    --validate \
    --seed 42 \
    --export-metadata
```

#### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--size` | int | 1000 | Number of samples to generate |
| `--output` | str | `data/synthetic_training_data.csv` | Output file path |
| `--validate` | flag | False | Run validation after generation |
| `--seed` | int | 42 | Random seed for reproducibility |
| `--export-metadata` | flag | False | Export dataset metadata |
| `--user-patterns` | str | `realistic` | User pattern type: `realistic`, `extreme`, `balanced` |

#### Generated Data Structure

```python
# CSV columns
columns = [
    # Features (19 columns)
    'hour_of_day', 'is_weekend', 'is_business_hours', 'time_intensity',
    'is_mobile', 'is_tablet', 'is_desktop', 'touch_enabled', 'device_pixel_ratio',
    'viewport_area', 'aspect_ratio', 'viewport_diagonal', 'pixel_density',
    'avg_session_duration', 'total_interactions', 'days_since_first_visit',
    'user_density_group', 'estimated_network_speed', 'accessibility_needs',
    
    # Targets - CSS Classes (3 columns)
    'css_class_density', 'css_class_font', 'css_class_theme',
    
    # Targets - CSS Variables (8 columns)
    'font_size_base', 'line_height_base', 'spacing_base', 'border_radius_base',
    'color_primary_h', 'color_primary_s', 'color_primary_l', 'animation_duration'
]
```

#### Usage Examples

```python
# Programmatic usage
from scripts.generate_synthetic_data import DataGenerator

generator = DataGenerator(seed=42)

# Generate dataset
dataset = generator.generate_comprehensive_dataset(
    size=1000,
    user_patterns='realistic'
)

# Export to various formats
generator.export_csv(dataset, 'data/training.csv')
generator.export_json(dataset, 'data/training.json')
generator.export_metadata(dataset, 'data/metadata.json')
```

### 2. Model Training: `train_xgboost_models.py`

**Purpose**: Train XGBoost classifier and regressor models.

```bash
# Basic training
python scripts/train_xgboost_models.py \
    --data data/synthetic_training_data.csv \
    --output models/

# Advanced training with hyperparameter tuning
python scripts/train_xgboost_models.py \
    --data data/synthetic_training_data.csv \
    --output models/ \
    --tune-hyperparams \
    --cv-folds 5 \
    --test-size 0.2 \
    --random-state 42
```

#### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--data` | str | Required | Path to training data CSV |
| `--output` | str | `models/` | Output directory for trained models |
| `--tune-hyperparams` | flag | False | Enable hyperparameter tuning |
| `--cv-folds` | int | 5 | Cross-validation folds |
| `--test-size` | float | 0.2 | Test set proportion |
| `--random-state` | int | 42 | Random seed |
| `--gpu` | flag | False | Enable GPU acceleration |
| `--n-jobs` | int | -1 | Number of parallel jobs |

#### Training Process

```python
def main_training_pipeline(args):
    """Main training pipeline."""
    
    # 1. Load and validate data
    data = load_training_data(args.data)
    validate_training_data(data)
    
    # 2. Split data
    X_train, X_test, y_class_train, y_class_test, y_reg_train, y_reg_test = \
        split_training_data(data, test_size=args.test_size)
    
    # 3. Feature preprocessing
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 4. Train classifier
    if args.tune_hyperparams:
        classifier = train_classifier_with_tuning(X_train_scaled, y_class_train)
    else:
        classifier = train_classifier_default(X_train_scaled, y_class_train)
    
    # 5. Train regressor
    if args.tune_hyperparams:
        regressor = train_regressor_with_tuning(X_train_scaled, y_reg_train)
    else:
        regressor = train_regressor_default(X_train_scaled, y_reg_train)
    
    # 6. Evaluate models
    metrics = evaluate_models(
        classifier, regressor, scaler,
        X_test_scaled, y_class_test, y_reg_test
    )
    
    # 7. Save models and results
    save_training_results(
        classifier, regressor, scaler, metrics,
        output_dir=args.output
    )
    
    return metrics
```

### 3. Model Validation: `validate_models.py`

**Purpose**: Comprehensive validation of trained models.

```bash
# Validate latest models
python scripts/validate_models.py --models models/

# Validate specific model version
python scripts/validate_models.py \
    --models models/ \
    --version 20251102_143000 \
    --test-data data/validation_set.csv
```

#### Validation Tests

```python
def run_validation_suite(models_dir, test_data=None):
    """Complete model validation suite."""
    
    results = {}
    
    # 1. Model Loading Test
    try:
        models = load_trained_models(models_dir)
        results['loading'] = 'PASS'
    except Exception as e:
        results['loading'] = f'FAIL: {e}'
        return results
    
    # 2. Prediction Test
    try:
        # Test with sample features
        sample_features = generate_sample_features()
        class_pred = models['classifier'].predict([sample_features])
        reg_pred = models['regressor'].predict([sample_features])
        results['prediction'] = 'PASS'
    except Exception as e:
        results['prediction'] = f'FAIL: {e}'
    
    # 3. Performance Test
    try:
        # Test inference speed
        speed_test = test_inference_speed(models, n_samples=100)
        if speed_test['avg_time_ms'] < 100:
            results['performance'] = 'PASS'
        else:
            results['performance'] = f'FAIL: {speed_test["avg_time_ms"]}ms > 100ms'
    except Exception as e:
        results['performance'] = f'FAIL: {e}'
    
    # 4. Accuracy Test (if test data provided)
    if test_data:
        try:
            accuracy_test = test_model_accuracy(models, test_data)
            results['accuracy'] = accuracy_test
        except Exception as e:
            results['accuracy'] = f'FAIL: {e}'
    
    return results
```

### 4. Feature Analysis: `analyze_features.py`

**Purpose**: Analyze feature importance and model behavior.

```bash
# Analyze feature importance
python scripts/analyze_features.py \
    --models models/ \
    --data data/synthetic_training_data.csv \
    --output analysis/

# Generate feature importance plots
python scripts/analyze_features.py \
    --models models/ \
    --plot-importance \
    --plot-correlations \
    --export-report
```

#### Analysis Features

```python
def feature_importance_analysis(classifier, regressor, feature_names):
    """Analyze feature importance for both models."""
    
    # Classifier feature importance
    clf_importance = classifier.feature_importances_
    clf_importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': clf_importance
    }).sort_values('importance', ascending=False)
    
    # Regressor feature importance
    reg_importance = regressor.feature_importances_
    reg_importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': reg_importance
    }).sort_values('importance', ascending=False)
    
    # Combined analysis
    combined_importance = (clf_importance + reg_importance) / 2
    combined_df = pd.DataFrame({
        'feature': feature_names,
        'classifier_importance': clf_importance,
        'regressor_importance': reg_importance,
        'combined_importance': combined_importance
    }).sort_values('combined_importance', ascending=False)
    
    return {
        'classifier': clf_importance_df,
        'regressor': reg_importance_df,
        'combined': combined_df
    }
```

### 5. Model Deployment: `deploy_models.py`

**Purpose**: Deploy trained models to production environment.

```bash
# Deploy to staging
python scripts/deploy_models.py \
    --source models/ \
    --target staging \
    --version latest

# Deploy to production with validation
python scripts/deploy_models.py \
    --source models/ \
    --target production \
    --version 20251102_143000 \
    --validate \
    --backup-existing
```

#### Deployment Process

```python
def deploy_models(source_dir, target_env, version='latest', validate=True):
    """Deploy models to target environment."""
    
    deployment_log = []
    
    try:
        # 1. Validate source models
        if validate:
            validation_results = validate_models(source_dir, version)
            if not all(result == 'PASS' for result in validation_results.values()):
                raise DeploymentError(f"Model validation failed: {validation_results}")
            deployment_log.append("✅ Model validation passed")
        
        # 2. Backup existing models (if any)
        if target_env == 'production':
            backup_existing_models()
            deployment_log.append("✅ Existing models backed up")
        
        # 3. Copy models to target
        copy_models_to_target(source_dir, target_env, version)
        deployment_log.append("✅ Models copied to target")
        
        # 4. Update symbolic links
        update_model_links(target_env, version)
        deployment_log.append("✅ Model links updated")
        
        # 5. Test deployment
        test_deployment(target_env)
        deployment_log.append("✅ Deployment test passed")
        
        # 6. Update deployment metadata
        update_deployment_metadata(target_env, version)
        deployment_log.append("✅ Deployment metadata updated")
        
        return {
            'status': 'SUCCESS',
            'version': version,
            'environment': target_env,
            'log': deployment_log
        }
        
    except Exception as e:
        deployment_log.append(f"❌ Deployment failed: {e}")
        
        # Rollback on failure
        if target_env == 'production':
            rollback_deployment()
            deployment_log.append("✅ Rollback completed")
        
        return {
            'status': 'FAILED',
            'error': str(e),
            'log': deployment_log
        }
```

## Training Workflow

### Development Workflow

```bash
# 1. Generate training data
python scripts/generate_synthetic_data.py --size 5000 --validate

# 2. Train models with hyperparameter tuning
python scripts/train_xgboost_models.py \
    --data data/synthetic_training_data.csv \
    --tune-hyperparams \
    --cv-folds 5

# 3. Validate trained models
python scripts/validate_models.py --models models/

# 4. Analyze feature importance
python scripts/analyze_features.py \
    --models models/ \
    --data data/synthetic_training_data.csv \
    --plot-importance

# 5. Deploy to staging
python scripts/deploy_models.py \
    --source models/ \
    --target staging \
    --validate
```

### Production Workflow

```bash
# 1. Generate larger training dataset
python scripts/generate_synthetic_data.py --size 10000 --validate

# 2. Train production models
python scripts/train_xgboost_models.py \
    --data data/synthetic_training_data.csv \
    --tune-hyperparams \
    --cv-folds 10 \
    --gpu

# 3. Comprehensive validation
python scripts/validate_models.py \
    --models models/ \
    --test-data data/validation_set.csv

# 4. Deploy to production
python scripts/deploy_models.py \
    --source models/ \
    --target production \
    --validate \
    --backup-existing
```

## Configuration Files

### Training Configuration: `config/training.yaml`

```yaml
# Training configuration
training:
  data:
    size: 5000
    validation_split: 0.2
    random_state: 42
  
  preprocessing:
    scaling: 'standard'
    feature_selection: false
  
  models:
    classifier:
      objective: 'multi:softprob'
      learning_rate: 0.1
      max_depth: 6
      n_estimators: 100
      reg_alpha: 0.1
      reg_lambda: 1.0
    
    regressor:
      objective: 'reg:squarederror'
      learning_rate: 0.1
      max_depth: 6
      n_estimators: 100
      reg_alpha: 0.1
      reg_lambda: 1.0
  
  tuning:
    method: 'grid_search'  # or 'bayesian'
    cv_folds: 5
    n_iter: 50  # for bayesian
  
  output:
    model_dir: 'models/'
    backup_models: true
    export_metrics: true
```

### Environment Configuration: `config/environments.yaml`

```yaml
# Environment configuration
environments:
  development:
    model_dir: 'models/dev/'
    validation_required: false
    backup_enabled: false
  
  staging:
    model_dir: 'models/staging/'
    validation_required: true
    backup_enabled: true
    performance_threshold:
      latency_ms: 100
      accuracy_min: 0.7
  
  production:
    model_dir: 'models/prod/'
    validation_required: true
    backup_enabled: true
    rollback_enabled: true
    performance_threshold:
      latency_ms: 50
      accuracy_min: 0.8
    monitoring:
      enabled: true
      alert_threshold: 0.05  # 5% accuracy drop
```

## Troubleshooting

### Common Issues

#### 1. Training Data Issues

```bash
# Error: Invalid feature dimensions
# Solution: Validate data generation
python scripts/generate_synthetic_data.py --validate

# Error: Missing target values
# Solution: Check CSV format
head -n 5 data/synthetic_training_data.csv
```

#### 2. Model Training Failures

```bash
# Error: Out of memory during training
# Solution: Reduce dataset size or use GPU
python scripts/train_xgboost_models.py --data data/small_dataset.csv --gpu

# Error: Convergence issues
# Solution: Adjust learning rate
python scripts/train_xgboost_models.py --learning-rate 0.05
```

#### 3. Deployment Issues

```bash
# Error: Model validation failed
# Solution: Check model files
python scripts/validate_models.py --models models/ --verbose

# Error: Permission denied during deployment
# Solution: Check file permissions
chmod +x scripts/deploy_models.py
```

### Debug Mode

```bash
# Enable debug logging for all scripts
export PYTHONPATH=.
export LOG_LEVEL=DEBUG

# Run with verbose output
python scripts/train_xgboost_models.py --verbose --debug
```

This documentation provides comprehensive guidance for using all training scripts in the XGBoost pipeline.
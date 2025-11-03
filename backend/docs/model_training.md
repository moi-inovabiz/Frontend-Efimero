# XGBoost Model Training Documentation

## Overview

This document describes the complete XGBoost model training pipeline for the Frontend Efímero adaptive UI system. The training process uses dual models (Classifier + Regressor) to predict CSS design tokens based on user context features.

## Training Architecture

### Dual Model Approach

The system employs two complementary XGBoost models:

1. **XGBoost Classifier**: Predicts discrete CSS classes
   - **Input**: 19 numerical features from user context
   - **Output**: CSS class probabilities (density, font, theme categories)
   - **Target**: Categorical labels like `['densidad-alta', 'fuente-serif', 'tema-oscuro']`

2. **XGBoost Regressor**: Predicts continuous CSS variable values
   - **Input**: Same 19 numerical features
   - **Output**: Numerical CSS values (font sizes, spacing, colors)
   - **Target**: Continuous values like `[1.15, 24, 0.8, ...]` for CSS variables

### Training Data Structure

```python
# Training dataset schema
{
    "features": np.ndarray,      # Shape: (n_samples, 19)
    "css_classes": np.ndarray,   # Shape: (n_samples, 3) - categorical
    "css_variables": np.ndarray, # Shape: (n_samples, 8) - continuous
    "metadata": {
        "feature_names": List[str],      # 19 feature names
        "class_labels": List[str],       # CSS class categories
        "variable_names": List[str],     # CSS variable names
        "generation_date": datetime,
        "dataset_size": int
    }
}
```

## Data Generation Pipeline

### Synthetic Dataset Creation

**Script**: `scripts/generate_synthetic_data.py`

```python
def generate_comprehensive_dataset(size: int = 1000) -> Dict[str, Any]:
    """
    Generate synthetic training data with realistic user patterns.
    
    Args:
        size: Number of samples to generate
        
    Returns:
        Complete dataset with features and targets
    """
```

#### User Pattern Simulation

The data generator creates diverse user scenarios:

1. **Temporal Patterns**:
   - Business hours bias (9AM-6PM weekdays)
   - Evening mobile usage spikes
   - Weekend behavior variations

2. **Device Distributions**:
   - 60% mobile users (viewport < 768px)
   - 25% desktop users (viewport > 1024px)
   - 15% tablet users (768-1024px)

3. **Behavioral Correlations**:
   - Mobile users → compact UI preferences
   - Desktop power users → dense information layouts
   - Evening users → dark theme preference
   - High-resolution displays → detailed interfaces

#### Feature-Target Relationships

```python
# Example correlation rules
def generate_css_targets(features: np.ndarray) -> Tuple[List[str], List[float]]:
    """Generate realistic CSS targets based on features."""
    
    # Device-based rules
    if features[4] == 1.0:  # is_mobile
        density = "densidad-baja"
        font_size_base = 1.0  # Smaller for mobile
    elif features[6] == 1.0:  # is_desktop
        density = "densidad-alta"
        font_size_base = 1.15  # Larger for desktop
    
    # Time-based rules
    if features[0] >= 18 or features[0] <= 6:  # Evening/night
        theme = "tema-oscuro"
        color_brightness = 0.3
    else:
        theme = "tema-claro"
        color_brightness = 0.8
    
    # High-resolution adjustments
    if features[8] >= 2.0:  # device_pixel_ratio
        font_size_base *= 1.1
        spacing_base = 20
    
    return css_classes, css_variables
```

### Data Validation

```python
def validate_training_data(dataset: Dict[str, Any]) -> bool:
    """Comprehensive dataset validation."""
    
    features = dataset["features"]
    css_classes = dataset["css_classes"]
    css_variables = dataset["css_variables"]
    
    # Shape validation
    assert features.shape[1] == 19, f"Expected 19 features, got {features.shape[1]}"
    assert css_classes.shape[1] == 3, f"Expected 3 class categories, got {css_classes.shape[1]}"
    assert css_variables.shape[1] == 8, f"Expected 8 variables, got {css_variables.shape[1]}"
    
    # Feature quality checks
    assert np.isfinite(features).all(), "Features contain NaN/Inf values"
    assert (features[:, 0] >= 0).all() and (features[:, 0] <= 23).all(), "Invalid hour_of_day"
    assert np.all(np.isin(features[:, 1:8], [0.0, 1.0])), "Binary features not binary"
    
    # Target validation
    valid_classes = ['densidad-baja', 'densidad-media', 'densidad-alta',
                     'fuente-sans', 'fuente-serif', 'fuente-mono',
                     'tema-claro', 'tema-oscuro', 'tema-auto']
    for class_set in css_classes:
        assert all(cls in valid_classes for cls in class_set), "Invalid CSS class"
    
    assert css_variables.min() >= 0, "CSS variables contain negative values"
    assert css_variables.max() <= 100, "CSS variables exceed reasonable range"
    
    return True
```

## Model Training Pipeline

### Training Script

**Script**: `scripts/train_xgboost_models.py`

```python
def train_dual_models(
    dataset_path: str,
    output_dir: str = "models/",
    test_size: float = 0.2,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Complete dual model training pipeline.
    
    Args:
        dataset_path: Path to training dataset
        output_dir: Directory to save trained models
        test_size: Fraction for test split
        random_state: Random seed for reproducibility
        
    Returns:
        Training results and metrics
    """
```

### Hyperparameter Configuration

#### XGBoost Classifier Parameters

```python
classifier_params = {
    # Core parameters
    'objective': 'multi:softprob',     # Multi-class classification
    'num_class': 9,                    # 3 categories × 3 options each
    'eval_metric': 'mlogloss',         # Multi-class log loss
    
    # Learning parameters
    'learning_rate': 0.1,              # Conservative learning
    'max_depth': 6,                    # Moderate depth for generalization
    'min_child_weight': 1,             # Minimum samples per leaf
    'subsample': 0.8,                  # Row sampling for regularization
    'colsample_bytree': 0.8,           # Feature sampling
    
    # Regularization
    'reg_alpha': 0.1,                  # L1 regularization
    'reg_lambda': 1.0,                 # L2 regularization
    
    # Performance
    'n_estimators': 100,               # Number of trees
    'random_state': 42,                # Reproducibility
    'n_jobs': -1,                      # Use all CPU cores
    'verbosity': 1                     # Moderate logging
}
```

#### XGBoost Regressor Parameters

```python
regressor_params = {
    # Core parameters
    'objective': 'reg:squarederror',   # Regression with MSE
    'eval_metric': 'rmse',             # Root mean squared error
    
    # Learning parameters
    'learning_rate': 0.1,              # Same as classifier
    'max_depth': 6,                    # Consistent depth
    'min_child_weight': 1,             # Minimum samples per leaf
    'subsample': 0.8,                  # Row sampling
    'colsample_bytree': 0.8,           # Feature sampling
    
    # Regularization
    'reg_alpha': 0.1,                  # L1 regularization
    'reg_lambda': 1.0,                 # L2 regularization
    
    # Performance
    'n_estimators': 100,               # Number of trees
    'random_state': 42,                # Reproducibility
    'n_jobs': -1,                      # Use all CPU cores
    'verbosity': 1                     # Moderate logging
}
```

### Hyperparameter Tuning

#### Grid Search Configuration

```python
def hyperparameter_tuning(X_train, y_train, model_type='classifier'):
    """Systematic hyperparameter optimization."""
    
    if model_type == 'classifier':
        param_grid = {
            'learning_rate': [0.05, 0.1, 0.15],
            'max_depth': [4, 6, 8],
            'n_estimators': [50, 100, 150],
            'subsample': [0.7, 0.8, 0.9],
            'reg_alpha': [0.0, 0.1, 0.2]
        }
        scoring = 'neg_log_loss'
    else:  # regressor
        param_grid = {
            'learning_rate': [0.05, 0.1, 0.15],
            'max_depth': [4, 6, 8],
            'n_estimators': [50, 100, 150],
            'subsample': [0.7, 0.8, 0.9],
            'reg_alpha': [0.0, 0.1, 0.2]
        }
        scoring = 'neg_mean_squared_error'
    
    # Grid search with cross-validation
    grid_search = GridSearchCV(
        estimator=create_base_model(model_type),
        param_grid=param_grid,
        cv=5,                    # 5-fold cross-validation
        scoring=scoring,         # Optimization metric
        n_jobs=-1,              # Parallel processing
        verbose=1               # Progress tracking
    )
    
    return grid_search.fit(X_train, y_train)
```

#### Bayesian Optimization (Advanced)

```python
from skopt import BayesSearchCV
from skopt.space import Real, Integer

def bayesian_optimization(X_train, y_train, model_type='classifier'):
    """Advanced hyperparameter optimization using Bayesian methods."""
    
    search_spaces = {
        'learning_rate': Real(0.01, 0.3, prior='log-uniform'),
        'max_depth': Integer(3, 10),
        'n_estimators': Integer(50, 300),
        'subsample': Real(0.6, 1.0),
        'colsample_bytree': Real(0.6, 1.0),
        'reg_alpha': Real(0.0, 1.0),
        'reg_lambda': Real(0.0, 2.0)
    }
    
    bayes_search = BayesSearchCV(
        estimator=create_base_model(model_type),
        search_spaces=search_spaces,
        n_iter=50,              # Number of iterations
        cv=5,                   # Cross-validation folds
        n_jobs=-1,              # Parallel processing
        random_state=42         # Reproducibility
    )
    
    return bayes_search.fit(X_train, y_train)
```

## Model Evaluation

### Validation Metrics

#### Classification Metrics

```python
def evaluate_classifier(model, X_test, y_test, class_names):
    """Comprehensive classifier evaluation."""
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Core metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    # Multi-class specific
    log_loss_score = log_loss(y_test, y_pred_proba)
    
    # Per-class metrics
    classification_rep = classification_report(
        y_test, y_pred, 
        target_names=class_names,
        output_dict=True
    )
    
    # Confusion matrix
    conf_matrix = confusion_matrix(y_test, y_pred)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'log_loss': log_loss_score,
        'classification_report': classification_rep,
        'confusion_matrix': conf_matrix.tolist()
    }
```

#### Regression Metrics

```python
def evaluate_regressor(model, X_test, y_test, variable_names):
    """Comprehensive regressor evaluation."""
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Core metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Per-variable metrics
    per_variable_metrics = {}
    for i, var_name in enumerate(variable_names):
        per_variable_metrics[var_name] = {
            'mse': mean_squared_error(y_test[:, i], y_pred[:, i]),
            'mae': mean_absolute_error(y_test[:, i], y_pred[:, i]),
            'r2': r2_score(y_test[:, i], y_pred[:, i])
        }
    
    # Explained variance
    explained_variance = explained_variance_score(y_test, y_pred)
    
    return {
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
        'r2_score': r2,
        'explained_variance': explained_variance,
        'per_variable_metrics': per_variable_metrics
    }
```

### Cross-Validation

```python
def cross_validate_models(X, y_class, y_reg, cv_folds=5):
    """Robust cross-validation for both models."""
    
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    from sklearn.multioutput import MultiOutputRegressor
    
    # Stratified k-fold for classification
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    
    # Classifier cross-validation
    classifier = create_classifier()
    clf_scores = cross_val_score(
        classifier, X, y_class, 
        cv=skf, 
        scoring='accuracy',
        n_jobs=-1
    )
    
    # Regressor cross-validation
    regressor = MultiOutputRegressor(create_regressor())
    reg_scores = cross_val_score(
        regressor, X, y_reg,
        cv=cv_folds,
        scoring='neg_mean_squared_error',
        n_jobs=-1
    )
    
    return {
        'classifier': {
            'mean_accuracy': clf_scores.mean(),
            'std_accuracy': clf_scores.std(),
            'scores': clf_scores.tolist()
        },
        'regressor': {
            'mean_rmse': np.sqrt(-reg_scores.mean()),
            'std_rmse': np.sqrt(reg_scores.std()),
            'scores': (-reg_scores).tolist()
        }
    }
```

## Model Serialization

### Saving Trained Models

```python
import joblib
from datetime import datetime
import json

def save_models(classifier, regressor, scaler, metadata, output_dir="models/"):
    """Save trained models with metadata."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save models
    joblib.dump(classifier, f"{output_dir}/xgboost_classifier_{timestamp}.joblib")
    joblib.dump(regressor, f"{output_dir}/xgboost_regressor_{timestamp}.joblib")
    joblib.dump(scaler, f"{output_dir}/feature_scaler_{timestamp}.joblib")
    
    # Save metadata
    metadata_with_timestamp = {
        **metadata,
        'training_date': datetime.now().isoformat(),
        'model_version': timestamp,
        'xgboost_version': xgb.__version__,
        'sklearn_version': sklearn.__version__
    }
    
    with open(f"{output_dir}/model_metadata_{timestamp}.json", 'w') as f:
        json.dump(metadata_with_timestamp, f, indent=2)
    
    # Create symbolic links for latest models
    create_latest_links(timestamp, output_dir)
    
    return timestamp

def create_latest_links(timestamp, output_dir):
    """Create symbolic links to latest models."""
    import os
    
    latest_files = [
        ('xgboost_classifier.joblib', f'xgboost_classifier_{timestamp}.joblib'),
        ('xgboost_regressor.joblib', f'xgboost_regressor_{timestamp}.joblib'),
        ('feature_scaler.joblib', f'feature_scaler_{timestamp}.joblib'),
        ('model_metadata.json', f'model_metadata_{timestamp}.json')
    ]
    
    for latest_name, versioned_name in latest_files:
        latest_path = os.path.join(output_dir, latest_name)
        versioned_path = os.path.join(output_dir, versioned_name)
        
        # Remove existing link if it exists
        if os.path.exists(latest_path):
            os.remove(latest_path)
        
        # Create new symbolic link
        os.symlink(versioned_name, latest_path)
```

### Model Loading

```python
def load_trained_models(model_dir="models/", use_latest=True):
    """Load trained models for inference."""
    
    if use_latest:
        classifier_path = f"{model_dir}/xgboost_classifier.joblib"
        regressor_path = f"{model_dir}/xgboost_regressor.joblib"
        scaler_path = f"{model_dir}/feature_scaler.joblib"
        metadata_path = f"{model_dir}/model_metadata.json"
    else:
        # Load specific version
        # Implementation for version selection
        pass
    
    try:
        classifier = joblib.load(classifier_path)
        regressor = joblib.load(regressor_path)
        scaler = joblib.load(scaler_path)
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        return {
            'classifier': classifier,
            'regressor': regressor,
            'scaler': scaler,
            'metadata': metadata
        }
    
    except FileNotFoundError as e:
        raise ModelLoadError(f"Model files not found: {e}")
    except Exception as e:
        raise ModelLoadError(f"Error loading models: {e}")
```

## Training Performance Optimization

### Memory Optimization

```python
def optimize_training_memory(dataset_size):
    """Configure XGBoost for optimal memory usage."""
    
    if dataset_size < 1000:
        # Small dataset - can load everything
        return {
            'tree_method': 'exact',
            'max_bin': 256
        }
    elif dataset_size < 10000:
        # Medium dataset - moderate optimization
        return {
            'tree_method': 'hist',
            'max_bin': 128,
            'max_delta_step': 1
        }
    else:
        # Large dataset - aggressive optimization
        return {
            'tree_method': 'hist',
            'max_bin': 64,
            'max_delta_step': 2,
            'sketch_eps': 0.1
        }
```

### GPU Acceleration

```python
def configure_gpu_training():
    """Configure XGBoost for GPU acceleration if available."""
    
    try:
        import cupy
        gpu_available = True
    except ImportError:
        gpu_available = False
    
    if gpu_available:
        return {
            'tree_method': 'gpu_hist',
            'gpu_id': 0,
            'predictor': 'gpu_predictor'
        }
    else:
        return {
            'tree_method': 'hist',
            'n_jobs': -1
        }
```

### Distributed Training

```python
def setup_distributed_training(n_workers=4):
    """Configure distributed XGBoost training."""
    
    return {
        'n_jobs': n_workers,
        'verbosity': 1,
        'enable_categorical': True,
        'use_label_encoder': False
    }
```

## Model Validation Pipeline

### Training Pipeline Validation

```python
def validate_training_pipeline():
    """End-to-end training pipeline validation."""
    
    # 1. Generate small synthetic dataset
    dataset = generate_comprehensive_dataset(size=100)
    
    # 2. Validate dataset
    assert validate_training_data(dataset)
    
    # 3. Train models
    results = train_dual_models(dataset)
    
    # 4. Validate trained models
    assert results['classifier'] is not None
    assert results['regressor'] is not None
    assert results['metrics']['classifier']['accuracy'] > 0.5
    assert results['metrics']['regressor']['r2_score'] > 0.3
    
    # 5. Test serialization
    timestamp = save_models(
        results['classifier'],
        results['regressor'],
        results['scaler'],
        results['metadata']
    )
    
    # 6. Test loading
    loaded_models = load_trained_models()
    assert loaded_models['metadata']['model_version'] == timestamp
    
    print("✅ Training pipeline validation successful")
    return True
```

## Best Practices

### Data Quality

1. **Feature Consistency**: Ensure features match training schema exactly
2. **Target Alignment**: Verify CSS targets represent realistic design choices
3. **Temporal Balance**: Include data from different time periods
4. **Device Distribution**: Maintain realistic device type proportions

### Model Performance

1. **Regularization**: Use appropriate L1/L2 to prevent overfitting
2. **Early Stopping**: Monitor validation loss to stop training optimally
3. **Feature Importance**: Analyze which features drive predictions
4. **Cross-Validation**: Always validate with unseen data

### Production Readiness

1. **Version Control**: Track all model versions and metadata
2. **Reproducibility**: Fix random seeds and document environment
3. **Monitoring**: Plan for model performance tracking in production
4. **Rollback**: Maintain previous model versions for safety

---

This documentation provides a comprehensive guide to the XGBoost training pipeline. For implementation details, see the training scripts in the `scripts/` directory.
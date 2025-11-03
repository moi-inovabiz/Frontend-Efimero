# Retraining Scripts

## Overview

This document describes the automated scripts for model retraining, including data collection, validation, training, and deployment.

## Script Reference

### 1. Data Collection: `collect_production_data.py`

**Purpose**: Collect and prepare production data for retraining.

```bash
# Collect data from last 7 days
python scripts/collect_production_data.py \
    --start-date "2025-10-26" \
    --end-date "2025-11-02" \
    --output data/production_data.csv

# Collect with filtering and validation
python scripts/collect_production_data.py \
    --days-back 30 \
    --min-session-duration 30000 \
    --validate \
    --export-metadata
```

#### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--start-date` | str | 7 days ago | Start date (YYYY-MM-DD) |
| `--end-date` | str | Today | End date (YYYY-MM-DD) |
| `--days-back` | int | 7 | Days to collect (alternative to dates) |
| `--output` | str | `data/production_data.csv` | Output file path |
| `--min-session-duration` | int | 10000 | Minimum session duration (ms) |
| `--validate` | flag | False | Validate collected data |
| `--export-metadata` | flag | False | Export collection metadata |

#### Implementation

```python
#!/usr/bin/env python3
"""
Production Data Collection Script
Collects user interaction data from Firebase for model retraining.
"""

import argparse
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.core.config import settings
from app.services.firebase_service import FirebaseService
from app.ml.feature_processor import FeatureProcessor

class ProductionDataCollector:
    def __init__(self):
        self.firebase = FirebaseService()
        self.feature_processor = FeatureProcessor()
        
    async def collect_data(
        self, 
        start_date: datetime, 
        end_date: datetime,
        min_session_duration: int = 10000
    ) -> pd.DataFrame:
        """Collect production interaction data."""
        
        print(f"Collecting data from {start_date} to {end_date}")
        
        # Query interaction logs
        logs = await self.firebase.query_collection(
            collection='interaction_logs',
            filters=[
                ('timestamp', '>=', start_date),
                ('timestamp', '<=', end_date),
                ('session_duration', '>=', min_session_duration)
            ]
        )
        
        print(f"Found {len(logs)} interaction logs")
        
        # Process logs into training format
        training_data = []
        
        for log in logs:
            try:
                # Extract features
                user_context = self._parse_user_context(log)
                features = self.feature_processor.prepare_features_v2(user_context)
                
                # Infer optimal targets from behavior
                css_classes, css_variables = self._infer_targets_from_behavior(log)
                
                # Combine into training row
                row = {
                    **{f'feature_{i}': features[i] for i in range(19)},
                    'css_class_density': css_classes[0],
                    'css_class_font': css_classes[1], 
                    'css_class_theme': css_classes[2],
                    **{f'css_var_{i}': css_variables[i] for i in range(8)}
                }
                
                training_data.append(row)
                
            except Exception as e:
                print(f"Error processing log: {e}")
                continue
        
        df = pd.DataFrame(training_data)
        print(f"Successfully processed {len(df)} samples")
        
        return df

def main():
    parser = argparse.ArgumentParser(description='Collect production data for retraining')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--days-back', type=int, default=7, help='Days to collect')
    parser.add_argument('--output', type=str, default='data/production_data.csv')
    parser.add_argument('--min-session-duration', type=int, default=10000)
    parser.add_argument('--validate', action='store_true')
    parser.add_argument('--export-metadata', action='store_true')
    
    args = parser.parse_args()
    
    # Calculate date range
    if args.start_date and args.end_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days_back)
    
    # Collect data
    collector = ProductionDataCollector()
    df = asyncio.run(collector.collect_data(start_date, end_date, args.min_session_duration))
    
    # Save data
    df.to_csv(args.output, index=False)
    print(f"Data saved to {args.output}")
    
    # Validation
    if args.validate:
        validation_results = collector.validate_data(df)
        print(f"Validation results: {validation_results}")
    
    # Export metadata
    if args.export_metadata:
        metadata = {
            'collection_date': datetime.now().isoformat(),
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_samples': len(df),
            'min_session_duration': args.min_session_duration
        }
        
        metadata_path = args.output.replace('.csv', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

if __name__ == '__main__':
    main()
```

### 2. Incremental Retraining: `incremental_retrain.py`

**Purpose**: Perform incremental model updates with new data.

```bash
# Basic incremental retraining
python scripts/incremental_retrain.py \
    --data data/production_data.csv \
    --models models/

# Advanced incremental retraining
python scripts/incremental_retrain.py \
    --data data/production_data.csv \
    --models models/ \
    --min-samples 100 \
    --validation-split 0.2 \
    --backup-current
```

#### Implementation

```python
#!/usr/bin/env python3
"""
Incremental Model Retraining Script
Updates existing models with new production data.
"""

import argparse
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from sklearn.metrics import accuracy_score, mean_squared_error

class IncrementalRetrainer:
    def __init__(self, models_dir: str):
        self.models_dir = models_dir
        self.min_improvement_threshold = 0.01  # 1% minimum improvement
        
    def retrain(self, new_data: pd.DataFrame, min_samples: int = 100) -> Dict[str, Any]:
        """Perform incremental retraining."""
        
        if len(new_data) < min_samples:
            return {
                'status': 'skipped',
                'reason': f'Insufficient data: {len(new_data)} < {min_samples}'
            }
        
        # Load current models
        current_models = self._load_current_models()
        
        # Prepare new training data
        X_new, y_class_new, y_reg_new = self._prepare_training_data(new_data)
        
        # Incremental training
        updated_classifier = self._update_classifier(
            current_models['classifier'], X_new, y_class_new
        )
        
        updated_regressor = self._update_regressor(
            current_models['regressor'], X_new, y_reg_new
        )
        
        # Validation
        validation_results = self._validate_updated_models(
            updated_classifier, updated_regressor, X_new, y_class_new, y_reg_new
        )
        
        if validation_results['improvement_significant']:
            # Save updated models
            timestamp = self._save_updated_models(
                updated_classifier, updated_regressor, current_models['scaler']
            )
            
            return {
                'status': 'success',
                'model_version': timestamp,
                'validation_results': validation_results,
                'samples_used': len(new_data)
            }
        else:
            return {
                'status': 'no_improvement',
                'validation_results': validation_results
            }
    
    def _update_classifier(self, current_classifier, X_new, y_new):
        """Update classifier with new data using warm start."""
        
        # Create updated classifier with more trees
        updated_classifier = XGBClassifier(
            **current_classifier.get_params(),
            n_estimators=current_classifier.n_estimators + 20,
            warm_start=True
        )
        
        # Fit on new data
        updated_classifier.fit(X_new, y_new)
        
        return updated_classifier

def main():
    parser = argparse.ArgumentParser(description='Incremental model retraining')
    parser.add_argument('--data', type=str, required=True, help='New training data CSV')
    parser.add_argument('--models', type=str, default='models/', help='Models directory')
    parser.add_argument('--min-samples', type=int, default=100, help='Minimum samples for retraining')
    parser.add_argument('--validation-split', type=float, default=0.2, help='Validation split')
    parser.add_argument('--backup-current', action='store_true', help='Backup current models')
    
    args = parser.parse_args()
    
    # Load new data
    new_data = pd.read_csv(args.data)
    print(f"Loaded {len(new_data)} new samples")
    
    # Backup current models if requested
    if args.backup_current:
        backup_models(args.models)
        print("Current models backed up")
    
    # Incremental retraining
    retrainer = IncrementalRetrainer(args.models)
    results = retrainer.retrain(new_data, args.min_samples)
    
    print(f"Retraining results: {results}")

if __name__ == '__main__':
    main()
```

### 3. Full Retraining: `full_retrain.py`

**Purpose**: Complete model retraining from scratch.

```bash
# Full retraining with hyperparameter tuning
python scripts/full_retrain.py \
    --data data/combined_training_data.csv \
    --output models/retrained/ \
    --tune-hyperparams \
    --cv-folds 5

# Production retraining
python scripts/full_retrain.py \
    --data data/production_training_data.csv \
    --output models/prod/ \
    --compare-with-current \
    --deploy-if-better
```

### 4. Model Comparison: `compare_models.py`

**Purpose**: Compare model performance across versions.

```bash
# Compare two model versions
python scripts/compare_models.py \
    --model-a models/current/ \
    --model-b models/retrained/ \
    --test-data data/validation_set.csv

# Comprehensive comparison with plots
python scripts/compare_models.py \
    --model-a models/v_20251101_120000/ \
    --model-b models/v_20251102_143000/ \
    --test-data data/validation_set.csv \
    --generate-plots \
    --export-report
```

### 5. Automated Retraining: `auto_retrain.py`

**Purpose**: Automated retraining pipeline with scheduling.

```bash
# Run automated retraining check
python scripts/auto_retrain.py --mode check

# Force retraining
python scripts/auto_retrain.py --mode force

# Setup cron job for automated retraining
# 0 2 * * 1 cd /path/to/project && python scripts/auto_retrain.py --mode scheduled
```

#### Implementation

```python
#!/usr/bin/env python3
"""
Automated Retraining Pipeline
Handles scheduled and triggered model retraining.
"""

import argparse
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

class AutomatedRetrainer:
    def __init__(self):
        self.retraining_config = self._load_retraining_config()
        
    def _load_retraining_config(self) -> Dict[str, Any]:
        """Load retraining configuration."""
        return {
            'min_days_since_last_training': 7,
            'min_new_samples': 500,
            'performance_threshold': 0.75,
            'max_performance_drop': 0.05,
            'enable_auto_deployment': False
        }
    
    async def check_retraining_needed(self) -> Dict[str, Any]:
        """Check if retraining is needed based on various criteria."""
        
        checks = {
            'time_based': self._check_time_based_trigger(),
            'data_volume': await self._check_data_volume_trigger(),
            'performance': await self._check_performance_trigger(),
            'drift': await self._check_drift_trigger()
        }
        
        # Determine if retraining should be triggered
        should_retrain = any([
            checks['time_based']['triggered'],
            checks['data_volume']['triggered'],
            checks['performance']['triggered'],
            checks['drift']['triggered']
        ])
        
        return {
            'should_retrain': should_retrain,
            'triggers': checks,
            'recommendation': self._generate_recommendation(checks)
        }
    
    async def run_automated_retraining(self) -> Dict[str, Any]:
        """Run the complete automated retraining pipeline."""
        
        pipeline_results = {
            'start_time': datetime.now().isoformat(),
            'stages': {}
        }
        
        try:
            # Stage 1: Check if retraining is needed
            retraining_check = await self.check_retraining_needed()
            pipeline_results['stages']['check'] = retraining_check
            
            if not retraining_check['should_retrain']:
                pipeline_results['status'] = 'skipped'
                pipeline_results['reason'] = 'No retraining triggers activated'
                return pipeline_results
            
            # Stage 2: Collect production data
            data_collection = await self._collect_production_data()
            pipeline_results['stages']['data_collection'] = data_collection
            
            if data_collection['status'] != 'success':
                raise Exception(f"Data collection failed: {data_collection['error']}")
            
            # Stage 3: Validate data quality
            data_validation = await self._validate_collected_data(data_collection['data_path'])
            pipeline_results['stages']['data_validation'] = data_validation
            
            if data_validation['recommendation'] == 'abort':
                raise Exception(f"Data quality issues: {data_validation['issues']}")
            
            # Stage 4: Determine retraining strategy
            strategy = self._determine_retraining_strategy(retraining_check['triggers'])
            pipeline_results['stages']['strategy'] = {'strategy': strategy}
            
            # Stage 5: Execute retraining
            if strategy == 'incremental':
                retraining_results = await self._run_incremental_retraining(data_collection['data_path'])
            else:
                retraining_results = await self._run_full_retraining(data_collection['data_path'])
            
            pipeline_results['stages']['retraining'] = retraining_results
            
            if retraining_results['status'] != 'success':
                raise Exception(f"Retraining failed: {retraining_results['error']}")
            
            # Stage 6: Model validation
            validation_results = await self._validate_retrained_models(retraining_results['model_version'])
            pipeline_results['stages']['validation'] = validation_results
            
            if not validation_results['performance_acceptable']:
                raise Exception(f"Model validation failed: {validation_results['issues']}")
            
            # Stage 7: Deployment (if enabled)
            if self.retraining_config['enable_auto_deployment']:
                deployment_results = await self._deploy_retrained_models(retraining_results['model_version'])
                pipeline_results['stages']['deployment'] = deployment_results
            else:
                pipeline_results['stages']['deployment'] = {'status': 'skipped', 'reason': 'Auto-deployment disabled'}
            
            pipeline_results['status'] = 'success'
            pipeline_results['model_version'] = retraining_results['model_version']
            
        except Exception as e:
            pipeline_results['status'] = 'failed'
            pipeline_results['error'] = str(e)
            
            # Cleanup on failure
            await self._cleanup_failed_retraining()
        
        finally:
            pipeline_results['end_time'] = datetime.now().isoformat()
            pipeline_results['duration_minutes'] = (
                datetime.fromisoformat(pipeline_results['end_time']) - 
                datetime.fromisoformat(pipeline_results['start_time'])
            ).total_seconds() / 60
        
        return pipeline_results

def main():
    parser = argparse.ArgumentParser(description='Automated model retraining')
    parser.add_argument('--mode', choices=['check', 'force', 'scheduled'], default='check')
    parser.add_argument('--config', type=str, help='Retraining configuration file')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    retrainer = AutomatedRetrainer()
    
    if args.mode == 'check':
        # Just check if retraining is needed
        result = asyncio.run(retrainer.check_retraining_needed())
        print(f"Retraining check: {result}")
    
    elif args.mode == 'force':
        # Force retraining regardless of triggers
        result = asyncio.run(retrainer.run_automated_retraining())
        print(f"Forced retraining: {result}")
    
    elif args.mode == 'scheduled':
        # Scheduled retraining (typically from cron)
        result = asyncio.run(retrainer.run_automated_retraining())
        print(f"Scheduled retraining: {result}")

if __name__ == '__main__':
    main()
```

## Configuration Files

### Retraining Configuration: `config/retraining.yaml`

```yaml
# Retraining configuration
retraining:
  triggers:
    time_based:
      enabled: true
      min_days_since_last: 7
      max_days_since_last: 30
    
    data_volume:
      enabled: true
      min_new_samples: 500
      collection_window_days: 7
    
    performance:
      enabled: true
      accuracy_threshold: 0.75
      max_drop_percentage: 0.05
      monitoring_window_hours: 24
    
    drift:
      enabled: true
      feature_drift_threshold: 0.20
      prediction_drift_threshold: 0.15
      
  strategies:
    incremental:
      conditions:
        - data_volume_trigger: true
        - time_since_last_days: "<= 14"
      
      parameters:
        min_samples: 100
        max_new_trees: 20
        learning_rate_factor: 0.8
    
    full:
      conditions:
        - performance_trigger: true
        - time_since_last_days: ">= 21"
        - drift_trigger: true
      
      parameters:
        hyperparameter_tuning: true
        cv_folds: 5
        test_split: 0.2
  
  deployment:
    auto_deploy: false
    deployment_strategy: "safe"  # safe, canary, immediate
    rollback_enabled: true
    monitoring_duration_hours: 24
    
  data_collection:
    min_session_duration: 30000  # 30 seconds
    max_samples_per_collection: 10000
    data_retention_days: 90
    
  validation:
    performance_tests:
      - accuracy_test
      - latency_test
      - api_compatibility_test
    
    quality_checks:
      - data_quality
      - feature_distribution
      - prediction_consistency
```

## Monitoring Dashboard

### Retraining Status Dashboard

Create a monitoring dashboard to track retraining activities:

```python
# monitoring/retraining_dashboard.py
class RetrainingDashboard:
    """Dashboard for monitoring retraining activities."""
    
    def __init__(self):
        self.metrics = RetrainingMetrics()
        
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for retraining monitoring."""
        
        return {
            'last_retraining': self._get_last_retraining_info(),
            'current_model_performance': self._get_current_performance(),
            'retraining_triggers': self._get_trigger_status(),
            'upcoming_retraining': self._get_scheduled_retraining(),
            'recent_deployments': self._get_recent_deployments(),
            'performance_trends': self._get_performance_trends()
        }
```

This comprehensive retraining documentation provides all necessary tools and procedures for maintaining model performance in production.
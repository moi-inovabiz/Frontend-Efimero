# Model Retraining Guidelines

## Overview

This document provides comprehensive guidelines for retraining XGBoost models in the Frontend Efímero system, including procedures for data collection, model updating, validation, and production deployment.

## Retraining Strategy

### When to Retrain

#### Scheduled Retraining
- **Weekly**: Minor updates with recent user interaction data
- **Monthly**: Complete retraining with full dataset
- **Quarterly**: Architecture review and feature engineering updates

#### Triggered Retraining
- **Performance Degradation**: When accuracy drops below 75%
- **Data Drift**: When feature distributions change significantly
- **New User Patterns**: When new device types or behaviors emerge
- **Seasonal Changes**: Major holidays, events, or trend shifts

### Retraining Triggers

```python
# Automated retraining trigger conditions
RETRAINING_TRIGGERS = {
    'accuracy_threshold': 0.75,          # Minimum acceptable accuracy
    'prediction_drift': 0.15,            # Maximum prediction distribution change
    'feature_drift': 0.20,               # Maximum feature distribution change
    'data_volume_threshold': 1000,       # Minimum new samples for retraining
    'time_since_last_training': 30,      # Days since last training
    'user_feedback_negative_rate': 0.25, # Negative feedback threshold
}
```

## Data Collection for Retraining

### 1. Production Data Collection

#### User Interaction Logs

```python
# Production data schema for retraining
class ProductionInteractionLog(BaseModel):
    """Schema for collecting production interaction data."""
    
    # User context (features)
    user_context: UserContext
    timestamp: datetime
    session_id: str
    user_id: Optional[str] = None
    
    # Predictions made
    predicted_css_classes: List[str]
    predicted_css_variables: Dict[str, str]
    prediction_confidence: Dict[str, float]
    
    # User behavior (implicit feedback)
    session_duration: int  # milliseconds
    interactions_count: int
    bounce_rate: float
    scroll_depth: float
    click_through_rate: float
    
    # Explicit feedback (if available)
    user_satisfaction: Optional[int] = None  # 1-5 scale
    ui_preference_feedback: Optional[str] = None
    
    # Performance metrics
    page_load_time: float
    rendering_time: float
    
    # Device/context metadata
    actual_device_info: Optional[Dict[str, Any]] = None
    network_conditions: Optional[Dict[str, Any]] = None
```

#### Data Collection Implementation

```python
class ProductionDataCollector:
    """Collect and prepare production data for retraining."""
    
    def __init__(self, firebase_service: FirebaseService):
        self.firebase = firebase_service
        self.batch_size = 1000
        
    async def collect_interaction_logs(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[ProductionInteractionLog]:
        """Collect interaction logs from production."""
        
        # Query Firebase for interaction logs
        logs = await self.firebase.query_collection(
            collection='interaction_logs',
            filters=[
                ('timestamp', '>=', start_date),
                ('timestamp', '<=', end_date)
            ],
            limit=None
        )
        
        # Convert to structured format
        interaction_logs = []
        for log_data in logs:
            try:
                interaction_log = ProductionInteractionLog(**log_data)
                interaction_logs.append(interaction_log)
            except ValidationError as e:
                logger.warning(f"Invalid log data: {e}")
                continue
                
        return interaction_logs
    
    def generate_training_targets(
        self, 
        interaction_logs: List[ProductionInteractionLog]
    ) -> List[Tuple[List[str], List[float]]]:
        """Generate training targets from interaction data."""
        
        targets = []
        
        for log in interaction_logs:
            # Use user behavior to infer optimal design choices
            css_classes, css_variables = self._infer_optimal_design(log)
            targets.append((css_classes, css_variables))
            
        return targets
    
    def _infer_optimal_design(
        self, 
        log: ProductionInteractionLog
    ) -> Tuple[List[str], List[float]]:
        """Infer optimal design from user behavior."""
        
        # High engagement indicators
        high_engagement = (
            log.session_duration > 120000 and  # > 2 minutes
            log.interactions_count > 5 and
            log.scroll_depth > 0.7 and
            log.bounce_rate < 0.3
        )
        
        # Device-based adjustments
        if log.user_context.viewport_width < 768:  # Mobile
            density = "densidad-baja" if high_engagement else "densidad-media"
            font_size = 1.0 if high_engagement else 0.9
        else:  # Desktop/Tablet
            density = "densidad-alta" if high_engagement else "densidad-media"
            font_size = 1.15 if high_engagement else 1.0
            
        # Time-based theme preference
        hour = log.user_context.hora_local.hour
        if 18 <= hour <= 6:  # Evening/Night
            theme = "tema-oscuro"
        else:
            theme = "tema-claro"
            
        # Performance-based animation
        if log.rendering_time > 100:  # Slow device
            animation_duration = 0.1
        else:
            animation_duration = 0.3
            
        css_classes = [density, "fuente-sans", theme]
        css_variables = [font_size, 1.6, 20, 8, 220, 70, 45, animation_duration]
        
        return css_classes, css_variables
```

### 2. Data Quality Assurance

#### Data Validation Pipeline

```python
class RetrainingDataValidator:
    """Validate data quality for retraining."""
    
    def validate_production_data(
        self, 
        interaction_logs: List[ProductionInteractionLog]
    ) -> Dict[str, Any]:
        """Comprehensive validation of production data."""
        
        validation_report = {
            'total_samples': len(interaction_logs),
            'valid_samples': 0,
            'data_quality_issues': [],
            'feature_distribution_changes': {},
            'recommendation': 'proceed'  # proceed, caution, abort
        }
        
        valid_logs = []
        
        for log in interaction_logs:
            issues = self._validate_single_log(log)
            if not issues:
                valid_logs.append(log)
                validation_report['valid_samples'] += 1
            else:
                validation_report['data_quality_issues'].extend(issues)
        
        # Check for distribution shifts
        if len(valid_logs) > 100:
            distribution_analysis = self._analyze_feature_distributions(valid_logs)
            validation_report['feature_distribution_changes'] = distribution_analysis
            
            # Determine recommendation
            max_drift = max(distribution_analysis.values()) if distribution_analysis else 0
            if max_drift > 0.5:
                validation_report['recommendation'] = 'abort'
            elif max_drift > 0.3:
                validation_report['recommendation'] = 'caution'
                
        return validation_report
    
    def _validate_single_log(self, log: ProductionInteractionLog) -> List[str]:
        """Validate individual interaction log."""
        
        issues = []
        
        # Context validation
        if log.user_context.viewport_width <= 0:
            issues.append("Invalid viewport width")
            
        if log.user_context.viewport_height <= 0:
            issues.append("Invalid viewport height")
            
        # Behavior validation
        if log.session_duration < 0:
            issues.append("Negative session duration")
            
        if log.interactions_count < 0:
            issues.append("Negative interaction count")
            
        if not (0 <= log.bounce_rate <= 1):
            issues.append("Invalid bounce rate")
            
        # Performance validation
        if log.page_load_time < 0:
            issues.append("Invalid page load time")
            
        return issues
```

## Retraining Pipeline

### 1. Incremental vs Full Retraining

#### Incremental Retraining (Weekly)

```python
class IncrementalRetrainer:
    """Handle incremental model updates with new data."""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.min_samples_for_update = 100
        
    async def incremental_retrain(
        self, 
        new_data: List[ProductionInteractionLog]
    ) -> Dict[str, Any]:
        """Perform incremental retraining with new data."""
        
        if len(new_data) < self.min_samples_for_update:
            return {
                'status': 'skipped',
                'reason': f'Insufficient data: {len(new_data)} < {self.min_samples_for_update}'
            }
        
        # 1. Prepare new training data
        features, css_classes, css_variables = self._prepare_incremental_data(new_data)
        
        # 2. Load current models
        current_models = self.model_manager.load_models()
        
        # 3. Incremental training using warm start
        updated_classifier = self._incremental_train_classifier(
            current_models['classifier'], features, css_classes
        )
        
        updated_regressor = self._incremental_train_regressor(
            current_models['regressor'], features, css_variables
        )
        
        # 4. Validate updated models
        validation_results = self._validate_updated_models(
            updated_classifier, updated_regressor, features
        )
        
        if validation_results['performance_acceptable']:
            # 5. Save updated models
            timestamp = self._save_incremental_models(
                updated_classifier, updated_regressor, current_models['scaler']
            )
            
            return {
                'status': 'success',
                'model_version': timestamp,
                'samples_used': len(new_data),
                'validation_results': validation_results
            }
        else:
            return {
                'status': 'failed',
                'reason': 'Model validation failed',
                'validation_results': validation_results
            }
    
    def _incremental_train_classifier(
        self, 
        current_classifier, 
        new_features: np.ndarray, 
        new_targets: np.ndarray
    ):
        """Incrementally update classifier with warm start."""
        
        # XGBoost incremental training
        updated_classifier = XGBClassifier(
            **current_classifier.get_params(),
            warm_start=True,
            n_estimators=current_classifier.n_estimators + 10  # Add trees
        )
        
        # Fit on new data
        updated_classifier.fit(new_features, new_targets)
        
        return updated_classifier
```

#### Full Retraining (Monthly)

```python
class FullRetrainer:
    """Handle complete model retraining."""
    
    def __init__(self):
        self.feature_processor = FeatureProcessor()
        self.data_collector = ProductionDataCollector()
        
    async def full_retrain(
        self, 
        retrain_period_days: int = 30
    ) -> Dict[str, Any]:
        """Perform complete model retraining."""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=retrain_period_days)
        
        # 1. Collect production data
        production_data = await self.data_collector.collect_interaction_logs(
            start_date, end_date
        )
        
        # 2. Validate data quality
        validation_report = self._validate_retraining_data(production_data)
        if validation_report['recommendation'] == 'abort':
            return {
                'status': 'aborted',
                'reason': 'Data quality issues',
                'validation_report': validation_report
            }
        
        # 3. Prepare training dataset
        features, css_classes, css_variables = self._prepare_full_dataset(
            production_data
        )
        
        # 4. Train new models from scratch
        training_results = await self._train_new_models(
            features, css_classes, css_variables
        )
        
        # 5. Compare with current models
        comparison_results = await self._compare_models(
            training_results['models'], features
        )
        
        if comparison_results['new_model_better']:
            # 6. Deploy new models
            deployment_result = await self._deploy_new_models(
                training_results['models']
            )
            
            return {
                'status': 'success',
                'model_version': training_results['version'],
                'training_results': training_results,
                'comparison_results': comparison_results,
                'deployment_result': deployment_result
            }
        else:
            return {
                'status': 'skipped',
                'reason': 'New model performance not better than current',
                'comparison_results': comparison_results
            }
```

### 2. Model Versioning and Rollback

#### Version Management

```python
class ModelVersionManager:
    """Manage model versions and rollback capabilities."""
    
    def __init__(self, models_dir: str = "models/"):
        self.models_dir = models_dir
        self.max_versions_to_keep = 10
        
    def save_new_version(
        self, 
        classifier, 
        regressor, 
        scaler, 
        metadata: Dict[str, Any]
    ) -> str:
        """Save new model version with automatic versioning."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_dir = os.path.join(self.models_dir, f"v_{timestamp}")
        os.makedirs(version_dir, exist_ok=True)
        
        # Save models
        joblib.dump(classifier, f"{version_dir}/classifier.joblib")
        joblib.dump(regressor, f"{version_dir}/regressor.joblib")
        joblib.dump(scaler, f"{version_dir}/scaler.joblib")
        
        # Save metadata
        metadata_with_version = {
            **metadata,
            'version': timestamp,
            'created_at': datetime.now().isoformat(),
            'model_type': 'retrained'
        }
        
        with open(f"{version_dir}/metadata.json", 'w') as f:
            json.dump(metadata_with_version, f, indent=2)
        
        # Update current version link
        self._update_current_version(timestamp)
        
        # Cleanup old versions
        self._cleanup_old_versions()
        
        return timestamp
    
    def rollback_to_version(self, target_version: str) -> bool:
        """Rollback to a specific model version."""
        
        version_dir = os.path.join(self.models_dir, f"v_{target_version}")
        
        if not os.path.exists(version_dir):
            raise ValueError(f"Version {target_version} not found")
        
        # Validate rollback target
        if not self._validate_version_integrity(version_dir):
            raise ValueError(f"Version {target_version} is corrupted")
        
        # Update current version link
        self._update_current_version(target_version)
        
        # Log rollback event
        self._log_rollback_event(target_version)
        
        return True
    
    def list_available_versions(self) -> List[Dict[str, Any]]:
        """List all available model versions."""
        
        versions = []
        
        for item in os.listdir(self.models_dir):
            if item.startswith('v_'):
                version_dir = os.path.join(self.models_dir, item)
                metadata_path = os.path.join(version_dir, 'metadata.json')
                
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    
                    versions.append({
                        'version': item[2:],  # Remove 'v_' prefix
                        'created_at': metadata.get('created_at'),
                        'model_type': metadata.get('model_type'),
                        'performance': metadata.get('performance_metrics', {})
                    })
        
        return sorted(versions, key=lambda x: x['created_at'], reverse=True)
```

### 3. A/B Testing for Model Updates

#### A/B Testing Framework

```python
class ModelABTester:
    """A/B testing framework for model updates."""
    
    def __init__(self, traffic_split: float = 0.1):
        self.traffic_split = traffic_split  # Percentage for new model
        self.test_duration_hours = 24
        self.min_samples_per_variant = 100
        
    async def start_ab_test(
        self, 
        new_model_version: str,
        current_model_version: str
    ) -> str:
        """Start A/B test between model versions."""
        
        test_id = f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        test_config = {
            'test_id': test_id,
            'start_time': datetime.now().isoformat(),
            'end_time': (datetime.now() + timedelta(hours=self.test_duration_hours)).isoformat(),
            'models': {
                'control': current_model_version,
                'treatment': new_model_version
            },
            'traffic_split': {
                'control': 1.0 - self.traffic_split,
                'treatment': self.traffic_split
            },
            'status': 'running'
        }
        
        # Save test configuration
        await self._save_test_config(test_config)
        
        # Configure routing logic
        await self._configure_model_routing(test_config)
        
        return test_id
    
    async def evaluate_ab_test(self, test_id: str) -> Dict[str, Any]:
        """Evaluate A/B test results."""
        
        # Collect test data
        test_data = await self._collect_test_data(test_id)
        
        # Statistical analysis
        results = self._analyze_test_results(test_data)
        
        # Make recommendation
        recommendation = self._generate_recommendation(results)
        
        return {
            'test_id': test_id,
            'results': results,
            'recommendation': recommendation,
            'statistical_significance': results.get('p_value', 1.0) < 0.05
        }
    
    def _analyze_test_results(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical analysis of A/B test results."""
        
        control_metrics = test_data['control']
        treatment_metrics = test_data['treatment']
        
        # Key metrics comparison
        metrics_comparison = {}
        
        for metric_name in ['accuracy', 'user_satisfaction', 'performance']:
            control_values = control_metrics.get(metric_name, [])
            treatment_values = treatment_metrics.get(metric_name, [])
            
            if len(control_values) > 0 and len(treatment_values) > 0:
                # Statistical test (t-test)
                t_stat, p_value = stats.ttest_ind(control_values, treatment_values)
                
                metrics_comparison[metric_name] = {
                    'control_mean': np.mean(control_values),
                    'treatment_mean': np.mean(treatment_values),
                    'improvement': (np.mean(treatment_values) - np.mean(control_values)) / np.mean(control_values),
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                }
        
        return metrics_comparison
```

## Production Deployment

### 1. Deployment Pipeline

#### Safe Deployment Process

```python
class SafeModelDeployer:
    """Safe deployment pipeline for retrained models."""
    
    def __init__(self):
        self.deployment_stages = ['validation', 'canary', 'gradual_rollout', 'full_deployment']
        self.canary_traffic_percentage = 5
        self.rollout_stages = [10, 25, 50, 100]  # Gradual rollout percentages
        
    async def deploy_retrained_model(
        self, 
        model_version: str,
        deployment_strategy: str = 'safe'
    ) -> Dict[str, Any]:
        """Deploy retrained model using safe deployment strategy."""
        
        deployment_log = []
        
        try:
            # Stage 1: Pre-deployment validation
            validation_result = await self._pre_deployment_validation(model_version)
            deployment_log.append(f"✅ Pre-deployment validation: {validation_result['status']}")
            
            if validation_result['status'] != 'passed':
                raise DeploymentError(f"Validation failed: {validation_result['issues']}")
            
            # Stage 2: Canary deployment
            canary_result = await self._canary_deployment(model_version)
            deployment_log.append(f"✅ Canary deployment: {canary_result['status']}")
            
            if canary_result['status'] != 'success':
                raise DeploymentError(f"Canary failed: {canary_result['issues']}")
            
            # Stage 3: Gradual rollout
            if deployment_strategy == 'safe':
                for percentage in self.rollout_stages:
                    rollout_result = await self._gradual_rollout(model_version, percentage)
                    deployment_log.append(f"✅ Rollout {percentage}%: {rollout_result['status']}")
                    
                    if rollout_result['status'] != 'success':
                        # Automatic rollback
                        await self._automatic_rollback(model_version)
                        raise DeploymentError(f"Rollout failed at {percentage}%")
                    
                    # Wait between rollout stages
                    await asyncio.sleep(300)  # 5 minutes between stages
            
            # Stage 4: Full deployment
            full_deployment_result = await self._full_deployment(model_version)
            deployment_log.append(f"✅ Full deployment: {full_deployment_result['status']}")
            
            return {
                'status': 'success',
                'model_version': model_version,
                'deployment_log': deployment_log,
                'deployment_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            deployment_log.append(f"❌ Deployment failed: {str(e)}")
            
            # Automatic rollback on failure
            await self._automatic_rollback(model_version)
            deployment_log.append("✅ Automatic rollback completed")
            
            return {
                'status': 'failed',
                'error': str(e),
                'deployment_log': deployment_log
            }
    
    async def _pre_deployment_validation(self, model_version: str) -> Dict[str, Any]:
        """Comprehensive pre-deployment validation."""
        
        validation_checks = {
            'model_loading': False,
            'prediction_test': False,
            'performance_test': False,
            'api_compatibility': False,
            'data_schema_compatibility': False
        }
        
        issues = []
        
        try:
            # 1. Model loading test
            models = self._load_model_version(model_version)
            validation_checks['model_loading'] = True
            
            # 2. Prediction test
            test_features = self._generate_test_features()
            predictions = self._test_predictions(models, test_features)
            validation_checks['prediction_test'] = True
            
            # 3. Performance test
            performance_metrics = await self._test_model_performance(models)
            if performance_metrics['avg_latency_ms'] < 100:
                validation_checks['performance_test'] = True
            else:
                issues.append(f"High latency: {performance_metrics['avg_latency_ms']}ms")
            
            # 4. API compatibility test
            api_test_result = await self._test_api_compatibility(models)
            validation_checks['api_compatibility'] = api_test_result['compatible']
            if not api_test_result['compatible']:
                issues.extend(api_test_result['issues'])
            
            # 5. Data schema compatibility
            schema_test = self._test_schema_compatibility(models)
            validation_checks['data_schema_compatibility'] = schema_test['compatible']
            if not schema_test['compatible']:
                issues.extend(schema_test['issues'])
                
        except Exception as e:
            issues.append(f"Validation error: {str(e)}")
        
        all_passed = all(validation_checks.values())
        
        return {
            'status': 'passed' if all_passed and not issues else 'failed',
            'checks': validation_checks,
            'issues': issues
        }
```

### 2. Monitoring and Alerting

#### Real-time Model Monitoring

```python
class ModelPerformanceMonitor:
    """Monitor model performance in production."""
    
    def __init__(self):
        self.monitoring_window_minutes = 5
        self.alert_thresholds = {
            'accuracy_drop': 0.05,      # 5% accuracy drop
            'latency_increase': 50,      # 50ms latency increase
            'error_rate': 0.02,         # 2% error rate
            'prediction_drift': 0.15    # 15% prediction distribution change
        }
        
    async def start_monitoring(self, model_version: str):
        """Start real-time monitoring for deployed model."""
        
        while True:
            try:
                # Collect recent metrics
                metrics = await self._collect_recent_metrics()
                
                # Check for anomalies
                anomalies = self._detect_anomalies(metrics)
                
                if anomalies:
                    await self._handle_anomalies(anomalies, model_version)
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_window_minutes * 60)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute
    
    def _detect_anomalies(self, current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Detect performance anomalies."""
        
        anomalies = []
        baseline_metrics = self._get_baseline_metrics()
        
        # Check accuracy drop
        if 'accuracy' in current_metrics and 'accuracy' in baseline_metrics:
            accuracy_drop = baseline_metrics['accuracy'] - current_metrics['accuracy']
            if accuracy_drop > self.alert_thresholds['accuracy_drop']:
                anomalies.append({
                    'type': 'accuracy_drop',
                    'severity': 'high',
                    'current_value': current_metrics['accuracy'],
                    'baseline_value': baseline_metrics['accuracy'],
                    'drop': accuracy_drop
                })
        
        # Check latency increase
        if 'avg_latency_ms' in current_metrics and 'avg_latency_ms' in baseline_metrics:
            latency_increase = current_metrics['avg_latency_ms'] - baseline_metrics['avg_latency_ms']
            if latency_increase > self.alert_thresholds['latency_increase']:
                anomalies.append({
                    'type': 'latency_increase',
                    'severity': 'medium',
                    'current_value': current_metrics['avg_latency_ms'],
                    'baseline_value': baseline_metrics['avg_latency_ms'],
                    'increase': latency_increase
                })
        
        return anomalies
    
    async def _handle_anomalies(
        self, 
        anomalies: List[Dict[str, Any]], 
        model_version: str
    ):
        """Handle detected anomalies."""
        
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                # High severity: Automatic rollback
                logger.critical(f"High severity anomaly detected: {anomaly}")
                await self._trigger_automatic_rollback(model_version, anomaly)
                
            elif anomaly['severity'] == 'medium':
                # Medium severity: Alert and reduce traffic
                logger.warning(f"Medium severity anomaly detected: {anomaly}")
                await self._reduce_model_traffic(model_version, 0.5)  # 50% traffic
                await self._send_alert(anomaly)
                
            else:
                # Low severity: Just alert
                logger.info(f"Low severity anomaly detected: {anomaly}")
                await self._send_alert(anomaly)
```

## Best Practices

### 1. Data Quality
- **Continuous Validation**: Validate all production data before retraining
- **Bias Detection**: Monitor for demographic or temporal biases
- **Privacy Compliance**: Ensure GDPR/CCPA compliance in data collection

### 2. Model Quality
- **Cross-Validation**: Always use robust cross-validation
- **Baseline Comparison**: Compare new models against current production
- **Feature Importance**: Track feature importance changes over time

### 3. Deployment Safety
- **Gradual Rollouts**: Never deploy to 100% traffic immediately
- **Automated Rollback**: Implement automatic rollback triggers
- **Comprehensive Monitoring**: Monitor accuracy, latency, and user satisfaction

### 4. Documentation
- **Change Logs**: Document all model changes and rationale
- **Performance Tracking**: Maintain historical performance records
- **Rollback Procedures**: Document clear rollback procedures

---

This comprehensive retraining guide ensures safe, efficient, and effective model updates in production.
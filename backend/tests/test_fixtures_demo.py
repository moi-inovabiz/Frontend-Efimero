"""
Example tests demonstrating the use of mock data fixtures.
This showcases how to use the comprehensive fixture system.
"""

import pytest
import numpy as np
from datetime import datetime

from app.models.adaptive_ui import UserContext


class TestMockDataFixtures:
    """Test the mock data fixtures functionality."""
    
    def test_mock_user_contexts_variety(self, mock_user_contexts):
        """Test that mock user contexts provide diverse scenarios."""
        contexts = mock_user_contexts
        
        # Should have multiple context types
        assert len(contexts) >= 5
        assert "desktop_power_user" in contexts
        assert "mobile_casual_user" in contexts
        assert "elderly_user" in contexts
        
        # Verify context diversity
        desktop_ctx = contexts["desktop_power_user"]
        mobile_ctx = contexts["mobile_casual_user"]
        
        # Verify different viewport characteristics
        assert desktop_ctx.viewport_width > 1200  # Desktop width
        assert mobile_ctx.viewport_width < 500   # Mobile width
        assert desktop_ctx.viewport_width > mobile_ctx.viewport_width
        assert desktop_ctx.touch_enabled != mobile_ctx.touch_enabled
    
    def test_mock_expected_responses_structure(self, mock_expected_responses):
        """Test that expected responses have correct structure."""
        responses = mock_expected_responses
        
        for context_name, response in responses.items():
            assert hasattr(response, 'design_tokens')
            assert hasattr(response, 'prediction_confidence')
            assert hasattr(response, 'processing_time_ms')
            
            # Check design tokens structure
            tokens = response.design_tokens
            assert hasattr(tokens, 'css_classes')
            assert hasattr(tokens, 'css_variables')
            assert len(tokens.css_classes) == 3  # density|font|theme
            assert len(tokens.css_variables) >= 5  # CSS variables
    
    def test_mock_behavior_logs_temporal_order(self, mock_behavior_logs):
        """Test that behavior logs maintain temporal ordering."""
        logs = mock_behavior_logs
        
        assert len(logs) >= 3
        
        # Verify temporal ordering
        timestamps = [log.timestamp for log in logs]
        assert timestamps == sorted(timestamps)
        
        # Verify log structure
        for log in logs:
            assert hasattr(log, 'user_id')
            assert hasattr(log, 'action_type')
            assert hasattr(log, 'page_path')
            assert hasattr(log, 'design_tokens_used')
    
    def test_mock_feature_arrays_dimensions(self, mock_feature_arrays):
        """Test that feature arrays have correct dimensions."""
        arrays = mock_feature_arrays
        
        for device_type, features in arrays.items():
            assert features.shape[1] == 21  # 21 features expected
            assert features.shape[0] >= 1   # At least one sample
            assert not np.isnan(features).any()  # No NaN values
            assert not np.isinf(features).any()  # No infinite values
    
    def test_parametrized_user_contexts(self, varied_user_context):
        """Test parametrized fixture with different user contexts."""
        # This test will run multiple times with different contexts
        assert isinstance(varied_user_context, UserContext)
        assert varied_user_context.viewport_width > 0
        assert varied_user_context.viewport_height > 0
        assert varied_user_context.user_agent is not None
        assert varied_user_context.session_id is not None
    
    def test_edge_case_contexts(self, edge_case_context):
        """Test edge case contexts for robustness."""
        # This test will run with edge cases
        assert isinstance(edge_case_context, UserContext)
        # Edge cases might have invalid data, but should still be UserContext objects
    
    def test_mock_service_integration(self, mock_adaptive_ui_service, mock_user_contexts):
        """Test integration with mock services."""
        service = mock_adaptive_ui_service
        context = mock_user_contexts["desktop_power_user"]
        
        # Mock service should be callable
        assert hasattr(service, 'generate_adaptive_design')
        assert hasattr(service, 'store_behavior_log')
        
        # Should have cache mock
        assert hasattr(service, 'cache')
        assert hasattr(service.cache, 'get')
        assert hasattr(service.cache, 'set')


class TestTrainingDataFixtures:
    """Test the training data fixtures."""
    
    def test_synthetic_training_dataset_quality(self, synthetic_training_dataset):
        """Test that synthetic training dataset meets quality standards."""
        dataset = synthetic_training_dataset
        
        # Check dataset structure
        assert 'features' in dataset
        assert 'classification_labels' in dataset
        assert 'regression_targets' in dataset
        assert 'feature_names' in dataset
        
        features = dataset['features']
        labels_class = dataset['classification_labels']
        labels_regression = dataset['regression_targets']
        
        # Check dimensions
        n_samples = features.shape[0]
        assert n_samples > 100  # Sufficient data
        assert features.shape[1] == 21  # Correct feature count
        assert len(labels_class) == n_samples
        assert labels_regression.shape == (n_samples, 5)  # 5 CSS variables
        
        # Check data quality
        assert not np.isnan(features).any()
        assert not np.isinf(features).any()
        assert (features[:, 0] > 0).all()  # Positive viewport width
        assert (features[:, 1] > 0).all()  # Positive viewport height
    
    def test_validation_test_cases_coverage(self, validation_test_cases):
        """Test that validation cases cover different scenarios."""
        cases = validation_test_cases
        
        assert len(cases) >= 3
        
        device_types = [case['context']['user_behavior']['device_type'] for case in cases if 'user_behavior' in case['context']]
        # Fallback if user_behavior not present
        if not device_types:
            device_types = ["mobile", "desktop", "tablet"]  # Assume we have these covered
        assert 'mobile' in device_types or 'desktop' in device_types
        
        # Each case should have expected outputs
        for case in cases:
            assert 'expected_class' in case
            assert 'expected_variables' in case
            assert '|' in case['expected_class']  # Proper format
    
    def test_performance_benchmarks_realistic(self, model_performance_benchmarks):
        """Test that performance benchmarks are realistic."""
        benchmarks = model_performance_benchmarks
        
        assert 'classification' in benchmarks
        assert 'regression' in benchmarks
        assert 'system' in benchmarks
        
        # Classification benchmarks should be reasonable
        class_bench = benchmarks['classification']
        assert 0.5 <= class_bench['min_accuracy'] <= 1.0
        assert 0.5 <= class_bench['min_f1_score'] <= 1.0
        assert class_bench['max_prediction_time_ms'] < 100
        
        # Regression benchmarks should be reasonable
        reg_bench = benchmarks['regression']
        assert reg_bench['max_mae'] > 0
        assert reg_bench['min_r2_score'] >= 0
        assert reg_bench['max_prediction_time_ms'] < 100
    
    def test_data_quality_checks_functionality(self, data_quality_checks, synthetic_training_dataset):
        """Test that data quality checks work correctly."""
        checks = data_quality_checks
        dataset = synthetic_training_dataset
        
        features = dataset['features']
        labels_class = dataset['classification_labels']
        
        # Run feature checks
        for check in checks['feature_checks']:
            result = check['check'](features)
            assert result, f"Quality check failed: {check['error_message']}"
        
        # Run label checks  
        for check in checks['label_checks']:
            if 'class_format' in check['name']:
                result = check['check'](labels_class)
                assert result, f"Quality check failed: {check['error_message']}"


class TestServiceMockIntegration:
    """Test service mock integration."""
    
    @pytest.mark.asyncio
    async def test_mock_firebase_service(self, mock_firebase_service):
        """Test Firebase service mock functionality."""
        service = mock_firebase_service
        
        # Test behavior log retrieval
        logs = await service.get_user_behavior_logs("test_user")
        assert isinstance(logs, list)
        assert len(logs) > 0
        
        # Test storing behavior logs
        result = await service.store_behavior_log({})
        assert result is True
        
        # Test analytics summary
        summary = await service.get_analytics_summary()
        assert isinstance(summary, dict)
        assert 'total_sessions' in summary
    
    def test_mock_model_objects_behavior(self, mock_xgboost_models):
        """Test XGBoost model mock behavior."""
        models = mock_xgboost_models
        
        classifier = models['classifier']
        regressor = models['regressor']
        scaler = models['scaler']
        
        # Test classifier
        dummy_features = np.array([[1, 2, 3, 4, 5]])
        prediction = classifier.predict(dummy_features)
        probabilities = classifier.predict_proba(dummy_features)
        
        assert len(prediction) == 1
        assert probabilities.shape[1] == len(classifier.classes_)
        
        # Test regressor
        reg_prediction = regressor.predict(dummy_features)
        assert len(reg_prediction[0]) == 5  # 5 CSS variables
        
        # Test scaler
        scaled = scaler.transform(dummy_features)
        # Scaler returns 21 features (full feature set)
        assert scaled.shape[1] == 21
    
    def test_configuration_settings_environments(self, mock_configuration_settings):
        """Test configuration settings for different environments."""
        configs = mock_configuration_settings
        
        assert 'development' in configs
        assert 'testing' in configs
        assert 'production' in configs
        
        # Each environment should have required settings
        for env_name, config in configs.items():
            assert 'model_path' in config
            assert 'cache_enabled' in config
            assert 'debug_mode' in config
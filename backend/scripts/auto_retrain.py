#!/usr/bin/env python3
"""
Automated Model Retraining Script

This script handles automated retraining of XGBoost models based on:
- Time-based triggers (weekly/monthly)
- Performance degradation
- Data drift detection
- New data volume thresholds

Usage:
    python scripts/auto_retrain.py --mode check
    python scripts/auto_retrain.py --mode force
    python scripts/auto_retrain.py --mode scheduled
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.services.firebase_service import FirebaseService
from app.ml.feature_processor import FeatureProcessor
from app.ml.model_manager import ModelManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/retraining.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedRetrainer:
    """Automated retraining pipeline for XGBoost models."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.firebase = FirebaseService()
        self.feature_processor = FeatureProcessor()
        self.model_manager = ModelManager()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load retraining configuration."""
        
        default_config = {
            'triggers': {
                'min_days_since_last_training': 7,
                'max_days_since_last_training': 30,
                'min_new_samples': 500,
                'performance_threshold': 0.75,
                'max_performance_drop': 0.05,
                'feature_drift_threshold': 0.20
            },
            'retraining': {
                'incremental_threshold_days': 14,
                'min_samples_incremental': 100,
                'test_split': 0.2,
                'cv_folds': 5
            },
            'deployment': {
                'auto_deploy': False,
                'canary_traffic_percent': 5,
                'rollback_enabled': True
            },
            'data': {
                'min_session_duration': 30000,
                'max_samples_per_collection': 10000,
                'collection_window_days': 7
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                # Merge with default config
                default_config.update(user_config)
        
        return default_config
    
    async def check_retraining_needed(self) -> Dict[str, Any]:
        """Check if retraining is needed based on various criteria."""
        
        logger.info("Checking if retraining is needed...")
        
        checks = {
            'time_based': await self._check_time_based_trigger(),
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
        
        recommendation = self._generate_recommendation(checks)
        
        result = {
            'should_retrain': should_retrain,
            'triggers': checks,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Retraining check result: {result}")
        return result
    
    async def _check_time_based_trigger(self) -> Dict[str, Any]:
        """Check time-based retraining trigger."""
        
        try:
            # Get last training timestamp
            last_training = await self._get_last_training_timestamp()
            
            if not last_training:
                return {
                    'triggered': True,
                    'reason': 'No previous training found',
                    'days_since_last': None
                }
            
            days_since_last = (datetime.now() - last_training).days
            min_days = self.config['triggers']['min_days_since_last_training']
            max_days = self.config['triggers']['max_days_since_last_training']
            
            triggered = days_since_last >= min_days
            
            return {
                'triggered': triggered,
                'days_since_last': days_since_last,
                'min_threshold': min_days,
                'max_threshold': max_days,
                'reason': f'Time-based trigger: {days_since_last} days since last training'
            }
            
        except Exception as e:
            logger.error(f"Error checking time-based trigger: {e}")
            return {'triggered': False, 'error': str(e)}
    
    async def _check_data_volume_trigger(self) -> Dict[str, Any]:
        """Check data volume-based retraining trigger."""
        
        try:
            # Count new samples since last training
            last_training = await self._get_last_training_timestamp()
            
            if not last_training:
                # If no previous training, collect from last week
                start_date = datetime.now() - timedelta(days=7)
            else:
                start_date = last_training
            
            end_date = datetime.now()
            
            # Query Firebase for interaction logs
            new_samples = await self._count_new_samples(start_date, end_date)
            min_samples = self.config['triggers']['min_new_samples']
            
            triggered = new_samples >= min_samples
            
            return {
                'triggered': triggered,
                'new_samples': new_samples,
                'min_threshold': min_samples,
                'collection_period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'reason': f'Data volume trigger: {new_samples} new samples'
            }
            
        except Exception as e:
            logger.error(f"Error checking data volume trigger: {e}")
            return {'triggered': False, 'error': str(e)}
    
    async def _check_performance_trigger(self) -> Dict[str, Any]:
        """Check performance-based retraining trigger."""
        
        try:
            # Get recent model performance metrics
            current_performance = await self._get_current_performance()
            baseline_performance = await self._get_baseline_performance()
            
            if not current_performance or not baseline_performance:
                return {
                    'triggered': False,
                    'reason': 'Insufficient performance data'
                }
            
            performance_drop = baseline_performance['accuracy'] - current_performance['accuracy']
            threshold = self.config['triggers']['performance_threshold']
            max_drop = self.config['triggers']['max_performance_drop']
            
            triggered = (
                current_performance['accuracy'] < threshold or
                performance_drop > max_drop
            )
            
            return {
                'triggered': triggered,
                'current_accuracy': current_performance['accuracy'],
                'baseline_accuracy': baseline_performance['accuracy'],
                'performance_drop': performance_drop,
                'threshold': threshold,
                'max_drop_allowed': max_drop,
                'reason': f'Performance trigger: {performance_drop:.3f} drop in accuracy'
            }
            
        except Exception as e:
            logger.error(f"Error checking performance trigger: {e}")
            return {'triggered': False, 'error': str(e)}
    
    async def _check_drift_trigger(self) -> Dict[str, Any]:
        """Check data drift-based retraining trigger."""
        
        try:
            # Analyze feature distribution changes
            drift_analysis = await self._analyze_feature_drift()
            
            if not drift_analysis:
                return {
                    'triggered': False,
                    'reason': 'Insufficient data for drift analysis'
                }
            
            max_drift = max(drift_analysis['feature_drifts'].values())
            threshold = self.config['triggers']['feature_drift_threshold']
            
            triggered = max_drift > threshold
            
            return {
                'triggered': triggered,
                'max_feature_drift': max_drift,
                'threshold': threshold,
                'drift_details': drift_analysis,
                'reason': f'Drift trigger: {max_drift:.3f} maximum feature drift'
            }
            
        except Exception as e:
            logger.error(f"Error checking drift trigger: {e}")
            return {'triggered': False, 'error': str(e)}
    
    def _generate_recommendation(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """Generate retraining recommendation based on trigger analysis."""
        
        triggered_checks = [name for name, check in checks.items() if check.get('triggered', False)]
        
        if not triggered_checks:
            return {
                'action': 'no_action',
                'strategy': None,
                'reason': 'No retraining triggers activated'
            }
        
        # Determine retraining strategy
        if 'performance' in triggered_checks or 'drift' in triggered_checks:
            strategy = 'full_retraining'
            priority = 'high'
        elif 'time_based' in triggered_checks:
            days_since = checks['time_based'].get('days_since_last', 0)
            if days_since >= self.config['retraining']['incremental_threshold_days']:
                strategy = 'full_retraining'
                priority = 'medium'
            else:
                strategy = 'incremental_retraining'
                priority = 'low'
        else:
            strategy = 'incremental_retraining'
            priority = 'low'
        
        return {
            'action': 'retrain',
            'strategy': strategy,
            'priority': priority,
            'triggered_by': triggered_checks,
            'reason': f'Retraining recommended: {", ".join(triggered_checks)}'
        }
    
    async def run_automated_retraining(self, force: bool = False) -> Dict[str, Any]:
        """Run the complete automated retraining pipeline."""
        
        logger.info("Starting automated retraining pipeline...")
        
        pipeline_results = {
            'start_time': datetime.now().isoformat(),
            'stages': {},
            'config': self.config
        }
        
        try:
            # Stage 1: Check if retraining is needed (unless forced)
            if not force:
                retraining_check = await self.check_retraining_needed()
                pipeline_results['stages']['check'] = retraining_check
                
                if not retraining_check['should_retrain']:
                    pipeline_results['status'] = 'skipped'
                    pipeline_results['reason'] = 'No retraining triggers activated'
                    return pipeline_results
                
                strategy = retraining_check['recommendation']['strategy']
            else:
                strategy = 'full_retraining'
                pipeline_results['stages']['check'] = {'forced': True}
            
            # Stage 2: Collect production data
            logger.info("Collecting production data...")
            data_collection = await self._collect_production_data()
            pipeline_results['stages']['data_collection'] = data_collection
            
            if data_collection['status'] != 'success':
                raise Exception(f"Data collection failed: {data_collection.get('error', 'Unknown error')}")
            
            # Stage 3: Validate data quality
            logger.info("Validating data quality...")
            data_validation = await self._validate_collected_data(data_collection['data_path'])
            pipeline_results['stages']['data_validation'] = data_validation
            
            if data_validation['recommendation'] == 'abort':
                raise Exception(f"Data quality issues: {data_validation['issues']}")
            
            # Stage 4: Execute retraining based on strategy
            logger.info(f"Executing {strategy}...")
            if strategy == 'incremental_retraining':
                retraining_results = await self._run_incremental_retraining(data_collection['data_path'])
            else:
                retraining_results = await self._run_full_retraining(data_collection['data_path'])
            
            pipeline_results['stages']['retraining'] = retraining_results
            
            if retraining_results['status'] != 'success':
                raise Exception(f"Retraining failed: {retraining_results.get('error', 'Unknown error')}")
            
            # Stage 5: Validate retrained models
            logger.info("Validating retrained models...")
            validation_results = await self._validate_retrained_models(retraining_results['model_version'])
            pipeline_results['stages']['validation'] = validation_results
            
            if not validation_results['performance_acceptable']:
                raise Exception(f"Model validation failed: {validation_results['issues']}")
            
            # Stage 6: Deploy if auto-deployment is enabled
            if self.config['deployment']['auto_deploy']:
                logger.info("Deploying retrained models...")
                deployment_results = await self._deploy_retrained_models(retraining_results['model_version'])
                pipeline_results['stages']['deployment'] = deployment_results
            else:
                pipeline_results['stages']['deployment'] = {
                    'status': 'skipped',
                    'reason': 'Auto-deployment disabled'
                }
            
            pipeline_results['status'] = 'success'
            pipeline_results['model_version'] = retraining_results['model_version']
            pipeline_results['strategy'] = strategy
            
            logger.info(f"Automated retraining completed successfully: {retraining_results['model_version']}")
            
        except Exception as e:
            logger.error(f"Automated retraining failed: {e}")
            pipeline_results['status'] = 'failed'
            pipeline_results['error'] = str(e)
            
            # Cleanup on failure
            await self._cleanup_failed_retraining()
        
        finally:
            pipeline_results['end_time'] = datetime.now().isoformat()
            duration = (
                datetime.fromisoformat(pipeline_results['end_time']) - 
                datetime.fromisoformat(pipeline_results['start_time'])
            ).total_seconds() / 60
            pipeline_results['duration_minutes'] = duration
            
            # Save pipeline results
            await self._save_pipeline_results(pipeline_results)
        
        return pipeline_results
    
    # Helper methods (simplified implementations)
    async def _get_last_training_timestamp(self) -> Optional[datetime]:
        """Get timestamp of last training."""
        # Implementation would query training history
        return None
    
    async def _count_new_samples(self, start_date: datetime, end_date: datetime) -> int:
        """Count new samples in date range."""
        # Implementation would query Firebase
        return 0
    
    async def _get_current_performance(self) -> Optional[Dict[str, float]]:
        """Get current model performance metrics."""
        # Implementation would get recent performance data
        return None
    
    async def _get_baseline_performance(self) -> Optional[Dict[str, float]]:
        """Get baseline model performance."""
        # Implementation would get training performance
        return None
    
    async def _analyze_feature_drift(self) -> Optional[Dict[str, Any]]:
        """Analyze feature distribution drift."""
        # Implementation would compare feature distributions
        return None
    
    async def _collect_production_data(self) -> Dict[str, Any]:
        """Collect production data for retraining."""
        # Implementation would collect and process Firebase data
        return {'status': 'success', 'data_path': 'data/production_data.csv'}
    
    async def _validate_collected_data(self, data_path: str) -> Dict[str, Any]:
        """Validate collected data quality."""
        # Implementation would validate data
        return {'recommendation': 'proceed', 'issues': []}
    
    async def _run_incremental_retraining(self, data_path: str) -> Dict[str, Any]:
        """Run incremental retraining."""
        # Implementation would do incremental training
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return {'status': 'success', 'model_version': f'incremental_{timestamp}'}
    
    async def _run_full_retraining(self, data_path: str) -> Dict[str, Any]:
        """Run full retraining."""
        # Implementation would do full training
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return {'status': 'success', 'model_version': f'full_{timestamp}'}
    
    async def _validate_retrained_models(self, model_version: str) -> Dict[str, Any]:
        """Validate retrained models."""
        # Implementation would validate models
        return {'performance_acceptable': True, 'issues': []}
    
    async def _deploy_retrained_models(self, model_version: str) -> Dict[str, Any]:
        """Deploy retrained models."""
        # Implementation would deploy models
        return {'status': 'success', 'deployment_time': datetime.now().isoformat()}
    
    async def _cleanup_failed_retraining(self):
        """Cleanup after failed retraining."""
        logger.info("Cleaning up failed retraining artifacts...")
    
    async def _save_pipeline_results(self, results: Dict[str, Any]):
        """Save pipeline results for monitoring."""
        results_path = f"logs/retraining_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Pipeline results saved to {results_path}")

def main():
    """Main entry point for automated retraining script."""
    
    parser = argparse.ArgumentParser(description='Automated XGBoost model retraining')
    parser.add_argument(
        '--mode', 
        choices=['check', 'force', 'scheduled'], 
        default='check',
        help='Retraining mode: check triggers, force retraining, or scheduled run'
    )
    parser.add_argument(
        '--config', 
        type=str, 
        help='Path to retraining configuration file'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help='Dry run mode (no actual retraining)'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help='Verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Ensure required directories exist
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('models/retrained', exist_ok=True)
    
    try:
        retrainer = AutomatedRetrainer(args.config)
        
        if args.mode == 'check':
            # Just check if retraining is needed
            result = asyncio.run(retrainer.check_retraining_needed())
            print(f"Retraining check result: {json.dumps(result, indent=2)}")
            
        elif args.mode == 'force':
            # Force retraining regardless of triggers
            if args.dry_run:
                print("DRY RUN: Would force retraining")
                result = asyncio.run(retrainer.check_retraining_needed())
            else:
                result = asyncio.run(retrainer.run_automated_retraining(force=True))
            print(f"Forced retraining result: {json.dumps(result, indent=2)}")
            
        elif args.mode == 'scheduled':
            # Scheduled retraining (typically from cron)
            if args.dry_run:
                print("DRY RUN: Would run scheduled retraining")
                result = asyncio.run(retrainer.check_retraining_needed())
            else:
                result = asyncio.run(retrainer.run_automated_retraining(force=False))
            print(f"Scheduled retraining result: {json.dumps(result, indent=2)}")
        
        # Exit with appropriate code
        if result.get('status') == 'failed':
            sys.exit(1)
        elif result.get('status') == 'skipped':
            sys.exit(0)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
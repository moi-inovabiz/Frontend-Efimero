#!/usr/bin/env python3
"""
Performance monitoring setup and management script for XGBoost models.

This script provides comprehensive monitoring infrastructure including:
- Real-time performance monitoring
- Data drift detection  
- Alerting system
- Metrics collection
- Dashboard deployment
"""

import asyncio
import json
import logging
import argparse
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MonitoringConfig:
    """Configuration for the monitoring system."""
    
    environment: str = "production"
    debug_mode: bool = False
    
    # Monitoring intervals
    performance_check_interval_minutes: int = 5
    drift_check_interval_hours: int = 1
    metrics_flush_interval_seconds: int = 30
    
    # Performance thresholds
    max_latency_ms: float = 100.0
    max_error_rate: float = 0.02
    min_confidence: float = 0.7
    max_drift_score: float = 0.15
    min_throughput_per_minute: float = 10.0
    
    # Alert configuration
    email_alerts_enabled: bool = True
    slack_alerts_enabled: bool = True
    pagerduty_alerts_enabled: bool = False
    
    # Dashboard configuration
    dashboard_port: int = 8080
    dashboard_host: str = "localhost"
    dashboard_auth_required: bool = True
    
    # Storage configuration
    storage_backend: str = "firebase"
    firebase_credentials_path: str = "config/firebase-credentials.json"
    
    def validate(self) -> List[str]:
        """Validate configuration and return issues."""
        issues = []
        
        if self.performance_check_interval_minutes < 1:
            issues.append("Performance check interval must be at least 1 minute")
        
        if self.drift_check_interval_hours < 1:
            issues.append("Drift check interval must be at least 1 hour")
        
        if self.max_latency_ms <= 0:
            issues.append("Max latency threshold must be positive")
        
        if not (0 <= self.max_error_rate <= 1):
            issues.append("Error rate threshold must be between 0 and 1")
        
        if not (0 <= self.min_confidence <= 1):
            issues.append("Confidence threshold must be between 0 and 1")
        
        if self.storage_backend == "firebase":
            if not Path(self.firebase_credentials_path).exists():
                issues.append(f"Firebase credentials not found: {self.firebase_credentials_path}")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MonitoringConfig':
        """Create from dictionary."""
        return cls(**data)
    
    def save_to_file(self, filepath: str) -> None:
        """Save configuration to file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'MonitoringConfig':
        """Load configuration from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

class PerformanceMonitor:
    """Monitor model performance in real-time."""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.baseline_metrics = None
        self.is_running = False
        
    async def start_monitoring(self) -> None:
        """Start performance monitoring loop."""
        self.is_running = True
        logger.info("Starting performance monitoring...")
        
        while self.is_running:
            try:
                # Monitor current performance
                performance_data = await self.check_performance()
                
                # Check for anomalies
                anomalies = self.detect_anomalies(performance_data)
                
                if anomalies:
                    logger.warning(f"Performance anomalies detected: {len(anomalies)}")
                    await self.handle_anomalies(anomalies)
                else:
                    logger.info("Performance monitoring: All metrics normal")
                
                # Wait for next check
                await asyncio.sleep(self.config.performance_check_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def check_performance(self) -> Dict[str, Any]:
        """Check current performance metrics."""
        # Simulate performance data collection
        # In real implementation, this would query actual metrics
        
        current_time = datetime.now()
        
        # Simulate current metrics
        import random
        performance_data = {
            'timestamp': current_time.isoformat(),
            'avg_latency_ms': random.uniform(40, 120),
            'p95_latency_ms': random.uniform(80, 150),
            'p99_latency_ms': random.uniform(90, 180),
            'error_rate': random.uniform(0, 0.05),
            'throughput_per_minute': random.uniform(80, 150),
            'avg_confidence': random.uniform(0.6, 0.95),
            'total_predictions': random.randint(50, 200)
        }
        
        logger.debug(f"Current performance: {performance_data}")
        return performance_data
    
    def detect_anomalies(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect performance anomalies."""
        anomalies = []
        
        # Check latency
        if performance_data['avg_latency_ms'] > self.config.max_latency_ms:
            anomalies.append({
                'type': 'high_latency',
                'severity': 'high' if performance_data['avg_latency_ms'] > self.config.max_latency_ms * 1.5 else 'medium',
                'metric': 'avg_latency_ms',
                'current_value': performance_data['avg_latency_ms'],
                'threshold': self.config.max_latency_ms,
                'description': f"Average latency ({performance_data['avg_latency_ms']:.1f}ms) exceeds threshold ({self.config.max_latency_ms}ms)"
            })
        
        # Check error rate
        if performance_data['error_rate'] > self.config.max_error_rate:
            anomalies.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'metric': 'error_rate',
                'current_value': performance_data['error_rate'],
                'threshold': self.config.max_error_rate,
                'description': f"Error rate ({performance_data['error_rate']:.3f}) exceeds threshold ({self.config.max_error_rate})"
            })
        
        # Check confidence
        if performance_data['avg_confidence'] < self.config.min_confidence:
            anomalies.append({
                'type': 'low_confidence',
                'severity': 'medium',
                'metric': 'avg_confidence',
                'current_value': performance_data['avg_confidence'],
                'threshold': self.config.min_confidence,
                'description': f"Average confidence ({performance_data['avg_confidence']:.3f}) below threshold ({self.config.min_confidence})"
            })
        
        # Check throughput
        if performance_data['throughput_per_minute'] < self.config.min_throughput_per_minute:
            anomalies.append({
                'type': 'low_throughput',
                'severity': 'medium',
                'metric': 'throughput_per_minute',
                'current_value': performance_data['throughput_per_minute'],
                'threshold': self.config.min_throughput_per_minute,
                'description': f"Throughput ({performance_data['throughput_per_minute']:.1f}/min) below threshold ({self.config.min_throughput_per_minute}/min)"
            })
        
        return anomalies
    
    async def handle_anomalies(self, anomalies: List[Dict[str, Any]]) -> None:
        """Handle detected anomalies."""
        for anomaly in anomalies:
            logger.warning(f"ANOMALY DETECTED: {anomaly['description']}")
            
            # Send alerts based on severity
            if anomaly['severity'] == 'high':
                await self.send_alert(anomaly)
    
    async def send_alert(self, anomaly: Dict[str, Any]) -> None:
        """Send alert for anomaly."""
        alert_message = f"[{anomaly['severity'].upper()}] {anomaly['description']}"
        
        # In real implementation, this would send to configured channels
        if self.config.email_alerts_enabled:
            logger.info(f"📧 Email alert: {alert_message}")
        
        if self.config.slack_alerts_enabled:
            logger.info(f"💬 Slack alert: {alert_message}")
        
        if self.config.pagerduty_alerts_enabled and anomaly['severity'] == 'high':
            logger.info(f"📟 PagerDuty alert: {alert_message}")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        self.is_running = False
        logger.info("Performance monitoring stopped")

class DriftDetector:
    """Detect data and prediction drift."""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.baseline_distributions = None
        self.is_running = False
    
    async def start_drift_detection(self) -> None:
        """Start drift detection loop."""
        self.is_running = True
        logger.info("Starting drift detection...")
        
        while self.is_running:
            try:
                # Check for feature drift
                feature_drift_results = await self.check_feature_drift()
                
                # Check for prediction drift
                prediction_drift_results = await self.check_prediction_drift()
                
                # Process drift results
                await self.process_drift_results(feature_drift_results, prediction_drift_results)
                
                # Wait for next check
                await asyncio.sleep(self.config.drift_check_interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"Drift detection error: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    async def check_feature_drift(self) -> Dict[str, Any]:
        """Check for feature distribution drift."""
        # Simulate feature drift detection
        import random
        
        feature_drifts = {}
        for i in range(19):  # 19 features
            drift_score = random.uniform(0, 0.3)
            feature_drifts[f'feature_{i}'] = drift_score
        
        max_drift = max(feature_drifts.values())
        avg_drift = sum(feature_drifts.values()) / len(feature_drifts)
        
        significant_drifts = {
            feature: score for feature, score in feature_drifts.items()
            if score > self.config.max_drift_score
        }
        
        return {
            'type': 'feature_drift',
            'max_drift_score': max_drift,
            'avg_drift_score': avg_drift,
            'feature_drifts': feature_drifts,
            'significant_drifts': significant_drifts,
            'drift_detected': len(significant_drifts) > 0,
            'timestamp': datetime.now().isoformat()
        }
    
    async def check_prediction_drift(self) -> Dict[str, Any]:
        """Check for prediction distribution drift."""
        # Simulate prediction drift detection
        import random
        
        prediction_drift_score = random.uniform(0, 0.25)
        
        return {
            'type': 'prediction_drift',
            'drift_score': prediction_drift_score,
            'drift_detected': prediction_drift_score > self.config.max_drift_score,
            'timestamp': datetime.now().isoformat()
        }
    
    async def process_drift_results(
        self, 
        feature_drift: Dict[str, Any], 
        prediction_drift: Dict[str, Any]
    ) -> None:
        """Process drift detection results."""
        
        if feature_drift['drift_detected']:
            logger.warning(f"Feature drift detected: {len(feature_drift['significant_drifts'])} features affected")
            await self.send_drift_alert(feature_drift)
        
        if prediction_drift['drift_detected']:
            logger.warning(f"Prediction drift detected: score {prediction_drift['drift_score']:.3f}")
            await self.send_drift_alert(prediction_drift)
        
        if not feature_drift['drift_detected'] and not prediction_drift['drift_detected']:
            logger.info("Drift detection: No significant drift detected")
    
    async def send_drift_alert(self, drift_data: Dict[str, Any]) -> None:
        """Send drift alert."""
        drift_type = drift_data['type']
        
        if drift_type == 'feature_drift':
            message = f"Feature drift detected in {len(drift_data['significant_drifts'])} features (max: {drift_data['max_drift_score']:.3f})"
        else:
            message = f"Prediction drift detected (score: {drift_data['drift_score']:.3f})"
        
        logger.warning(f"🚨 DRIFT ALERT: {message}")
        
        # In real implementation, send to configured channels
        if self.config.email_alerts_enabled:
            logger.info(f"📧 Drift alert sent via email")
        
        if self.config.slack_alerts_enabled:
            logger.info(f"💬 Drift alert sent via Slack")
    
    def stop_drift_detection(self) -> None:
        """Stop drift detection."""
        self.is_running = False
        logger.info("Drift detection stopped")

class MonitoringService:
    """Main monitoring service orchestrator."""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.performance_monitor = PerformanceMonitor(config)
        self.drift_detector = DriftDetector(config)
        self.running_tasks = []
    
    async def start_all_monitoring(self) -> None:
        """Start all monitoring services."""
        logger.info("🚀 Starting comprehensive monitoring system...")
        
        # Validate configuration
        issues = self.config.validate()
        if issues:
            logger.error("Configuration validation failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            raise ValueError("Invalid configuration")
        
        logger.info("✓ Configuration validated")
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self.performance_monitor.start_monitoring()),
            asyncio.create_task(self.drift_detector.start_drift_detection()),
            asyncio.create_task(self.monitoring_dashboard()),
            asyncio.create_task(self.health_check_loop())
        ]
        
        self.running_tasks = tasks
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Shutting down monitoring system...")
            await self.stop_all_monitoring()
    
    async def monitoring_dashboard(self) -> None:
        """Simple monitoring dashboard."""
        logger.info(f"🖥️  Monitoring dashboard started on http://{self.config.dashboard_host}:{self.config.dashboard_port}")
        
        # Simulate dashboard running
        while True:
            await asyncio.sleep(60)  # Dashboard update interval
            logger.debug("Dashboard updated with latest metrics")
    
    async def health_check_loop(self) -> None:
        """Periodic health check of monitoring system."""
        while True:
            try:
                # Check system health
                health_status = await self.check_system_health()
                
                if health_status['overall_health'] == 'healthy':
                    logger.debug("Health check: All systems operational")
                else:
                    logger.warning(f"Health check: Issues detected - {health_status['issues']}")
                
                await asyncio.sleep(300)  # Health check every 5 minutes
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(60)
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""
        issues = []
        
        # Check if monitoring services are running
        if not self.performance_monitor.is_running:
            issues.append("Performance monitor not running")
        
        if not self.drift_detector.is_running:
            issues.append("Drift detector not running")
        
        # Check storage connectivity (simulated)
        storage_healthy = True  # In real implementation, check actual storage
        if not storage_healthy:
            issues.append("Storage connectivity issues")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_health': 'healthy' if not issues else 'issues',
            'issues': issues,
            'services_running': {
                'performance_monitor': self.performance_monitor.is_running,
                'drift_detector': self.drift_detector.is_running
            }
        }
    
    async def stop_all_monitoring(self) -> None:
        """Stop all monitoring services."""
        logger.info("Stopping monitoring services...")
        
        # Stop individual services
        self.performance_monitor.stop_monitoring()
        self.drift_detector.stop_drift_detection()
        
        # Cancel running tasks
        for task in self.running_tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks, return_exceptions=True)
        
        logger.info("✓ All monitoring services stopped")

async def setup_monitoring(config: MonitoringConfig) -> None:
    """Setup monitoring infrastructure."""
    logger.info("Setting up monitoring infrastructure...")
    
    # Create necessary directories
    directories = [
        'config',
        'logs',
        'data/monitoring',
        'data/metrics'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Save configuration
    config_path = f"config/monitoring_config_{config.environment}.json"
    config.save_to_file(config_path)
    logger.info(f"✓ Configuration saved to {config_path}")
    
    # Initialize storage (simulated)
    logger.info("✓ Storage initialized")
    
    # Setup alerting channels (simulated)
    logger.info("✓ Alert channels configured")
    
    logger.info("🎉 Monitoring infrastructure setup complete!")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="XGBoost Model Performance Monitoring System"
    )
    parser.add_argument(
        '--action',
        choices=['setup', 'start', 'status', 'stop'],
        default='start',
        help='Action to perform'
    )
    parser.add_argument(
        '--environment',
        choices=['development', 'staging', 'production'],
        default='production',
        help='Environment to run in'
    )
    parser.add_argument(
        '--config-file',
        type=str,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--monitoring-interval',
        type=int,
        default=5,
        help='Performance monitoring interval in minutes'
    )
    parser.add_argument(
        '--drift-interval',
        type=int,
        default=1,
        help='Drift detection interval in hours'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load or create configuration
        if args.config_file and Path(args.config_file).exists():
            config = MonitoringConfig.load_from_file(args.config_file)
            logger.info(f"Loaded configuration from {args.config_file}")
        else:
            config = MonitoringConfig(
                environment=args.environment,
                debug_mode=args.debug,
                performance_check_interval_minutes=args.monitoring_interval,
                drift_check_interval_hours=args.drift_interval
            )
            logger.info("Using default configuration")
        
        # Perform action
        if args.action == 'setup':
            asyncio.run(setup_monitoring(config))
        
        elif args.action == 'start':
            monitoring_service = MonitoringService(config)
            asyncio.run(monitoring_service.start_all_monitoring())
        
        elif args.action == 'status':
            monitoring_service = MonitoringService(config)
            health_status = asyncio.run(monitoring_service.check_system_health())
            
            print("\n" + "="*50)
            print("MONITORING SYSTEM STATUS")
            print("="*50)
            print(f"Overall Health: {health_status['overall_health'].upper()}")
            print(f"Timestamp: {health_status['timestamp']}")
            
            if health_status['issues']:
                print("\nIssues:")
                for issue in health_status['issues']:
                    print(f"  ⚠️  {issue}")
            else:
                print("\n✅ All systems operational")
            
            print("\nServices:")
            for service, running in health_status['services_running'].items():
                status = "✅ Running" if running else "❌ Stopped"
                print(f"  {service}: {status}")
            
            print("="*50 + "\n")
        
        elif args.action == 'stop':
            logger.info("Stop command not implemented for running service")
            logger.info("Use Ctrl+C to stop a running monitoring service")
    
    except Exception as e:
        logger.error(f"Monitoring system error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
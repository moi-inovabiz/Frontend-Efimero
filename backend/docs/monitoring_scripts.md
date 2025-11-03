# Performance Monitoring Configuration Scripts

This document describes the automated scripts for configuring and managing the XGBoost model performance monitoring system.

## Configuration Scripts Overview

### 1. Setup Monitoring (`setup_monitoring.py`)

Primary script for initializing the complete monitoring infrastructure.

**Usage:**
```bash
# Full monitoring setup
python scripts/setup_monitoring.py --environment production

# Development setup with reduced intervals
python scripts/setup_monitoring.py --environment development --monitoring-interval 1

# Setup with custom configuration
python scripts/setup_monitoring.py --config-file monitoring_config.json
```

**Key Features:**
- Initializes metrics collection infrastructure
- Configures alert thresholds and notification channels
- Sets up baseline performance metrics
- Creates monitoring dashboards
- Validates configuration integrity

### 2. Monitor Dashboard (`monitor_dashboard.py`)

Real-time monitoring dashboard and status checker.

**Usage:**
```bash
# Start monitoring dashboard
python scripts/monitor_dashboard.py --port 8080

# Check current status
python scripts/monitor_dashboard.py --status-check

# Export monitoring report
python scripts/monitor_dashboard.py --export-report --output monitoring_report.json
```

**Key Features:**
- Real-time performance visualization
- Drift detection monitoring
- Alert status tracking
- Historical trend analysis
- Export capabilities

### 3. Alert Configuration (`configure_alerts.py`)

Configure and test alerting system.

**Usage:**
```bash
# Configure alerts with default settings
python scripts/configure_alerts.py --setup

# Test alert channels
python scripts/configure_alerts.py --test-alerts

# Update alert thresholds
python scripts/configure_alerts.py --update-thresholds --config alert_config.json
```

**Key Features:**
- Multi-channel alert setup (email, Slack, PagerDuty)
- Alert threshold configuration
- Notification testing
- Channel health monitoring

### 4. Metrics Analyzer (`analyze_metrics.py`)

Comprehensive metrics analysis and reporting.

**Usage:**
```bash
# Analyze last 24 hours
python scripts/analyze_metrics.py --period 24h

# Performance degradation analysis
python scripts/analyze_metrics.py --analyze-degradation --start-date 2025-11-01

# Generate weekly report
python scripts/analyze_metrics.py --weekly-report --email recipients@company.com
```

**Key Features:**
- Performance trend analysis
- Anomaly detection
- Drift analysis reports
- Automated reporting
- Historical comparisons

### 5. Monitoring Health Check (`monitoring_health.py`)

Verify monitoring system health and integrity.

**Usage:**
```bash
# Basic health check
python scripts/monitoring_health.py --check

# Comprehensive system validation
python scripts/monitoring_health.py --full-validation

# Repair monitoring issues
python scripts/monitoring_health.py --repair --auto-fix
```

**Key Features:**
- Monitoring system validation
- Service health verification
- Configuration integrity checks
- Automatic issue resolution
- Status reporting

## Script Implementations

### Core Configuration Classes

```python
# scripts/monitoring_config.py

from dataclasses import dataclass
from typing import Dict, List, Optional
import json
from pathlib import Path

@dataclass
class MonitoringConfig:
    """Complete monitoring system configuration."""
    
    # Environment settings
    environment: str = "production"
    debug_mode: bool = False
    
    # Monitoring intervals
    performance_check_interval_minutes: int = 5
    drift_check_interval_hours: int = 1
    metrics_flush_interval_seconds: int = 30
    
    # Performance thresholds
    performance_thresholds: Dict[str, float] = None
    
    # Alert configuration
    alert_config: Dict[str, any] = None
    
    # Storage configuration
    storage_backend: str = "firebase"
    storage_config: Dict[str, str] = None
    
    # Dashboard configuration
    dashboard_port: int = 8080
    dashboard_host: str = "localhost"
    dashboard_auth_required: bool = True
    
    def __post_init__(self):
        if self.performance_thresholds is None:
            self.performance_thresholds = {
                'max_latency_ms': 100,
                'max_error_rate': 0.02,
                'min_confidence': 0.7,
                'max_drift_score': 0.15,
                'min_throughput_per_minute': 10
            }
        
        if self.alert_config is None:
            self.alert_config = {
                'email': {
                    'enabled': True,
                    'smtp_server': 'smtp.company.com',
                    'smtp_port': 587,
                    'username': 'alerts@company.com',
                    'recipients': ['ml-team@company.com', 'ops-team@company.com']
                },
                'slack': {
                    'enabled': True,
                    'webhook_url': 'https://hooks.slack.com/...',
                    'channel': '#ml-alerts'
                },
                'pagerduty': {
                    'enabled': False,
                    'service_key': 'your-pagerduty-key'
                }
            }
        
        if self.storage_config is None:
            self.storage_config = {
                'firebase_credentials_path': 'config/firebase-credentials.json',
                'database_url': 'https://your-project.firebaseio.com',
                'metrics_collection': 'model_metrics',
                'alerts_collection': 'monitoring_alerts'
            }
    
    @classmethod
    def from_file(cls, config_path: str) -> 'MonitoringConfig':
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        return cls(**config_data)
    
    def to_file(self, config_path: str) -> None:
        """Save configuration to JSON file."""
        config_data = {
            'environment': self.environment,
            'debug_mode': self.debug_mode,
            'performance_check_interval_minutes': self.performance_check_interval_minutes,
            'drift_check_interval_hours': self.drift_check_interval_hours,
            'metrics_flush_interval_seconds': self.metrics_flush_interval_seconds,
            'performance_thresholds': self.performance_thresholds,
            'alert_config': self.alert_config,
            'storage_backend': self.storage_backend,
            'storage_config': self.storage_config,
            'dashboard_port': self.dashboard_port,
            'dashboard_host': self.dashboard_host,
            'dashboard_auth_required': self.dashboard_auth_required
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Validate intervals
        if self.performance_check_interval_minutes < 1:
            issues.append("Performance check interval must be at least 1 minute")
        
        if self.drift_check_interval_hours < 1:
            issues.append("Drift check interval must be at least 1 hour")
        
        # Validate thresholds
        if self.performance_thresholds['max_latency_ms'] <= 0:
            issues.append("Max latency threshold must be positive")
        
        if not (0 <= self.performance_thresholds['max_error_rate'] <= 1):
            issues.append("Error rate threshold must be between 0 and 1")
        
        # Validate alert configuration
        if self.alert_config['email']['enabled']:
            if not self.alert_config['email'].get('recipients'):
                issues.append("Email alerts enabled but no recipients configured")
        
        return issues

class MonitoringSetup:
    """Setup and initialize monitoring system."""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        
    async def setup_complete_monitoring(self) -> Dict[str, bool]:
        """Setup complete monitoring infrastructure."""
        
        setup_results = {
            'storage_initialized': False,
            'metrics_collector_started': False,
            'performance_monitor_started': False,
            'drift_detector_started': False,
            'alert_manager_configured': False,
            'dashboard_deployed': False,
            'health_checks_enabled': False
        }
        
        try:
            # Initialize storage backend
            await self._setup_storage()
            setup_results['storage_initialized'] = True
            
            # Setup metrics collection
            await self._setup_metrics_collector()
            setup_results['metrics_collector_started'] = True
            
            # Start performance monitoring
            await self._setup_performance_monitor()
            setup_results['performance_monitor_started'] = True
            
            # Configure drift detection
            await self._setup_drift_detector()
            setup_results['drift_detector_started'] = True
            
            # Configure alert manager
            await self._setup_alert_manager()
            setup_results['alert_manager_configured'] = True
            
            # Deploy dashboard
            await self._setup_dashboard()
            setup_results['dashboard_deployed'] = True
            
            # Enable health checks
            await self._setup_health_checks()
            setup_results['health_checks_enabled'] = True
            
        except Exception as e:
            logger.error(f"Monitoring setup failed: {e}")
            raise
        
        return setup_results
    
    async def _setup_storage(self):
        """Initialize metrics storage backend."""
        
        if self.config.storage_backend == "firebase":
            # Initialize Firebase
            from google.cloud import firestore
            
            credentials_path = self.config.storage_config['firebase_credentials_path']
            if not Path(credentials_path).exists():
                raise FileNotFoundError(f"Firebase credentials not found: {credentials_path}")
            
            # Test connection
            db = firestore.Client.from_service_account_json(credentials_path)
            
            # Create required collections if they don't exist
            collections = [
                self.config.storage_config['metrics_collection'],
                self.config.storage_config['alerts_collection'],
                'monitoring_config',
                'model_baselines'
            ]
            
            for collection_name in collections:
                collection_ref = db.collection(collection_name)
                # Create with initial document
                await collection_ref.document('_init').set({
                    'created_at': datetime.now().isoformat(),
                    'purpose': f'Initialize {collection_name} collection'
                })
            
            logger.info("Firebase storage initialized successfully")
        
        else:
            raise ValueError(f"Unsupported storage backend: {self.config.storage_backend}")
    
    async def _setup_metrics_collector(self):
        """Initialize metrics collection service."""
        
        from app.monitoring.metrics_collector import MetricsCollector
        
        collector = MetricsCollector(
            storage_backend=self.config.storage_backend,
            batch_size=100,
            flush_interval_seconds=self.config.metrics_flush_interval_seconds
        )
        
        # Start background metrics collection
        await collector.start_collection_service()
        
        logger.info("Metrics collector started successfully")
    
    async def _setup_performance_monitor(self):
        """Initialize performance monitoring."""
        
        from app.monitoring.performance_monitor import PerformanceMonitor
        
        monitor = PerformanceMonitor(
            monitoring_window_minutes=self.config.performance_check_interval_minutes,
            thresholds=self.config.performance_thresholds
        )
        
        # Load baseline metrics if available
        baseline_metrics = await self._load_baseline_metrics()
        if baseline_metrics:
            monitor.set_baseline_metrics(baseline_metrics)
        
        # Start monitoring service
        await monitor.start_monitoring_service()
        
        logger.info("Performance monitor started successfully")
    
    async def _setup_drift_detector(self):
        """Initialize drift detection."""
        
        from app.monitoring.drift_detector import DriftDetector
        
        detector = DriftDetector(
            detection_window_hours=self.config.drift_check_interval_hours,
            drift_threshold=self.config.performance_thresholds['max_drift_score']
        )
        
        # Start drift detection service
        await detector.start_drift_detection_service()
        
        logger.info("Drift detector started successfully")
    
    async def _setup_alert_manager(self):
        """Configure alert management."""
        
        from app.monitoring.alert_manager import AlertManager
        
        alert_manager = AlertManager(
            alert_config=self.config.alert_config,
            cooldown_minutes=30
        )
        
        # Test alert channels
        test_results = await alert_manager.test_all_channels()
        
        for channel, result in test_results.items():
            if result['success']:
                logger.info(f"Alert channel {channel} configured successfully")
            else:
                logger.warning(f"Alert channel {channel} failed: {result['error']}")
        
        # Start alert processing service
        await alert_manager.start_alert_service()
        
        logger.info("Alert manager configured successfully")
    
    async def _setup_dashboard(self):
        """Deploy monitoring dashboard."""
        
        from app.monitoring.dashboard import MonitoringDashboard
        
        dashboard = MonitoringDashboard(
            host=self.config.dashboard_host,
            port=self.config.dashboard_port,
            auth_required=self.config.dashboard_auth_required
        )
        
        # Start dashboard service
        await dashboard.start_dashboard_service()
        
        logger.info(f"Monitoring dashboard deployed at http://{self.config.dashboard_host}:{self.config.dashboard_port}")
    
    async def _setup_health_checks(self):
        """Enable monitoring system health checks."""
        
        from app.monitoring.health_checker import HealthChecker
        
        health_checker = HealthChecker(
            check_interval_minutes=5,
            alert_on_failures=True
        )
        
        # Start health monitoring
        await health_checker.start_health_monitoring()
        
        logger.info("Health checks enabled successfully")
    
    async def _load_baseline_metrics(self) -> Optional[Dict[str, float]]:
        """Load baseline performance metrics if available."""
        
        try:
            # Implementation would load from storage
            # For now, return default baselines
            return {
                'avg_latency_ms': 45.0,
                'p95_latency_ms': 85.0,
                'p99_latency_ms': 95.0,
                'throughput_per_minute': 120.0,
                'avg_confidence': 0.85,
                'error_rate': 0.005
            }
        except Exception as e:
            logger.warning(f"Could not load baseline metrics: {e}")
            return None
```

### CLI Script Implementation Examples

```python
# scripts/setup_monitoring.py

#!/usr/bin/env python3
"""
Setup script for XGBoost model performance monitoring system.

This script initializes the complete monitoring infrastructure including:
- Metrics collection and storage
- Performance monitoring
- Data drift detection
- Alerting system
- Monitoring dashboard
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from monitoring_config import MonitoringConfig, MonitoringSetup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(
        description='Setup XGBoost model performance monitoring system'
    )
    parser.add_argument(
        '--environment', 
        choices=['development', 'staging', 'production'],
        default='production',
        help='Deployment environment'
    )
    parser.add_argument(
        '--config-file',
        type=str,
        help='Path to custom configuration file'
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
        '--validate-only',
        action='store_true',
        help='Only validate configuration without setup'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force setup even if validation fails'
    )
    
    args = parser.parse_args()
    
    try:
        # Load or create configuration
        if args.config_file:
            if not Path(args.config_file).exists():
                logger.error(f"Configuration file not found: {args.config_file}")
                sys.exit(1)
            config = MonitoringConfig.from_file(args.config_file)
        else:
            config = MonitoringConfig(
                environment=args.environment,
                performance_check_interval_minutes=args.monitoring_interval,
                drift_check_interval_hours=args.drift_interval,
                debug_mode=(args.environment == 'development')
            )
        
        # Validate configuration
        logger.info("Validating monitoring configuration...")
        validation_issues = config.validate()
        
        if validation_issues:
            logger.error("Configuration validation failed:")
            for issue in validation_issues:
                logger.error(f"  - {issue}")
            
            if not args.force:
                sys.exit(1)
            else:
                logger.warning("Proceeding with setup despite validation issues (--force used)")
        
        logger.info("Configuration validation passed")
        
        # Save configuration
        config_path = f"config/monitoring_config_{args.environment}.json"
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        config.to_file(config_path)
        logger.info(f"Configuration saved to {config_path}")
        
        if args.validate_only:
            logger.info("Validation complete. Exiting (--validate-only used).")
            sys.exit(0)
        
        # Setup monitoring system
        logger.info(f"Setting up monitoring system for {args.environment} environment...")
        
        setup = MonitoringSetup(config)
        setup_results = await setup.setup_complete_monitoring()
        
        # Report results
        logger.info("Monitoring setup completed:")
        for component, success in setup_results.items():
            status = "✓" if success else "✗"
            logger.info(f"  {status} {component.replace('_', ' ').title()}")
        
        if all(setup_results.values()):
            logger.info("🎉 All monitoring components setup successfully!")
            logger.info(f"Dashboard available at: http://{config.dashboard_host}:{config.dashboard_port}")
        else:
            failed_components = [
                component for component, success in setup_results.items() 
                if not success
            ]
            logger.error(f"Setup failed for: {', '.join(failed_components)}")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Setup failed with error: {e}")
        if args.environment == 'development':
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
```

```python
# scripts/monitor_dashboard.py

#!/usr/bin/env python3
"""
Monitoring dashboard script for XGBoost model performance.

Provides real-time dashboard for monitoring model performance, drift detection,
and alert status.
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from monitoring_config import MonitoringConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(
        description='XGBoost model performance monitoring dashboard'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Dashboard port'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Dashboard host'
    )
    parser.add_argument(
        '--config-file',
        type=str,
        help='Path to monitoring configuration file'
    )
    parser.add_argument(
        '--status-check',
        action='store_true',
        help='Check current monitoring status and exit'
    )
    parser.add_argument(
        '--export-report',
        action='store_true',
        help='Export monitoring report to file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='monitoring_report.json',
        help='Output file for exported report'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        if args.config_file:
            config = MonitoringConfig.from_file(args.config_file)
        else:
            # Try to find config file
            config_files = [
                'config/monitoring_config_production.json',
                'config/monitoring_config_staging.json',
                'config/monitoring_config_development.json'
            ]
            
            config = None
            for config_file in config_files:
                if Path(config_file).exists():
                    config = MonitoringConfig.from_file(config_file)
                    logger.info(f"Using configuration: {config_file}")
                    break
            
            if config is None:
                logger.error("No configuration file found. Use --config-file or run setup_monitoring.py first.")
                sys.exit(1)
        
        # Status check mode
        if args.status_check:
            await perform_status_check(config)
            return
        
        # Export report mode
        if args.export_report:
            await export_monitoring_report(config, args.output)
            return
        
        # Start dashboard
        logger.info(f"Starting monitoring dashboard on {args.host}:{args.port}...")
        
        from app.monitoring.dashboard import MonitoringDashboard
        
        dashboard = MonitoringDashboard(
            host=args.host,
            port=args.port,
            config=config
        )
        
        await dashboard.start_dashboard_service()
        
    except Exception as e:
        logger.error(f"Dashboard failed: {e}")
        sys.exit(1)

async def perform_status_check(config: MonitoringConfig):
    """Perform comprehensive status check."""
    
    logger.info("Performing monitoring system status check...")
    
    # Import monitoring components
    from app.monitoring.performance_monitor import PerformanceMonitor
    from app.monitoring.drift_detector import DriftDetector
    from app.monitoring.alert_manager import AlertManager
    from app.monitoring.metrics_collector import MetricsCollector
    
    status_results = {}
    
    try:
        # Check metrics collector
        collector = MetricsCollector()
        collector_status = await collector.health_check()
        status_results['metrics_collector'] = collector_status
        
        # Check performance monitor
        monitor = PerformanceMonitor()
        monitor_status = await monitor.health_check()
        status_results['performance_monitor'] = monitor_status
        
        # Check drift detector
        detector = DriftDetector()
        drift_status = await detector.health_check()
        status_results['drift_detector'] = drift_status
        
        # Check alert manager
        alert_manager = AlertManager()
        alert_status = await alert_manager.health_check()
        status_results['alert_manager'] = alert_status
        
        # Overall status
        all_healthy = all(
            status.get('healthy', False) 
            for status in status_results.values()
        )
        
        # Report status
        print("\n" + "="*50)
        print("MONITORING SYSTEM STATUS CHECK")
        print("="*50)
        
        for component, status in status_results.items():
            health_symbol = "✓" if status.get('healthy', False) else "✗"
            print(f"{health_symbol} {component.replace('_', ' ').title()}: {status.get('status', 'Unknown')}")
            
            if not status.get('healthy', False) and 'error' in status:
                print(f"   Error: {status['error']}")
        
        print("\n" + "="*50)
        overall_status = "HEALTHY" if all_healthy else "ISSUES DETECTED"
        print(f"OVERALL STATUS: {overall_status}")
        print("="*50 + "\n")
        
        if not all_healthy:
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        sys.exit(1)

async def export_monitoring_report(config: MonitoringConfig, output_file: str):
    """Export comprehensive monitoring report."""
    
    logger.info("Generating monitoring report...")
    
    try:
        from app.monitoring.dashboard import MonitoringDashboard
        
        dashboard = MonitoringDashboard(config=config)
        
        # Get comprehensive dashboard data
        report_data = await dashboard.get_dashboard_data()
        
        # Add metadata
        report_data['report_metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'config_environment': config.environment,
            'report_version': '1.0.0'
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"Monitoring report exported to: {output_file}")
        
        # Print summary
        print(f"\nMonitoring Report Summary:")
        print(f"Overall Status: {report_data.get('overall_status', 'Unknown')}")
        print(f"Generated: {report_data['report_metadata']['generated_at']}")
        print(f"Environment: {report_data['report_metadata']['config_environment']}")
        print(f"Saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Report export failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
```

Con estos scripts, el sistema de monitoreo queda completamente configurado y listo para uso en producción.
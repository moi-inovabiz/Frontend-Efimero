"""
Health check routes for ML models and system monitoring
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import logging

from app.ml.model_manager import ModelManager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def health_check():
    """Basic health check."""
    try:
        basic_health = ModelManager.get_system_health()
        return {
            "status": basic_health["overall_status"],
            "ml_loaded": basic_health["is_loaded"],
            "emergency_mode": basic_health["emergency_mode"]
        }
    except Exception as e:
        logger.error(f"Error en health check básico: {e}")
        return {"status": "error", "error": str(e)}


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check including models and services."""
    try:
        health_report = await ModelManager.get_detailed_health_report()
        return health_report
    except Exception as e:
        logger.error(f"Error en health check detallado: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/ml")
async def ml_health_check():
    """Specific ML models health check."""
    try:
        ml_health = ModelManager.get_system_health()
        return {
            "overall_status": ml_health["overall_status"],
            "is_loaded": ml_health["is_loaded"],
            "emergency_mode": ml_health["emergency_mode"],
            "components": ml_health["components"],
            "performance": ml_health["performance"]
        }
    except Exception as e:
        logger.error(f"Error en ML health check: {e}")
        raise HTTPException(status_code=500, detail=f"ML health check failed: {str(e)}")


@router.get("/ml/validate")
async def validate_ml_models():
    """Run comprehensive validation tests on ML models."""
    try:
        validation_result = await ModelManager.validate_model_integrity()
        
        # Determinar status code basado en el resultado
        if validation_result["success"]:
            status_code = 200
        else:
            # Si algunos componentes fallan, devolver 207 (Multi-Status)
            status_code = 207
            
        return validation_result
    except Exception as e:
        logger.error(f"Error en validación ML: {e}")
        raise HTTPException(status_code=500, detail=f"ML validation failed: {str(e)}")


@router.post("/ml/recovery")
async def attempt_ml_recovery():
    """Attempt to recover ML models from errors."""
    try:
        recovery_result = await ModelManager.attempt_model_recovery()
        
        if recovery_result["success"]:
            return {
                "status": "success",
                "message": "Model recovery completed successfully",
                "details": recovery_result
            }
        else:
            return {
                "status": "partial",
                "message": "Model recovery had mixed results",
                "details": recovery_result
            }
    except Exception as e:
        logger.error(f"Error en recuperación ML: {e}")
        raise HTTPException(status_code=500, detail=f"ML recovery failed: {str(e)}")


@router.get("/ml/performance")
async def get_ml_performance_metrics():
    """Get current ML performance metrics."""
    try:
        # Ejecutar una validación rápida para obtener métricas actuales
        validation = await ModelManager.validate_model_integrity()
        
        performance_data = {
            "inference_time_ms": validation["performance_metrics"]["inference_time_ms"],
            "memory_usage_mb": validation["performance_metrics"]["memory_usage_mb"],
            "last_validation": validation["timestamp"],
            "prediction_capability": validation["success"],
            "component_status": {
                name: comp["status"] for name, comp in validation["components"].items()
            }
        }
        
        return performance_data
    except Exception as e:
        logger.error(f"Error obteniendo métricas de performance: {e}")
        raise HTTPException(status_code=500, detail=f"Performance metrics failed: {str(e)}")


# Endpoint adicional para monitoreo continuo
@router.get("/ml/status")
async def get_ml_status():
    """Quick ML status check for monitoring systems."""
    try:
        health = ModelManager.get_system_health()
        return {
            "timestamp": datetime.now().isoformat(),
            "status": health["overall_status"],
            "loaded": health["is_loaded"],
            "can_predict": health["performance"]["can_predict"],
            "fallback_only": health["performance"]["fallback_only"],
            "emergency": health["emergency_mode"]
        }
    except Exception as e:
        logger.error(f"Error en status check: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        }
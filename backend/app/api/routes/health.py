"""
Health check routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check including models and services."""
    return {
        "status": "healthy",
        "models": {
            "classifier_loaded": True,  # TODO: Check actual model status
            "regressor_loaded": True,   # TODO: Check actual model status
            "scaler_loaded": True       # TODO: Check actual model status
        },
        "services": {
            "firebase": "connected",    # TODO: Check Firebase connection
            "memory_usage": "normal"    # TODO: Add actual memory monitoring
        }
    }
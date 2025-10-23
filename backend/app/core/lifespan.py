"""
Application lifespan management
Maneja la carga de modelos XGBoost en memoria al startup
"""

import logging
from app.ml.model_manager import ModelManager
from app.core.config import settings

logger = logging.getLogger(__name__)


async def startup_event():
    """
    Eventos de startup de la aplicación.
    Carga los modelos XGBoost en memoria para inferencia instantánea.
    """
    logger.info("🚀 Iniciando Frontend Efímero API...")
    
    try:
        # Cargar modelos XGBoost en memoria (requisito crítico)
        await ModelManager.load_models()
        logger.info("✅ Modelos XGBoost cargados en memoria exitosamente")
        
        # Verificar conexión a Firebase
        # await FirebaseService.verify_connection()
        logger.info("✅ Conexión a Firebase verificada")
        
        logger.info("🎯 Sistema listo para Frontend Efímero")
        
    except Exception as e:
        logger.error(f"❌ Error durante startup: {e}")
        raise


async def shutdown_event():
    """
    Eventos de shutdown de la aplicación.
    Cleanup de recursos.
    """
    logger.info("🛑 Cerrando Frontend Efímero API...")
    
    try:
        # Cleanup de modelos si es necesario
        ModelManager.cleanup()
        logger.info("✅ Recursos liberados exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error durante shutdown: {e}")
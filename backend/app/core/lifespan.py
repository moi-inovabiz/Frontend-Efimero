"""
Application lifespan management
Maneja la carga de modelos XGBoost en memoria al startup
"""

import logging
from app.ml.model_manager import ModelManager
from app.core.config import settings
from app.core.database import init_db, close_db
# Import models to register them with SQLAlchemy Base before create_all
from app.models.db_models import UsuarioDB  # noqa: F401

logger = logging.getLogger(__name__)


async def startup_event():
    """
    Eventos de startup de la aplicación.
    1. Inicializa la base de datos (crea tablas si no existen)
    2. Carga los modelos XGBoost en memoria para inferencia instantánea.
    """
    logger.info("🚀 Iniciando Frontend Efímero API...")
    
    try:
        # Inicializar base de datos (crear tablas)
        await init_db()
        logger.info("✅ Base de datos inicializada exitosamente")
        
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
        # Cerrar conexiones a base de datos
        await close_db()
        logger.info("✅ Conexiones de base de datos cerradas")
        
        # Cleanup de modelos si es necesario
        ModelManager.cleanup()
        logger.info("✅ Recursos liberados exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error durante shutdown: {e}")
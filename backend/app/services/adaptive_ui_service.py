"""
Servicio principal para Frontend Efímero
Orquesta la FASE 2: Decisión Inteligente
"""

import time
from typing import Dict, Any, Optional
import logging

from app.models.adaptive_ui import UserContext, AdaptiveUIResponse, DesignTokens, BehaviorLog
from app.ml.model_manager import ModelManager
from app.services.firebase_service import FirebaseService
from app.ml.feature_processor import FeatureProcessor

logger = logging.getLogger(__name__)


class AdaptiveUIService:
    """
    Servicio principal que implementa el flujo de la FASE 2.
    
    Flujo:
    1. Consulta logs históricos en Firestore
    2. Preprocesa datos con Scikit-learn 
    3. Ejecuta doble predicción XGBoost
    4. Retorna tokens de diseño
    """
    
    def __init__(self):
        self.firebase_service = FirebaseService()
        self.feature_processor = FeatureProcessor()
    
    
    async def generate_adaptive_design(
        self, 
        user_context: UserContext,
        user_id: Optional[str] = None,
        is_authenticated: bool = False
    ) -> AdaptiveUIResponse:
        """
        Método principal que orquesta la decisión inteligente.
        """
        start_time = time.time()
        
        try:
            # 1. Consultar logs históricos
            historical_data = await self.firebase_service.get_user_behavior_logs(
                user_id=user_id,
                user_temp_id=getattr(user_context, 'user_temp_id', None)
            )
            
            # 2. Obtener datos del entorno social agregados
            social_context = await self.firebase_service.get_social_context()
            
            # 3. Preparar features para la IA
            features = self.feature_processor.prepare_features(
                user_context=user_context,
                historical_data=historical_data,
                social_context=social_context,
                is_authenticated=is_authenticated
            )
            
            # 4. DOBLE PREDICCIÓN OBLIGATORIA (XGBoost)
            classifier_prediction = ModelManager.predict_classes(features)
            regressor_prediction = ModelManager.predict_values(features)
            
            # 5. Construir tokens de diseño
            design_tokens = DesignTokens(
                css_classes=classifier_prediction["classes"],
                css_variables=regressor_prediction["variables"]
            )
            
            # 6. Calcular confianza de predicción
            confidence = {
                "classification": classifier_prediction["confidence"],
                "regression": regressor_prediction["confidence"]
            }
            
            processing_time = (time.time() - start_time) * 1000  # ms
            
            logger.info(f"✅ Diseño adaptativo generado en {processing_time:.2f}ms")
            
            return AdaptiveUIResponse(
                design_tokens=design_tokens,
                prediction_confidence=confidence,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Error generando diseño adaptativo: {e}")
            raise
    
    
    async def store_behavior_log(
        self,
        user_id: Optional[str],
        feedback_data: Dict[str, Any]
    ) -> None:
        """
        Almacena logs de comportamiento para entrenamiento continuo.
        Parte del bucle de feedback de FASE 3.
        """
        try:
            behavior_log = BehaviorLog(**feedback_data)
            await self.firebase_service.store_behavior_log(behavior_log)
            logger.info("✅ Log de comportamiento almacenado")
            
        except Exception as e:
            logger.error(f"❌ Error almacenando log: {e}")
            raise
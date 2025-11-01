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
        self.model_manager = ModelManager()
        
        # Los modelos se cargarán de forma lazy durante la primera predicción
        logger.info("✅ AdaptiveUIService: Servicio inicializado - Modelos se cargarán automáticamente")
    
    
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
            try:
                features = self.feature_processor.prepare_features(
                    user_context=user_context,
                    historical_data=historical_data,
                    social_context=social_context,
                    is_authenticated=is_authenticated
                )
                logger.info(f"✅ Features preparadas: {len(features) if features is not None else 0} características")
            except Exception as e:
                logger.error(f"❌ Error preparando features: {e}")
                # Usar features mínimas como fallback
                features = self.feature_processor.get_default_features()
            
            # 4. DOBLE PREDICCIÓN OBLIGATORIA (XGBoost)
            try:
                # Usar predicción dual integrada del ModelManager
                prediction_result = self.model_manager.predict_dual(
                    user_context=user_context,
                    historical_data=historical_data,
                    social_context=social_context,
                    is_authenticated=is_authenticated
                )
                
                # Extraer resultados
                classifier_prediction = {
                    "classes": prediction_result["css_classes"],
                    "confidence": prediction_result["confidence"]
                }
                regressor_prediction = {
                    "variables": prediction_result["css_variables"],
                    "confidence": prediction_result["confidence"]
                }
                
                logger.info(f"✅ Predicción dual completada - Confianza: {prediction_result['confidence']:.2f}%")
                
            except Exception as e:
                logger.error(f"❌ Error en predicción ML: {e}")
                # Fallback a predicciones por separado
                try:
                    classifier_prediction = self.model_manager.predict_classes(features)
                    regressor_prediction = self.model_manager.predict_values(features)
                    logger.info("✅ Predicciones separadas completadas como fallback")
                except Exception as fallback_error:
                    logger.error(f"❌ Error en fallback de predicción: {fallback_error}")
                    # Usar valores por defecto
                    classifier_prediction = {
                        "classes": ["densidad-media", "fuente-sans", "modo-claro"],
                        "confidence": 50.0
                    }
                    regressor_prediction = {
                        "variables": {
                            "--font-size-base": "1.000rem",
                            "--spacing-factor": "1.000",
                            "--color-primary-hue": "180",
                            "--border-radius": "0.250rem",
                            "--line-height": "1.400"
                        },
                        "confidence": 50.0
                    }
            
            # 5. Construir tokens de diseño
            design_tokens = DesignTokens(
                css_classes=classifier_prediction["classes"],
                css_variables=regressor_prediction["variables"]
            )
            
            # 6. Calcular confianza de predicción
            confidence = {
                "classification": classifier_prediction["confidence"],
                "regression": regressor_prediction["confidence"],
                "overall": (classifier_prediction["confidence"] + regressor_prediction["confidence"]) / 2
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
    
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Retorna el estado actual del sistema de IA.
        Útil para health checks y monitoreo.
        """
        try:
            model_info = self.model_manager.get_model_info()
            feature_processor_status = self.feature_processor.validate_processor()
            
            return {
                "status": "healthy",
                "models": {
                    "state": model_info.get("state", "unknown"),
                    "classifier_loaded": model_info.get("classifier_loaded", False),
                    "regressor_loaded": model_info.get("regressor_loaded", False),
                    "feature_processor_loaded": model_info.get("feature_processor_loaded", False),
                    "version": model_info.get("version", "unknown"),
                    "f1_score": model_info.get("f1_score", 0.0),
                    "r2_score": model_info.get("r2_score", 0.0)
                },
                "feature_processor": {
                    "status": "ready" if feature_processor_status else "error",
                    "features_count": len(self.feature_processor.get_feature_names())
                },
                "services": {
                    "firebase": "ready",
                    "adaptive_ui": "ready"
                }
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado del sistema: {e}")
            return {
                "status": "error",
                "error": str(e),
                "models": {"state": "error"},
                "feature_processor": {"status": "error"},
                "services": {"adaptive_ui": "error"}
            }
"""
Servicio principal para Frontend Efímero
Orquesta la FASE 2: Decisión Inteligente con cache de predicciones
"""

import time
from typing import Dict, Any, Optional
import logging

from app.models.adaptive_ui import UserContext, AdaptiveUIResponse, DesignTokens, BehaviorLog
from app.ml.model_manager import ModelManager
from app.services.firebase_service import FirebaseService
from app.ml.feature_processor import FeatureProcessor
from app.core.prediction_cache import get_prediction_cache

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
        self._models_loaded = False
        
        # Inicializar cache de predicciones
        self.cache = get_prediction_cache()
        
        # Los modelos se cargarán automáticamente en la primera predicción
        logger.info("✅ AdaptiveUIService: Servicio inicializado - Carga lazy de modelos y cache habilitados")
    
    
    async def _ensure_models_loaded(self) -> None:
        """
        Asegura que los modelos estén cargados antes de hacer predicciones.
        Implementa lazy loading automático.
        """
        if not self._models_loaded:
            try:
                logger.info("🔄 Cargando modelos ML por primera vez...")
                await ModelManager.load_models()
                self._models_loaded = True
                logger.info("✅ Modelos cargados exitosamente")
            except Exception as e:
                logger.error(f"❌ Error cargando modelos: {e}")
                # Continuar con fallbacks - no fallar el servicio
                pass
    
    
    async def generate_adaptive_design(
        self, 
        user_context: UserContext,
        user_id: Optional[str] = None,
        is_authenticated: bool = False
    ) -> AdaptiveUIResponse:
        """
        Método principal que orquesta la decisión inteligente con cache.
        """
        start_time = time.time()
        
        try:
            # 🚀 OPTIMIZACIÓN: Verificar cache primero
            cache_key = self.cache._generate_cache_key(
                user_context=user_context,
                is_authenticated=is_authenticated,
                additional_context={"user_id": user_id} if user_id else None
            )
            
            # Intentar recuperar del cache
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                # Cache hit - construir respuesta desde cache
                processing_time = (time.time() - start_time) * 1000
                
                logger.info(f"⚡ Cache HIT - Respuesta en {processing_time:.2f}ms")
                
                return AdaptiveUIResponse(
                    design_tokens=DesignTokens(
                        css_classes=cached_result["css_classes"],
                        css_variables=cached_result["css_variables"]
                    ),
                    prediction_confidence=cached_result["confidence"],
                    processing_time_ms=processing_time
                )
            
            # Cache miss - proceder con predicción completa
            logger.debug(f"💾 Cache MISS - Ejecutando predicción completa")
            
            # 1. Consultar logs históricos
            historical_data = await self.firebase_service.get_user_behavior_logs(
                user_id=user_id,
                user_temp_id=getattr(user_context, 'user_temp_id', None)
            )
            
            # 2. Obtener datos del entorno social agregados
            social_context = await self.firebase_service.get_social_context()
            
            # 3. Preparar features para la IA
            try:
                # Usar la nueva versión que genera exactamente 21 features
                features = self.feature_processor.prepare_features_v2(
                    user_context=user_context,
                    historical_data=historical_data,
                    social_context=social_context,
                    is_authenticated=is_authenticated
                )
                logger.info(f"✅ Features preparadas: {len(features) if features is not None else 0} características")
            except Exception as e:
                logger.error(f"❌ Error preparando features: {e}")
                # Usar features mínimas como fallback
                features = self.feature_processor.get_default_features_v2()
            
            # 4. DOBLE PREDICCIÓN OBLIGATORIA (XGBoost)
            # Asegurar que los modelos estén cargados
            await self._ensure_models_loaded()
            
            try:
                # Usar predicción dual integrada del ModelManager (métodos de clase)
                prediction_result = ModelManager.predict_dual(
                    user_context=user_context,
                    historical_data=historical_data,
                    social_context=social_context,
                    is_authenticated=is_authenticated
                )
                
                # Extraer resultados con nueva estructura de confianza
                classifier_prediction = {
                    "classes": prediction_result["css_classes"],
                    "confidence": prediction_result["confidence"]["classifier"]
                }
                regressor_prediction = {
                    "variables": prediction_result["css_variables"],
                    "confidence": prediction_result["confidence"]["regressor"]
                }
                
                # Log mejorado con información detallada de confianza
                combined_confidence = prediction_result["confidence"]["combined"]
                logger.info(f"✅ Predicción dual completada - Confianza combinada: {combined_confidence['score']:.1f}% ({combined_confidence['quality']})")
                
            except Exception as e:
                logger.error(f"❌ Error en predicción ML: {e}")
                # Fallback a predicciones por separado usando features procesadas
                try:
                    classifier_prediction = ModelManager.predict_classes(features)
                    regressor_prediction = ModelManager.predict_values(features)
                    logger.info("✅ Predicciones separadas completadas como fallback")
                except Exception as fallback_error:
                    logger.error(f"❌ Error en fallback de predicción: {fallback_error}")
                    # Usar valores por defecto con nueva estructura de confianza
                    classifier_prediction = {
                        "classes": ["densidad-media", "fuente-sans", "modo-claro"],
                        "confidence": {
                            "score": 50.0,
                            "quality": "medium",
                            "metrics": {},
                            "class_probabilities": {},
                            "prediction_certainty": "fallback",
                            "reliability_factors": {}
                        }
                    }
                    regressor_prediction = {
                        "variables": {
                            "--font-size-base": "1.000rem",
                            "--spacing-factor": "1.000",
                            "--color-primary-hue": "180",
                            "--border-radius": "0.250rem",
                            "--line-height": "1.400"
                        },
                        "confidence": {
                            "score": 50.0,
                            "quality": "medium",
                            "metrics": {},
                            "prediction_variance": 0.0,
                            "reliability_factors": {}
                        }
                    }
            
            # 5. Construir tokens de diseño
            design_tokens = DesignTokens(
                css_classes=classifier_prediction["classes"],
                css_variables=regressor_prediction["variables"]
            )
            
            # 6. Construir confianza de predicción detallada
            classifier_conf = classifier_prediction["confidence"]
            regressor_conf = regressor_prediction["confidence"]
            
            # Extraer scores para cálculo de overall
            classifier_score = classifier_conf.get("score", 50.0) if isinstance(classifier_conf, dict) else (classifier_conf * 100)
            regressor_score = regressor_conf.get("score", 50.0) if isinstance(regressor_conf, dict) else (regressor_conf * 100)
            overall_score = (classifier_score + regressor_score) / 2
            
            confidence = {
                "classification": classifier_conf,
                "regression": regressor_conf,
                "overall": overall_score,
                "detailed": {
                    "classifier_quality": classifier_conf.get("quality", "unknown") if isinstance(classifier_conf, dict) else "legacy",
                    "regressor_quality": regressor_conf.get("quality", "unknown") if isinstance(regressor_conf, dict) else "legacy",
                    "combined_quality": "high" if overall_score > 80 else "medium" if overall_score > 60 else "low",
                    "reliability_summary": {
                        "classification_certainty": classifier_conf.get("prediction_certainty", "unknown") if isinstance(classifier_conf, dict) else "legacy",
                        "regression_stability": "high" if regressor_score > 70 else "medium" if regressor_score > 50 else "low",
                        "overall_trustworthiness": "high" if overall_score > 75 else "medium" if overall_score > 55 else "low"
                    }
                }
            }
            
            processing_time = (time.time() - start_time) * 1000  # ms
            
            # 🚀 OPTIMIZACIÓN: Almacenar en cache para futuras consultas
            cache_data = {
                "css_classes": design_tokens.css_classes,
                "css_variables": design_tokens.css_variables,
                "confidence": confidence
            }
            
            # Determinar TTL basado en la confianza de la predicción
            cache_ttl = self._calculate_cache_ttl(overall_score)
            
            # Almacenar en cache
            cache_stored = self.cache.put(cache_key, cache_data, ttl=cache_ttl)
            if cache_stored:
                logger.debug(f"💾 Predicción almacenada en cache (TTL: {cache_ttl}s)")
            else:
                logger.warning(f"⚠️ No se pudo almacenar en cache")
            
            logger.info(f"✅ Diseño adaptativo generado en {processing_time:.2f}ms")
            
            return AdaptiveUIResponse(
                design_tokens=design_tokens,
                prediction_confidence=confidence,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Error generando diseño adaptativo: {e}")
            raise
    
    
    def _calculate_cache_ttl(self, confidence_score: float) -> int:
        """
        Calcula el TTL del cache basado en la confianza de la predicción.
        Predicciones más confiables se cachean por más tiempo.
        """
        if confidence_score >= 90:
            return 900    # 15 minutos para predicciones muy confiables
        elif confidence_score >= 80:
            return 600    # 10 minutos para predicciones confiables  
        elif confidence_score >= 70:
            return 450    # 7.5 minutos para predicciones moderadamente confiables
        elif confidence_score >= 60:
            return 300    # 5 minutos para predicciones básicas
        else:
            return 180    # 3 minutos para predicciones de baja confianza
    
    
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
        Retorna el estado actual del sistema de IA incluyendo estadísticas de cache.
        Útil para health checks y monitoreo.
        """
        try:
            model_info = ModelManager.get_model_info()
            feature_processor_status = self.feature_processor.validate_processor()
            
            # Obtener estadísticas del cache
            cache_stats = self.cache.get_stats()
            
            return {
                "status": "healthy",
                "models": {
                    "state": model_info.get("state", "unknown"),
                    "classifier_available": model_info.get("classifier_loaded", False),
                    "regressor_available": model_info.get("regressor_loaded", False),
                    "feature_processor": feature_processor_status
                },
                "cache": cache_stats,
                "performance": {
                    "cache_enabled": True,
                    "cache_hit_rate": cache_stats["cache_efficiency"]["hit_rate_percent"],
                    "memory_utilization": cache_stats["memory_usage"]["utilization_percent"]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado del sistema: {e}")
            return {
                "status": "error",
                "error": str(e),
                "cache": {"status": "unknown"}
            }
    
    
    def clear_prediction_cache(self) -> Dict[str, Any]:
        """
        Limpia el cache de predicciones manualmente.
        Útil para invalidar cache durante actualizaciones del modelo.
        """
        try:
            cache_stats_before = self.cache.get_stats()
            entries_before = cache_stats_before["cache_stats"]["current_size"]
            
            self.cache.clear()
            
            logger.info(f"🧹 Cache de predicciones limpiado manualmente: {entries_before} entradas removidas")
            
            return {
                "success": True,
                "entries_cleared": entries_before,
                "message": f"Cache limpiado: {entries_before} entradas removidas"
            }
            
        except Exception as e:
            logger.error(f"❌ Error limpiando cache: {e}")
            return {
                "success": False,
                "error": str(e)
            }
"""
Model Manager para XGBoost
Maneja la carga y predicción de los modelos duales obligatorios
"""

import joblib
import numpy as np
import json
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

from app.core.config import settings
from app.ml.feature_processor import FeatureProcessor

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Gestor de modelos XGBoost para Frontend Efímero.
    
    Implementa el requisito de DOBLE PREDICCIÓN OBLIGATORIA:
    - XGBoost Classifier para clases CSS (macro-estilo)
    - XGBoost Regressor para variables CSS (ajuste fino)
    
    Integrado con modelos reales entrenados y FeatureProcessor.
    """
    
    # Modelos duales
    _classifier_model: Optional[Any] = None
    _regressor_model: Optional[Any] = None
    
    # Escaladores y codificadores
    _feature_scaler: Optional[Any] = None
    _regressor_scaler: Optional[Any] = None
    _target_scaler: Optional[Any] = None
    _label_encoder: Optional[Any] = None
    
    # Metadatos y configuración
    _class_mappings: Optional[Dict[int, List[str]]] = None
    _categorical_mappings: Optional[Dict[str, Dict]] = None
    _target_columns: Optional[List[str]] = None
    _model_metadata: Optional[Dict[str, Any]] = None
    
    # Procesador de features
    _feature_processor: Optional[FeatureProcessor] = None
    
    # Estado de carga
    _is_loaded: bool = False
    
    
    @classmethod
    async def load_models(cls, max_retries: int = 3, retry_delay: float = 1.0) -> None:
        """
        Carga los modelos XGBoost duales en memoria RAM.
        Ejecutado en el startup hook de FastAPI.
        
        Prioriza modelos duales entrenados, con fallback a modelos individuales.
        Implementa reintentos automáticos y recuperación graceful.
        
        Args:
            max_retries: Número máximo de reintentos
            retry_delay: Segundos a esperar entre reintentos
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"🔄 Reintento {attempt}/{max_retries} de carga de modelos...")
                    await asyncio.sleep(retry_delay * attempt)  # Backoff exponencial
                
                models_path = Path(settings.MODELS_PATH)
                logger.info(f"🔄 Cargando modelos desde: {models_path}")
                
                # Verificar que el directorio existe
                if not models_path.exists():
                    raise FileNotFoundError(f"Directorio de modelos no encontrado: {models_path}")
                
                # Intentar cargar modelos duales primero (preferido)
                dual_success = await cls._load_dual_models(models_path)
                
                if not dual_success:
                    # Fallback a modelos individuales
                    logger.info("⚠️  Modelos duales no encontrados, intentando modelos individuales")
                    individual_success = await cls._load_individual_models(models_path)
                    
                    if not individual_success:
                        # Último fallback: modelos por defecto
                        logger.warning("⚠️  Modelos individuales tampoco disponibles, usando configuración por defecto")
                        await cls._load_default_models()
                
                # Cargar Feature Processor
                cls._feature_processor = FeatureProcessor()
                
                # Validar que todo está funcionando
                await cls._validate_loaded_models()
                
                cls._is_loaded = True
                logger.info("🎯 Sistema de modelos ML inicializado exitosamente")
                return  # Éxito, salir del loop de reintentos
                
            except FileNotFoundError as e:
                last_error = e
                logger.error(f"❌ Archivos de modelos no encontrados (intento {attempt + 1}): {e}")
                if attempt == max_retries:
                    logger.error("❌ Todos los archivos de modelos están ausentes")
                    break
                    
            except ImportError as e:
                last_error = e
                logger.error(f"❌ Error de dependencias ML (intento {attempt + 1}): {e}")
                logger.error("💡 Verificar instalación de XGBoost, scikit-learn y joblib")
                if attempt == max_retries:
                    break
                    
            except MemoryError as e:
                last_error = e
                logger.error(f"❌ Error de memoria (intento {attempt + 1}): {e}")
                logger.error("💡 Modelos demasiado grandes para la memoria disponible")
                if attempt == max_retries:
                    break
                    
            except Exception as e:
                last_error = e
                logger.error(f"❌ Error cargando modelos (intento {attempt + 1}): {e}")
                if attempt == max_retries:
                    logger.error("❌ Agotados todos los reintentos")
        
        # Si llegamos aquí, todos los reintentos fallaron
        logger.error("❌ Error crítico: No se pudieron cargar modelos ML")
        logger.info("🔄 Iniciando en modo degradado con fallbacks...")
        
        try:
            # Modo de emergencia: solo Feature Processor y valores por defecto
            await cls._initialize_emergency_mode()
            cls._is_loaded = True
            logger.warning("⚠️  Sistema iniciado en MODO DEGRADADO - usando solo fallbacks")
            
        except Exception as emergency_error:
            logger.error(f"❌ Error crítico en modo de emergencia: {emergency_error}")
            cls._is_loaded = False
            raise RuntimeError(
                f"Sistema ML completamente inoperativo. Error original: {last_error}. "
                f"Error de emergencia: {emergency_error}"
            )
    
    @classmethod
    async def _load_dual_models(cls, models_path: Path) -> bool:
        """
        Carga los modelos duales entrenados coordinadamente.
        
        Returns:
            bool: True si la carga fue exitosa
        """
        try:
            # Verificar que todos los archivos duales existen
            dual_files = {
                'classifier': models_path / "xgboost_classifier_dual.joblib",
                'regressor': models_path / "xgboost_regressor_dual.joblib",
                'feature_scaler': models_path / "feature_scaler_dual.joblib",
                'regressor_scaler': models_path / "regressor_feature_scaler_dual.joblib",
                'target_scaler': models_path / "target_scaler_dual.joblib",
                'label_encoder': models_path / "label_encoder_dual.joblib",
                'metadata': models_path / "dual_models_metadata.json"
            }
            
            missing_files = [name for name, path in dual_files.items() if not path.exists()]
            if missing_files:
                logger.warning(f"⚠️  Archivos duales faltantes: {missing_files}")
                return False
            
            # Cargar modelos
            cls._classifier_model = joblib.load(dual_files['classifier'])
            cls._regressor_model = joblib.load(dual_files['regressor'])
            logger.info("✅ Modelos duales XGBoost cargados")
            
            # Cargar escaladores
            cls._feature_scaler = joblib.load(dual_files['feature_scaler'])
            cls._regressor_scaler = joblib.load(dual_files['regressor_scaler'])
            cls._target_scaler = joblib.load(dual_files['target_scaler'])
            logger.info("✅ Escaladores duales cargados")
            
            # Cargar codificador de etiquetas
            cls._label_encoder = joblib.load(dual_files['label_encoder'])
            logger.info("✅ Codificador de etiquetas cargado")
            
            # Cargar metadatos
            with open(dual_files['metadata'], 'r', encoding='utf-8') as f:
                cls._model_metadata = json.load(f)
            
            # Extraer configuración importante
            cls._class_mappings = {
                int(k): v for k, v in cls._model_metadata['class_mappings'].items()
            }
            cls._categorical_mappings = cls._model_metadata['categorical_mappings']
            cls._target_columns = cls._model_metadata['target_columns']
            
            logger.info("✅ Metadatos duales cargados")
            
            # Log estadísticas del modelo
            training_results = cls._model_metadata['training_results']
            classifier_f1 = training_results['classifier']['test_f1_score']
            regressor_r2 = training_results['regressor']['test_r2_score']
            training_time = training_results['combined']['training_time_formatted']
            
            logger.info(f"📊 Estadísticas del modelo:")
            logger.info(f"   Classifier F1-Score: {classifier_f1:.4f}")
            logger.info(f"   Regressor R²: {regressor_r2:.4f}")
            logger.info(f"   Tiempo de entrenamiento: {training_time}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelos duales: {e}")
            return False
    
    @classmethod
    async def _load_individual_models(cls, models_path: Path) -> bool:
        """
        Carga modelos individuales como fallback.
        
        Returns:
            bool: True si la carga fue exitosa
        """
        try:
            logger.info("🔄 Cargando modelos individuales...")
            
            # Cargar XGBoost Classifier individual
            classifier_path = models_path / settings.CLASSIFIER_INDIVIDUAL_NAME
            if classifier_path.exists():
                cls._classifier_model = joblib.load(classifier_path)
                logger.info("✅ XGBoost Classifier individual cargado")
            else:
                logger.warning(f"⚠️  Modelo clasificador individual no encontrado: {classifier_path}")
                return False
            
            # Cargar XGBoost Regressor individual
            regressor_path = models_path / settings.REGRESSOR_INDIVIDUAL_NAME
            if regressor_path.exists():
                cls._regressor_model = joblib.load(regressor_path)
                logger.info("✅ XGBoost Regressor individual cargado")
            else:
                logger.warning(f"⚠️  Modelo regresor individual no encontrado: {regressor_path}")
                return False
            
            # Cargar escaladores individuales
            scaler_path = models_path / settings.SCALER_INDIVIDUAL_NAME
            if scaler_path.exists():
                cls._feature_scaler = joblib.load(scaler_path)
                logger.info("✅ Feature Scaler individual cargado")
            
            # Cargar metadata si existe
            try:
                metadata_files = [
                    models_path / "classifier_metadata.json",
                    models_path / "regressor_metadata.json"
                ]
                
                for metadata_file in metadata_files:
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            if cls._model_metadata is None:
                                cls._model_metadata = {"training_results": {}}
                            cls._model_metadata["training_results"].update(metadata)
                        
                logger.info("✅ Metadata de modelos individuales cargada")
                
            except Exception as e:
                logger.warning(f"⚠️  No se pudo cargar metadata individual: {e}")
            
            logger.info("🎯 Modelos individuales cargados exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelos individuales: {e}")
            return False
        regressor_path = models_path / settings.REGRESSOR_MODEL_NAME
        if regressor_path.exists():
            cls._regressor_model = joblib.load(regressor_path)
            logger.info("✅ XGBoost Regressor individual cargado")
        else:
            logger.error(f"❌ Modelo regresor no encontrado: {regressor_path}")
            raise FileNotFoundError(f"Regressor model not found: {regressor_path}")
        
        # Cargar Feature Scaler
        scaler_path = models_path / settings.SCALER_MODEL_NAME
        if scaler_path.exists():
            cls._feature_scaler = joblib.load(scaler_path)
            logger.info("✅ Feature Scaler individual cargado")
        else:
            logger.warning(f"⚠️  Scaler no encontrado: {scaler_path}")
        
        logger.info("✅ Modelos individuales cargados como fallback")
    
    
    @classmethod
    def predict_classes(cls, features: np.ndarray) -> Dict[str, Any]:
        """
        Predicción de clases CSS usando XGBoost Classifier entrenado.
        
        Args:
            features: Features preprocesadas para el modelo
            
        Returns:
            Dict con clases predichas y confianza
        """
        if not cls._is_loaded or cls._classifier_model is None:
            raise RuntimeError("Modelos no cargados. Ejecutar load_models() primero.")
        
        try:
            # Escalar features usando el scaler correcto
            if cls._feature_scaler:
                features_scaled = cls._feature_scaler.transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)
            
            # Predicción
            prediction = cls._classifier_model.predict(features_scaled)[0]
            prediction_proba = cls._classifier_model.predict_proba(features_scaled)[0]
            
            # Mapear predicción a clases CSS usando mapeo real
            css_classes = cls._map_prediction_to_css_classes(prediction)
            confidence = float(np.max(prediction_proba))
            
            return {
                "classes": css_classes,
                "confidence": confidence,
                "raw_prediction": int(prediction),
                "model_type": "dual" if cls._class_mappings else "individual"
            }
            
        except Exception as e:
            logger.error(f"❌ Error en predicción de clases: {e}")
            # Fallback a predicción por defecto
            return cls._get_default_class_prediction()
    
    @classmethod
    def predict_values(cls, features: np.ndarray) -> Dict[str, Any]:
        """
        Predicción de valores CSS usando XGBoost Regressor entrenado.
        
        Args:
            features: Features preprocesadas para el modelo
            
        Returns:
            Dict con variables CSS predichas y confianza
        """
        if not cls._is_loaded or cls._regressor_model is None:
            raise RuntimeError("Modelos no cargados. Ejecutar load_models() primero.")
        
        try:
            # Usar scaler específico del regressor si está disponible
            if cls._regressor_scaler:
                # Para modelos duales, usar el scaler específico del regressor
                features_scaled = cls._regressor_scaler.transform(features.reshape(1, -1))
            elif cls._feature_scaler:
                # Fallback al scaler general
                features_scaled = cls._feature_scaler.transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)
            
            # Predicción
            prediction_scaled = cls._regressor_model.predict(features_scaled)
            
            # Desescalar si tenemos target scaler (modelos duales)
            if cls._target_scaler and hasattr(prediction_scaled, 'shape') and len(prediction_scaled.shape) > 1:
                prediction = cls._target_scaler.inverse_transform(prediction_scaled)[0]
            else:
                prediction = prediction_scaled[0] if hasattr(prediction_scaled, '__len__') else prediction_scaled
            
            # Mapear predicción a variables CSS
            css_variables = cls._map_prediction_to_css_variables(prediction)
            
            # Calcular confianza basada en metadata o usar valor por defecto
            confidence = cls._calculate_regression_confidence(prediction)
            
            return {
                "variables": css_variables,
                "confidence": confidence,
                "raw_prediction": prediction.tolist() if hasattr(prediction, 'tolist') else prediction,
                "model_type": "dual" if cls._target_scaler else "individual"
            }
            
        except Exception as e:
            logger.error(f"❌ Error en predicción de valores: {e}")
            # Fallback a predicción por defecto
            return cls._get_default_value_prediction()
    
    @classmethod
    def predict_dual(cls, user_context, historical_data: List[Dict], social_context: Dict, is_authenticated: bool = False) -> Dict[str, Any]:
        """
        Predicción dual completa usando FeatureProcessor integrado.
        
        Args:
            user_context: Contexto del usuario (UserContext)
            historical_data: Datos históricos de comportamiento
            social_context: Contexto social agregado
            is_authenticated: Si el usuario está autenticado
            
        Returns:
            Dict con predicción dual completa
        """
        if not cls._is_loaded or not cls._feature_processor:
            raise RuntimeError("Sistema de modelos no inicializado")
        
        try:
            # Procesar features usando FeatureProcessor v2 (21 features)
            features = cls._feature_processor.prepare_features_v2(
                user_context, historical_data, social_context, is_authenticated
            )
            
            # Predicción dual
            class_result = cls.predict_classes(features)
            value_result = cls.predict_values(features)
            
            # Combinar resultados
            return {
                "css_classes": class_result["classes"],
                "css_variables": value_result["variables"],
                "confidence": {
                    "classifier": class_result["confidence"],
                    "regressor": value_result["confidence"],
                    "combined": (class_result["confidence"] + value_result["confidence"]) / 2
                },
                "model_info": {
                    "classifier_type": class_result.get("model_type", "unknown"),
                    "regressor_type": value_result.get("model_type", "unknown"),
                    "feature_count": len(features),
                    "prediction_timestamp": cls._get_timestamp()
                },
                "raw_predictions": {
                    "classifier": class_result["raw_prediction"],
                    "regressor": value_result["raw_prediction"]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error en predicción dual: {e}")
            return cls._get_default_dual_prediction()
    
    
    @classmethod
    def _map_prediction_to_css_classes(cls, prediction: Any) -> List[str]:
        """
        Mapea la predicción del clasificador a clases CSS usando mapeo real.
        """
        if cls._class_mappings and prediction in cls._class_mappings:
            return cls._class_mappings[prediction]
        
        # Fallback a mapeo básico si no hay mapeo entrenado
        basic_mapping = {
            0: ["densidad-baja", "fuente-sans", "modo-claro"],
            1: ["densidad-media", "fuente-serif", "modo-claro"],
            2: ["densidad-alta", "fuente-mono", "modo-nocturno"],
        }
        
        return basic_mapping.get(prediction % 3, ["densidad-media", "fuente-sans", "modo-claro"])
    
    @classmethod
    def _map_prediction_to_css_variables(cls, prediction: Any) -> Dict[str, str]:
        """
        Mapea la predicción del regresor a variables CSS usando configuración real.
        """
        if cls._target_columns and hasattr(prediction, '__len__') and len(prediction) >= len(cls._target_columns):
            # Usar mapeo basado en target_columns entrenados
            css_variables = {}
            for i, target_name in enumerate(cls._target_columns):
                value = prediction[i]
                
                # Formatear según el tipo de variable CSS
                if target_name == '--font-size-base':
                    css_variables[target_name] = f"{max(0.8, min(2.0, value)):.3f}rem"
                elif target_name == '--spacing-factor':
                    css_variables[target_name] = f"{max(0.5, min(2.0, value)):.3f}"
                elif target_name == '--color-primary-hue':
                    css_variables[target_name] = f"{max(0, min(360, value)):.0f}"
                elif target_name == '--border-radius':
                    css_variables[target_name] = f"{max(0, min(1.0, value)):.3f}rem"
                elif target_name == '--line-height':
                    css_variables[target_name] = f"{max(1.0, min(2.0, value)):.3f}"
                else:
                    css_variables[target_name] = f"{value:.3f}"
            
            return css_variables
        
        # Fallback a mapeo básico
        if hasattr(prediction, '__len__') and len(prediction) >= 3:
            return {
                "--font-size-base": f"{max(0.8, min(2.0, prediction[0])):.3f}rem",
                "--spacing-factor": f"{max(0.5, min(2.0, prediction[1])):.3f}",
                "--color-primary-hue": f"{max(0, min(360, prediction[2] * 360 if prediction[2] <= 1 else prediction[2])):.0f}",
                "--border-radius": f"{max(0, min(1.0, prediction[3] if len(prediction) > 3 else 0.25)):.3f}rem",
                "--line-height": f"{max(1.0, min(2.0, prediction[4] if len(prediction) > 4 else 1.4)):.3f}"
            }
        else:
            return cls._get_default_css_variables()
    
    @classmethod
    def _calculate_regression_confidence(cls, prediction: Any) -> float:
        """
        Calcula confianza para regresión usando metadata del modelo.
        """
        if cls._model_metadata and 'training_results' in cls._model_metadata:
            # Usar R² del entrenamiento como proxy de confianza
            r2_score = cls._model_metadata['training_results']['regressor']['test_r2_score']
            return max(0.3, min(1.0, r2_score))  # Clamp entre 30% y 100%
        
        # Fallback a confianza base
        return 0.85
    
    @classmethod
    def _get_default_class_prediction(cls) -> Dict[str, Any]:
        """Predicción de clases por defecto en caso de error."""
        return {
            "classes": ["densidad-media", "fuente-sans", "modo-claro"],
            "confidence": 0.5,
            "raw_prediction": 0,
            "model_type": "fallback"
        }
    
    @classmethod
    def _get_default_value_prediction(cls) -> Dict[str, Any]:
        """Predicción de valores por defecto en caso de error."""
        return {
            "variables": cls._get_default_css_variables(),
            "confidence": 0.5,
            "raw_prediction": [1.0, 1.0, 180, 0.25, 1.4],
            "model_type": "fallback"
        }
    
    @classmethod
    def _get_default_css_variables(cls) -> Dict[str, str]:
        """Variables CSS por defecto."""
        return {
            "--font-size-base": "1.000rem",
            "--spacing-factor": "1.000",
            "--color-primary-hue": "180",
            "--border-radius": "0.250rem",
            "--line-height": "1.400"
        }
    
    @classmethod
    def _get_default_dual_prediction(cls) -> Dict[str, Any]:
        """Predicción dual por defecto en caso de error."""
        return {
            "css_classes": ["densidad-media", "fuente-sans", "modo-claro"],
            "css_variables": cls._get_default_css_variables(),
            "confidence": {
                "classifier": 0.5,
                "regressor": 0.5,
                "combined": 0.5
            },
            "model_info": {
                "classifier_type": "fallback",
                "regressor_type": "fallback",
                "feature_count": 0,
                "prediction_timestamp": cls._get_timestamp()
            },
            "raw_predictions": {
                "classifier": 0,
                "regressor": [1.0, 1.0, 180, 0.25, 1.4]
            }
        }
    
    @classmethod
    def _get_timestamp(cls) -> str:
        """Obtiene timestamp actual."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    @classmethod
    def get_model_info(cls) -> Dict[str, Any]:
        """
        Obtiene información detallada de los modelos cargados.
        
        Returns:
            Dict con información de los modelos
        """
        if not cls._is_loaded:
            return {"status": "not_loaded", "models": {}}
        
        info = {
            "status": "loaded",
            "models": {
                "classifier_loaded": cls._classifier_model is not None,
                "regressor_loaded": cls._regressor_model is not None,
                "feature_processor_loaded": cls._feature_processor is not None
            },
            "scalers": {
                "feature_scaler": cls._feature_scaler is not None,
                "regressor_scaler": cls._regressor_scaler is not None,
                "target_scaler": cls._target_scaler is not None,
                "label_encoder": cls._label_encoder is not None
            }
        }
        
        # Agregar metadata si está disponible
        if cls._model_metadata:
            info["training_info"] = {
                "model_version": cls._model_metadata.get("version", "unknown"),
                "training_date": cls._model_metadata.get("training_results", {}).get("combined", {}).get("training_date", "unknown"),
                "classifier_f1": cls._model_metadata.get("training_results", {}).get("classifier", {}).get("test_f1_score", 0),
                "regressor_r2": cls._model_metadata.get("training_results", {}).get("regressor", {}).get("test_r2_score", 0),
                "n_classes": len(cls._class_mappings) if cls._class_mappings else 0,
                "n_targets": len(cls._target_columns) if cls._target_columns else 0
            }
        
        return info
    
    
    @classmethod
    async def _validate_loaded_models(cls) -> None:
        """
        Valida que los modelos cargados estén funcionando correctamente.
        Ejecuta predicciones de prueba para verificar integridad.
        """
        logger.info("🔍 Validando modelos cargados...")
        
        try:
            # Crear features de prueba
            test_features = np.array([0.5] * 21, dtype=np.float32)
            
            # Probar predicción de clasificación
            if cls._classifier_model is not None:
                try:
                    test_prediction = cls._classifier_model.predict_proba([test_features])
                    if test_prediction is None or len(test_prediction) == 0:
                        raise ValueError("Classifier no retorna predicciones válidas")
                    logger.info("✅ Classifier validado exitosamente")
                except Exception as e:
                    logger.error(f"❌ Classifier falló validación: {e}")
                    cls._classifier_model = None
            
            # Probar predicción de regresión
            if cls._regressor_model is not None:
                try:
                    test_prediction = cls._regressor_model.predict([test_features])
                    if test_prediction is None or len(test_prediction) == 0:
                        raise ValueError("Regressor no retorna predicciones válidas")
                    logger.info("✅ Regressor validado exitosamente")
                except Exception as e:
                    logger.error(f"❌ Regressor falló validación: {e}")
                    cls._regressor_model = None
            
            # Validar escaladores
            if cls._feature_scaler is not None:
                try:
                    scaled_features = cls._feature_scaler.transform([test_features])
                    if scaled_features is None:
                        raise ValueError("Feature scaler no funciona correctamente")
                    logger.info("✅ Feature scaler validado")
                except Exception as e:
                    logger.error(f"❌ Feature scaler falló: {e}")
                    cls._feature_scaler = None
            
            logger.info("🎯 Validación de modelos completada")
            
        except Exception as e:
            logger.error(f"❌ Error en validación de modelos: {e}")
            raise
    
    
    @classmethod
    async def _load_default_models(cls) -> None:
        """
        Carga configuración por defecto cuando no hay modelos disponibles.
        Establece mapeos básicos y configuración mínima.
        """
        logger.info("🔄 Cargando configuración por defecto...")
        
        # Mapeos básicos de clases CSS
        cls._class_mappings = {
            0: ["densidad-alta", "fuente-sans", "modo-claro"],
            1: ["densidad-alta", "fuente-sans", "modo-nocturno"],
            2: ["densidad-media", "fuente-sans", "modo-claro"],
            3: ["densidad-media", "fuente-sans", "modo-nocturno"],
            4: ["densidad-baja", "fuente-sans", "modo-claro"],
            5: ["densidad-baja", "fuente-sans", "modo-nocturno"]
        }
        
        # Variables CSS por defecto
        cls._target_columns = [
            "--font-size-base", "--spacing-factor", "--color-primary-hue",
            "--border-radius", "--line-height"
        ]
        
        # Metadata mínima
        cls._model_metadata = {
            "version": "fallback-1.0",
            "model_type": "default",
            "training_results": {
                "classifier": {"test_f1_score": 0.0},
                "regressor": {"test_r2_score": 0.0},
                "combined": {
                    "n_features": 21,
                    "classifier_f1_score": 0.0,
                    "regressor_r2_score": 0.0
                }
            }
        }
        
        logger.info("✅ Configuración por defecto cargada")
    
    
    @classmethod
    async def _initialize_emergency_mode(cls) -> None:
        """
        Inicializa el sistema en modo de emergencia.
        Solo Feature Processor básico y valores hardcodeados.
        """
        logger.warning("🚨 Iniciando modo de emergencia...")
        
        try:
            # Inicializar Feature Processor básico
            cls._feature_processor = FeatureProcessor()
            
            # Cargar configuración mínima
            await cls._load_default_models()
            
            # Limpiar referencias a modelos ML
            cls._classifier_model = None
            cls._regressor_model = None
            cls._feature_scaler = None
            cls._regressor_scaler = None
            cls._target_scaler = None
            cls._label_encoder = None
            
            logger.warning("⚠️  Modo de emergencia activo - solo fallbacks disponibles")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando modo de emergencia: {e}")
            raise
    
    
    @classmethod
    def is_in_emergency_mode(cls) -> bool:
        """
        Verifica si el sistema está operando en modo de emergencia.
        
        Returns:
            bool: True si está en modo emergencia
        """
        return (cls._is_loaded and 
                cls._classifier_model is None and 
                cls._regressor_model is None and
                cls._feature_processor is not None)
    
    
    @classmethod
    async def attempt_model_recovery(cls) -> Dict[str, Any]:
        """
        Intenta recuperar modelos después de un fallo.
        Útil para recuperación automática.
        
        Returns:
            Dict con resultados detallados de la recuperación
        """
        logger.info("🔄 Intentando recuperación de modelos...")
        
        recovery_result = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "message": "",
            "loaded_components": [],
            "errors": [],
            "previous_state": cls.get_system_health()
        }
        
        try:
            # Limpiar estado actual
            cls.cleanup()
            
            # Intentar recargar
            await cls.load_models(max_retries=2, retry_delay=0.5)
            
            # Verificar qué componentes se cargaron
            if cls._classifier_model:
                recovery_result["loaded_components"].append("classifier")
            if cls._regressor_model:
                recovery_result["loaded_components"].append("regressor")
            if cls._feature_processor:
                recovery_result["loaded_components"].append("feature_processor")
            if cls._feature_scaler:
                recovery_result["loaded_components"].append("feature_scaler")
            
            if cls._is_loaded and not cls.is_in_emergency_mode():
                recovery_result["success"] = True
                recovery_result["message"] = "Recuperación completa exitosa"
                logger.info("✅ Recuperación de modelos exitosa")
            elif cls._is_loaded:
                recovery_result["success"] = True
                recovery_result["message"] = "Recuperación parcial - sistema en modo degradado"
                logger.warning("⚠️  Recuperación parcial - sistema en modo degradado")
            else:
                recovery_result["success"] = False
                recovery_result["message"] = "Recuperación fallida - sistema offline"
                recovery_result["errors"].append("No se pudieron cargar componentes críticos")
                
        except Exception as e:
            recovery_result["success"] = False
            recovery_result["message"] = f"Fallo en recuperación: {str(e)}"
            recovery_result["errors"].append(str(e))
            logger.error(f"❌ Fallo en recuperación de modelos: {e}")
        
        recovery_result["final_state"] = cls.get_system_health()
        return recovery_result
    
    
    @classmethod
    def get_system_health(cls) -> Dict[str, Any]:
        """
        Obtiene un reporte detallado de salud del sistema ML.
        
        Returns:
            Dict con métricas de salud
        """
        health = {
            "overall_status": "unknown",
            "is_loaded": cls._is_loaded,
            "emergency_mode": cls.is_in_emergency_mode(),
            "components": {
                "classifier": "offline",
                "regressor": "offline", 
                "feature_processor": "offline",
                "scalers": "offline"
            },
            "performance": {
                "can_predict": False,
                "fallback_only": True
            },
            "validation": {
                "last_check": None,
                "model_integrity": "unknown",
                "prediction_quality": "unknown",
                "errors": []
            }
        }
        
        if cls._is_loaded:
            # Estado de componentes
            health["components"]["classifier"] = "online" if cls._classifier_model else "offline"
            health["components"]["regressor"] = "online" if cls._regressor_model else "offline"
            health["components"]["feature_processor"] = "online" if cls._feature_processor else "offline"
            health["components"]["scalers"] = "online" if cls._feature_scaler else "offline"
            
            # Estado general
            if cls.is_in_emergency_mode():
                health["overall_status"] = "degraded"
                health["performance"]["can_predict"] = True
                health["performance"]["fallback_only"] = True
            elif cls._classifier_model and cls._regressor_model:
                health["overall_status"] = "healthy"
                health["performance"]["can_predict"] = True
                health["performance"]["fallback_only"] = False
            else:
                health["overall_status"] = "partial"
                health["performance"]["can_predict"] = True
                health["performance"]["fallback_only"] = True
        else:
            health["overall_status"] = "offline"
            
        return health
    
    @classmethod
    async def validate_model_integrity(cls) -> Dict[str, Any]:
        """
        Valida la integridad de los modelos ML realizando predicciones de prueba.
        
        Returns:
            Dict con resultados de validación
        """
        validation_result = {
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "components": {
                "classifier": {"status": "unknown", "error": None},
                "regressor": {"status": "unknown", "error": None},
                "feature_processor": {"status": "unknown", "error": None},
                "scalers": {"status": "unknown", "error": None}
            },
            "predictions": {
                "classifier_test": None,
                "regressor_test": None,
                "prediction_ranges": {"classifier": None, "regressor": None}
            },
            "performance_metrics": {
                "inference_time_ms": None,
                "memory_usage_mb": None
            }
        }
        
        try:
            if not cls._is_loaded:
                raise RuntimeError("Sistema ML no está cargado")
            
            # Crear datos de prueba realistas usando UserContext
            from app.models.adaptive_ui import UserContext
            test_context = UserContext(
                # Campos requeridos por UserContext
                hora_local=datetime.now(),
                prefers_color_scheme="light",
                viewport_width=1920,
                viewport_height=1080,
                touch_enabled=False,
                device_pixel_ratio=1.0,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                session_id="test_session_123",
                page_path="/test",
                referer=None
            )
            
            start_time = time.time()
            
            # Validar Feature Processor
            try:
                if cls._feature_processor:
                    features = cls._feature_processor.prepare_features_v2(test_context)
                    if len(features) != 21:
                        raise ValueError(f"Feature processor devolvió {len(features)} features, esperadas 21")
                    validation_result["components"]["feature_processor"]["status"] = "healthy"
                else:
                    raise RuntimeError("Feature processor no disponible")
            except Exception as e:
                validation_result["components"]["feature_processor"]["status"] = "error"
                validation_result["components"]["feature_processor"]["error"] = str(e)
            
            # Validar Scalers
            try:
                if cls._feature_scaler:
                    features_array = np.array(features).reshape(1, -1)
                    scaled_features = cls._feature_scaler.transform(features_array)
                    # Para modelos individuales, usamos el mismo scaler para ambos modelos
                    regressor_scaled = scaled_features
                    validation_result["components"]["scalers"]["status"] = "healthy"
                else:
                    raise RuntimeError("Feature scaler no disponible")
            except Exception as e:
                validation_result["components"]["scalers"]["status"] = "error"
                validation_result["components"]["scalers"]["error"] = str(e)
                # Asegurar que las variables existan para evitar errores downstream
                features_array = np.array(features).reshape(1, -1)
                scaled_features = features_array  # Fallback sin escalado
                regressor_scaled = features_array
            
            # Validar Classifier
            try:
                if cls._classifier_model:
                    # Hacer predicción
                    class_probs = cls._classifier_model.predict_proba(scaled_features)[0]
                    class_prediction = cls._classifier_model.predict(scaled_features)[0]
                    
                    # Validar rangos esperados
                    if not (0 <= max(class_probs) <= 1):
                        raise ValueError(f"Probabilidades fuera de rango: {class_probs}")
                    
                    # Decodificar clase
                    if cls._label_encoder:
                        decoded_class = cls._label_encoder.inverse_transform([class_prediction])[0]
                        validation_result["predictions"]["classifier_test"] = {
                            "class": decoded_class,
                            "confidence": float(max(class_probs))
                        }
                    
                    validation_result["components"]["classifier"]["status"] = "healthy"
                    validation_result["predictions"]["prediction_ranges"]["classifier"] = {
                        "min_confidence": float(min(class_probs)),
                        "max_confidence": float(max(class_probs))
                    }
                else:
                    raise RuntimeError("Classifier no disponible")
            except Exception as e:
                validation_result["components"]["classifier"]["status"] = "error"
                validation_result["components"]["classifier"]["error"] = str(e)
            
            # Validar Regressor
            try:
                if cls._regressor_model:
                    # Hacer predicción
                    scaled_prediction = cls._regressor_model.predict(regressor_scaled)[0]
                    
                    # Desnormalizar si hay target scaler
                    if cls._target_scaler:
                        final_prediction = cls._target_scaler.inverse_transform([[scaled_prediction]])[0][0]
                    else:
                        final_prediction = scaled_prediction
                    
                    # Validar rangos razonables para variables CSS (0-100 o similar)
                    if not (-100 <= final_prediction <= 200):  # Rango amplio pero razonable
                        logger.warning(f"Predicción regressor fuera de rango esperado: {final_prediction}")
                    
                    validation_result["predictions"]["regressor_test"] = float(final_prediction)
                    validation_result["components"]["regressor"]["status"] = "healthy"
                    validation_result["predictions"]["prediction_ranges"]["regressor"] = {
                        "value": float(final_prediction),
                        "scaled_value": float(scaled_prediction)
                    }
                else:
                    raise RuntimeError("Regressor no disponible")
            except Exception as e:
                validation_result["components"]["regressor"]["status"] = "error"
                validation_result["components"]["regressor"]["error"] = str(e)
            
            # Calcular métricas de performance
            end_time = time.time()
            validation_result["performance_metrics"]["inference_time_ms"] = round((end_time - start_time) * 1000, 2)
            
            # Verificar memoria (simplificado)
            try:
                import psutil
                process = psutil.Process()
                validation_result["performance_metrics"]["memory_usage_mb"] = round(process.memory_info().rss / 1024 / 1024, 2)
            except ImportError:
                validation_result["performance_metrics"]["memory_usage_mb"] = "psutil_not_available"
            
            # Determinar éxito general
            all_healthy = all(
                comp["status"] == "healthy" 
                for comp in validation_result["components"].values()
            )
            validation_result["success"] = all_healthy
            
            if all_healthy:
                logger.info("✅ Validación de modelos ML completada exitosamente")
            else:
                failed_components = [
                    name for name, comp in validation_result["components"].items() 
                    if comp["status"] != "healthy"
                ]
                logger.warning(f"⚠️  Validación parcial - componentes con problemas: {failed_components}")
                
        except Exception as e:
            logger.error(f"❌ Error durante validación de integridad: {e}")
            validation_result["components"]["general"] = {"status": "error", "error": str(e)}
        
        return validation_result
    
    @classmethod
    async def get_detailed_health_report(cls) -> Dict[str, Any]:
        """
        Genera un reporte de salud detallado combinando estado actual y validación.
        
        Returns:
            Dict con reporte completo de salud
        """
        # Obtener estado básico
        basic_health = cls.get_system_health()
        
        # Ejecutar validación de integridad
        integrity_check = await cls.validate_model_integrity()
        
        # Combinar resultados
        detailed_report = {
            **basic_health,
            "detailed_validation": integrity_check,
            "recommendations": [],
            "alerts": []
        }
        
        # Generar recomendaciones basadas en los resultados
        if not integrity_check["success"]:
            detailed_report["recommendations"].append(
                "Ejecutar attempt_model_recovery() para intentar recuperar modelos"
            )
            
        failed_components = [
            name for name, comp in integrity_check["components"].items()
            if comp["status"] == "error"
        ]
        
        if failed_components:
            detailed_report["alerts"].append({
                "level": "warning",
                "message": f"Componentes con errores: {', '.join(failed_components)}"
            })
        
        # Alertas de performance
        if integrity_check["performance_metrics"]["inference_time_ms"]:
            inference_time = integrity_check["performance_metrics"]["inference_time_ms"]
            if inference_time > 100:  # Requirement: <100ms
                detailed_report["alerts"].append({
                    "level": "performance",
                    "message": f"Tiempo de inferencia ({inference_time}ms) excede el límite de 100ms"
                })
        
        return detailed_report


    @classmethod
    def cleanup(cls) -> None:
        """Limpia recursos de modelos."""
        cls._classifier_model = None
        cls._regressor_model = None
        cls._feature_scaler = None
        cls._regressor_scaler = None
        cls._target_scaler = None
        cls._label_encoder = None
        cls._class_mappings = None
        cls._categorical_mappings = None
        cls._target_columns = None
        cls._model_metadata = None
        cls._feature_processor = None
        cls._is_loaded = False
        logger.info("🧹 Sistema de modelos ML limpiado de memoria")
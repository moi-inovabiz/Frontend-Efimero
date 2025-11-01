"""
Model Manager para XGBoost
Maneja la carga y predicción de los modelos duales obligatorios
"""

import joblib
import numpy as np
import json
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
    async def load_models(cls) -> None:
        """
        Carga los modelos XGBoost duales en memoria RAM.
        Ejecutado en el startup hook de FastAPI.
        
        Prioriza modelos duales entrenados, con fallback a modelos individuales.
        """
        try:
            models_path = Path(settings.MODELS_PATH)
            logger.info(f"🔄 Cargando modelos desde: {models_path}")
            
            # Intentar cargar modelos duales primero (preferido)
            dual_success = await cls._load_dual_models(models_path)
            
            if not dual_success:
                # Fallback a modelos individuales
                logger.info("⚠️  Modelos duales no encontrados, intentando modelos individuales")
                await cls._load_individual_models(models_path)
            
            # Cargar Feature Processor
            cls._feature_processor = FeatureProcessor()
            
            cls._is_loaded = True
            logger.info("🎯 Sistema de modelos ML inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error crítico cargando modelos: {e}")
            # En producción, podríamos usar modelos por defecto aquí
            raise
    
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
    async def _load_individual_models(cls, models_path: Path) -> None:
        """
        Carga modelos individuales como fallback.
        """
        # Cargar XGBoost Classifier individual
        classifier_path = models_path / settings.CLASSIFIER_MODEL_NAME
        if classifier_path.exists():
            cls._classifier_model = joblib.load(classifier_path)
            logger.info("✅ XGBoost Classifier individual cargado")
        else:
            logger.error(f"❌ Modelo clasificador no encontrado: {classifier_path}")
            raise FileNotFoundError(f"Classifier model not found: {classifier_path}")
        
        # Cargar XGBoost Regressor individual
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
            # Procesar features usando FeatureProcessor
            features = cls._feature_processor.prepare_features(
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
"""
Model Manager para XGBoost
Maneja la carga y predicción de los modelos duales obligatorios
"""

import joblib
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Gestor de modelos XGBoost para Frontend Efímero.
    
    Implementa el requisito de DOBLE PREDICCIÓN OBLIGATORIA:
    - XGBoost Classifier para clases CSS (macro-estilo)
    - XGBoost Regressor para variables CSS (ajuste fino)
    """
    
    _classifier_model: Optional[Any] = None
    _regressor_model: Optional[Any] = None
    _feature_scaler: Optional[Any] = None
    _is_loaded: bool = False
    
    
    @classmethod
    async def load_models(cls) -> None:
        """
        Carga los modelos XGBoost en memoria RAM.
        Ejecutado en el startup hook de FastAPI.
        """
        try:
            models_path = Path(settings.MODELS_PATH)
            
            # Cargar XGBoost Classifier
            classifier_path = models_path / settings.CLASSIFIER_MODEL_NAME
            if classifier_path.exists():
                cls._classifier_model = joblib.load(classifier_path)
                logger.info("✅ XGBoost Classifier cargado")
            else:
                logger.warning(f"⚠️  Modelo clasificador no encontrado: {classifier_path}")
            
            # Cargar XGBoost Regressor
            regressor_path = models_path / settings.REGRESSOR_MODEL_NAME
            if regressor_path.exists():
                cls._regressor_model = joblib.load(regressor_path)
                logger.info("✅ XGBoost Regressor cargado")
            else:
                logger.warning(f"⚠️  Modelo regresor no encontrado: {regressor_path}")
            
            # Cargar Feature Scaler
            scaler_path = models_path / settings.SCALER_MODEL_NAME
            if scaler_path.exists():
                cls._feature_scaler = joblib.load(scaler_path)
                logger.info("✅ Feature Scaler cargado")
            else:
                logger.warning(f"⚠️  Scaler no encontrado: {scaler_path}")
            
            cls._is_loaded = True
            logger.info("🎯 Todos los modelos ML cargados en memoria")
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelos: {e}")
            raise
    
    
    @classmethod
    def predict_classes(cls, features: np.ndarray) -> Dict[str, Any]:
        """
        Predicción de clases CSS usando XGBoost Classifier.
        
        Args:
            features: Features preprocesadas para el modelo
            
        Returns:
            Dict con clases predichas y confianza
        """
        if not cls._is_loaded or cls._classifier_model is None:
            raise RuntimeError("Modelos no cargados. Ejecutar load_models() primero.")
        
        try:
            # Escalar features
            if cls._feature_scaler:
                features_scaled = cls._feature_scaler.transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)
            
            # Predicción
            prediction = cls._classifier_model.predict(features_scaled)[0]
            prediction_proba = cls._classifier_model.predict_proba(features_scaled)[0]
            
            # Mapear predicción a clases CSS
            css_classes = cls._map_prediction_to_css_classes(prediction)
            confidence = float(np.max(prediction_proba))
            
            return {
                "classes": css_classes,
                "confidence": confidence,
                "raw_prediction": prediction
            }
            
        except Exception as e:
            logger.error(f"❌ Error en predicción de clases: {e}")
            raise
    
    
    @classmethod
    def predict_values(cls, features: np.ndarray) -> Dict[str, Any]:
        """
        Predicción de valores CSS usando XGBoost Regressor.
        
        Args:
            features: Features preprocesadas para el modelo
            
        Returns:
            Dict con variables CSS predichas y confianza
        """
        if not cls._is_loaded or cls._regressor_model is None:
            raise RuntimeError("Modelos no cargados. Ejecutar load_models() primero.")
        
        try:
            # Escalar features
            if cls._feature_scaler:
                features_scaled = cls._feature_scaler.transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)
            
            # Predicción
            prediction = cls._regressor_model.predict(features_scaled)[0]
            
            # Mapear predicción a variables CSS
            css_variables = cls._map_prediction_to_css_variables(prediction)
            
            # Para regresión, usar desviación estándar como proxy de confianza
            confidence = cls._calculate_regression_confidence(prediction)
            
            return {
                "variables": css_variables,
                "confidence": confidence,
                "raw_prediction": prediction.tolist() if hasattr(prediction, 'tolist') else prediction
            }
            
        except Exception as e:
            logger.error(f"❌ Error en predicción de valores: {e}")
            raise
    
    
    @classmethod
    def _map_prediction_to_css_classes(cls, prediction: Any) -> List[str]:
        """
        Mapea la predicción del clasificador a clases CSS.
        TODO: Implementar mapeo real basado en el entrenamiento.
        """
        # Placeholder - implementar mapeo real
        class_mapping = {
            0: ["densidad-baja", "fuente-sans"],
            1: ["densidad-media", "fuente-serif"],
            2: ["densidad-alta", "fuente-mono"],
            # Agregar más mapeos según el entrenamiento
        }
        
        return class_mapping.get(prediction, ["densidad-media", "fuente-sans"])
    
    
    @classmethod
    def _map_prediction_to_css_variables(cls, prediction: Any) -> Dict[str, str]:
        """
        Mapea la predicción del regresor a variables CSS.
        TODO: Implementar mapeo real basado en el entrenamiento.
        """
        # Placeholder - implementar mapeo real
        if hasattr(prediction, '__len__') and len(prediction) >= 3:
            return {
                "--font-size-base": f"{max(0.8, min(2.0, prediction[0])):.2f}rem",
                "--spacing-unit": f"{max(0.25, min(2.0, prediction[1])):.2f}rem", 
                "--border-radius": f"{max(0, min(1.0, prediction[2])):.2f}rem"
            }
        else:
            return {
                "--font-size-base": "1.0rem",
                "--spacing-unit": "1.0rem",
                "--border-radius": "0.25rem"
            }
    
    
    @classmethod
    def _calculate_regression_confidence(cls, prediction: Any) -> float:
        """
        Calcula confianza para regresión.
        TODO: Implementar método más sofisticado.
        """
        # Placeholder - usar una confianza base
        return 0.85
    
    
    @classmethod
    def cleanup(cls) -> None:
        """Limpia recursos de modelos."""
        cls._classifier_model = None
        cls._regressor_model = None
        cls._feature_scaler = None
        cls._is_loaded = False
        logger.info("🧹 Modelos ML limpiados de memoria")
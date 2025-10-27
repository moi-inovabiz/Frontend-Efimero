"""
Feature Scaler para el Frontend Efímero
Pipeline de preprocesamiento que normaliza features para modelos XGBoost.
Implementa diferentes estrategias de escalado por grupo de features.
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from app.models.adaptive_ui import UserContext


# Configurar logging
logger = logging.getLogger(__name__)


class FeatureScalerError(Exception):
    """Excepción personalizada para errores del feature scaler."""
    pass


class FeatureScaler:
    """
    Pipeline de preprocesamiento que escala features para modelos XGBoost.
    
    Implementa diferentes estrategias de normalización por grupo de features:
    - Temporal: StandardScaler (distribución gaussiana)
    - Device: MinMaxScaler (rangos conocidos)
    - Historical: RobustScaler (resistente a outliers)
    - Social: MinMaxScaler (porcentajes 0-1)
    - Composite: RobustScaler (ratios con outliers)
    """
    
    # Definición de grupos de features
    FEATURE_GROUPS = {
        'temporal': {
            'indices': [0, 1, 2, 3],  # hour_sin, hour_cos, day_sin, day_cos
            'scaler_type': 'standard',
            'description': 'Features temporales con codificación seno/coseno'
        },
        'device': {
            'indices': [4, 5, 6, 7, 8],  # touch, pixel_ratio, aspect, area, color_scheme
            'scaler_type': 'minmax',
            'description': 'Features de dispositivo con rangos conocidos'
        },
        'historical': {
            'indices': [9, 10, 11, 12, 13],  # session_count, duration, interactions, diversity, recent
            'scaler_type': 'robust',
            'description': 'Features históricas con posibles outliers'
        },
        'social': {
            'indices': [14, 15, 16],  # dark_mode, density, serif preferences
            'scaler_type': 'minmax',
            'description': 'Features sociales (porcentajes 0-1)'
        },
        'composite': {
            'indices': [17, 18, 19],  # touch_vs_mouse, auth_multiplier, mobile_correlation
            'scaler_type': 'robust',
            'description': 'Features compuestas con ratios variables'
        }
    }
    
    def __init__(self):
        """Inicializa el FeatureScaler."""
        self.pipeline: Optional[ColumnTransformer] = None
        self.is_fitted: bool = False
        self.feature_names: List[str] = []
        self._create_feature_names()
        
    def _create_feature_names(self) -> None:
        """Crea nombres descriptivos para las 20 features."""
        self.feature_names = [
            # Temporal (4)
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
            # Device (5)
            'touch_enabled', 'device_pixel_ratio', 'viewport_aspect_ratio', 
            'viewport_area_normalized', 'color_scheme_preference',
            # Historical (5)
            'session_count_normalized', 'avg_session_duration', 'interaction_rate',
            'page_diversity', 'recent_activity',
            # Social (3)
            'global_dark_mode_pref', 'global_density_pref', 'global_serif_pref',
            # Composite (3)
            'touch_vs_mouse_error_ratio', 'auth_behavior_multiplier', 'mobile_time_correlation'
        ]
    
    def _create_pipeline(self) -> ColumnTransformer:
        """
        Crea el pipeline de transformación con diferentes scalers por grupo.
        
        Returns:
            ColumnTransformer: Pipeline configurado para cada grupo de features
        """
        transformers = []
        
        for group_name, group_config in self.FEATURE_GROUPS.items():
            indices = group_config['indices']
            scaler_type = group_config['scaler_type']
            
            # Crear scaler según tipo
            if scaler_type == 'standard':
                scaler = StandardScaler()
            elif scaler_type == 'minmax':
                scaler = MinMaxScaler()
            elif scaler_type == 'robust':
                scaler = RobustScaler()
            else:
                raise FeatureScalerError(f"Unknown scaler type: {scaler_type}")
            
            # Agregar transformador para este grupo
            transformers.append((
                f'{group_name}_scaler',
                scaler,
                indices
            ))
            
            logger.info(f"Created {scaler_type} scaler for {group_name} features: {indices}")
        
        # Crear ColumnTransformer que mantiene el orden original
        pipeline = ColumnTransformer(
            transformers=transformers,
            remainder='passthrough',  # Por si hay features adicionales
            sparse_threshold=0  # Mantener como array denso
        )
        
        return pipeline
    
    def fit(self, features: np.ndarray) -> 'FeatureScaler':
        """
        Entrena los scalers con datos de entrenamiento.
        
        Args:
            features: Array de features (n_samples, 20)
            
        Returns:
            self: Para method chaining
            
        Raises:
            FeatureScalerError: Si hay problemas con las dimensiones o datos
        """
        try:
            # Validar entrada
            features = self._validate_features(features, allow_single_sample=False)
            
            logger.info(f"Fitting scalers with {features.shape[0]} samples, {features.shape[1]} features")
            
            # Crear pipeline si no existe
            if self.pipeline is None:
                self.pipeline = self._create_pipeline()
            
            # Entrenar pipeline
            self.pipeline.fit(features)
            self.is_fitted = True
            
            # Log estadísticas por grupo
            self._log_scaling_stats(features)
            
            logger.info("FeatureScaler fitted successfully")
            return self
            
        except Exception as e:
            logger.error(f"Error fitting FeatureScaler: {e}")
            raise FeatureScalerError(f"Failed to fit scaler: {e}")
    
    def transform(self, features: np.ndarray) -> np.ndarray:
        """
        Transforma features usando scalers entrenados.
        
        Args:
            features: Array de features (n_samples, 20) o (20,)
            
        Returns:
            np.ndarray: Features transformadas con misma forma
            
        Raises:
            FeatureScalerError: Si el scaler no está entrenado
        """
        try:
            if not self.is_fitted:
                raise FeatureScalerError("Scaler must be fitted before transform")
            
            # Validar entrada
            original_shape = features.shape
            features = self._validate_features(features, allow_single_sample=True)
            
            # Transformar
            transformed = self.pipeline.transform(features)
            
            # Restaurar forma original si era muestra única
            if len(original_shape) == 1:
                transformed = transformed.reshape(-1)
            
            return transformed.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Error transforming features: {e}")
            raise FeatureScalerError(f"Failed to transform features: {e}")
    
    def fit_transform(self, features: np.ndarray) -> np.ndarray:
        """
        Entrena y transforma en un solo paso.
        
        Args:
            features: Array de features de entrenamiento
            
        Returns:
            np.ndarray: Features transformadas
        """
        return self.fit(features).transform(features)
    
    def inverse_transform(self, scaled_features: np.ndarray) -> np.ndarray:
        """
        Revierte la transformación (útil para debugging).
        Nota: Implementación manual ya que ColumnTransformer no siempre soporta inverse_transform.
        
        Args:
            scaled_features: Features transformadas
            
        Returns:
            np.ndarray: Features originales aproximadas
        """
        try:
            if not self.is_fitted:
                raise FeatureScalerError("Scaler must be fitted before inverse_transform")
            
            original_shape = scaled_features.shape
            scaled_features = self._validate_features(scaled_features, allow_single_sample=True)
            
            # Reconstruir features originales grupo por grupo
            original_features = np.zeros_like(scaled_features)
            
            for transformer_info in self.pipeline.transformers_:
                _, scaler, indices = transformer_info
                
                # Extraer features escaladas para este grupo
                group_scaled = scaled_features[:, indices]
                
                # Aplicar inverse_transform del scaler específico
                if hasattr(scaler, 'inverse_transform'):
                    group_original = scaler.inverse_transform(group_scaled)
                    original_features[:, indices] = group_original
                else:
                    # Fallback: copiar valores escalados
                    original_features[:, indices] = group_scaled
            
            # Restaurar forma original
            if len(original_shape) == 1:
                original_features = original_features.reshape(-1)
            
            return original_features.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Error in inverse transform: {e}")
            raise FeatureScalerError(f"Failed to inverse transform: {e}")
    
    def save(self, filepath: Union[str, Path]) -> None:
        """
        Guarda el scaler entrenado a disco.
        
        Args:
            filepath: Ruta donde guardar el scaler
        """
        try:
            if not self.is_fitted:
                raise FeatureScalerError("Cannot save unfitted scaler")
            
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar scaler y metadatos
            scaler_data = {
                'pipeline': self.pipeline,
                'feature_names': self.feature_names,
                'feature_groups': self.FEATURE_GROUPS,
                'is_fitted': self.is_fitted
            }
            
            joblib.dump(scaler_data, filepath)
            logger.info(f"FeatureScaler saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving scaler: {e}")
            raise FeatureScalerError(f"Failed to save scaler: {e}")
    
    @classmethod
    def load(cls, filepath: Union[str, Path]) -> 'FeatureScaler':
        """
        Carga un scaler desde disco.
        
        Args:
            filepath: Ruta del scaler guardado
            
        Returns:
            FeatureScaler: Instancia cargada y lista para usar
        """
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                raise FeatureScalerError(f"Scaler file not found: {filepath}")
            
            # Cargar datos
            scaler_data = joblib.load(filepath)
            
            # Crear instancia
            instance = cls()
            instance.pipeline = scaler_data['pipeline']
            instance.feature_names = scaler_data['feature_names']
            instance.is_fitted = scaler_data['is_fitted']
            
            logger.info(f"FeatureScaler loaded from {filepath}")
            return instance
            
        except Exception as e:
            logger.error(f"Error loading scaler: {e}")
            raise FeatureScalerError(f"Failed to load scaler: {e}")
    
    def get_feature_info(self) -> Dict[str, Any]:
        """
        Retorna información sobre las features y escalado.
        
        Returns:
            Dict con información de features, grupos y scalers
        """
        info = {
            'total_features': len(self.feature_names),
            'feature_names': self.feature_names,
            'feature_groups': self.FEATURE_GROUPS,
            'is_fitted': self.is_fitted
        }
        
        if self.is_fitted:
            # Agregar información de scalers entrenados
            info['scalers'] = {}
            for transformer in self.pipeline.transformers_:
                name, scaler, _ = transformer
                if hasattr(scaler, 'mean_'):
                    # StandardScaler
                    info['scalers'][name] = {
                        'type': 'StandardScaler',
                        'mean': scaler.mean_.tolist(),
                        'scale': scaler.scale_.tolist()
                    }
                elif hasattr(scaler, 'data_min_'):
                    # MinMaxScaler
                    info['scalers'][name] = {
                        'type': 'MinMaxScaler',
                        'data_min': scaler.data_min_.tolist(),
                        'data_max': scaler.data_max_.tolist()
                    }
                elif hasattr(scaler, 'center_'):
                    # RobustScaler
                    info['scalers'][name] = {
                        'type': 'RobustScaler',
                        'center': scaler.center_.tolist(),
                        'scale': scaler.scale_.tolist()
                    }
        
        return info
    
    def _validate_features(self, features: np.ndarray, allow_single_sample: bool = False) -> np.ndarray:
        """
        Valida que las features tengan la forma correcta.
        
        Args:
            features: Array de features a validar
            allow_single_sample: Si permitir muestras únicas (20,)
            
        Returns:
            np.ndarray: Features validadas (posiblemente reshaped)
        """
        if not isinstance(features, np.ndarray):
            features = np.array(features)
        
        # Manejar muestra única
        if features.ndim == 1:
            if not allow_single_sample:
                raise FeatureScalerError("Single sample not allowed for fitting")
            if len(features) != 20:
                raise FeatureScalerError(f"Expected 20 features, got {len(features)}")
            features = features.reshape(1, -1)
        
        # Validar forma 2D
        if features.ndim != 2:
            raise FeatureScalerError(f"Features must be 2D array, got {features.ndim}D")
        
        if features.shape[1] != 20:
            raise FeatureScalerError(f"Expected 20 features, got {features.shape[1]}")
        
        return features
    
    def _log_scaling_stats(self, features: np.ndarray) -> None:
        """Log estadísticas de escalado por grupo."""
        for group_name, group_config in self.FEATURE_GROUPS.items():
            indices = group_config['indices']
            group_features = features[:, indices]
            
            logger.info(f"{group_name} features stats:")
            logger.info(f"  Shape: {group_features.shape}")
            logger.info(f"  Mean: {np.mean(group_features, axis=0)}")
            logger.info(f"  Std: {np.std(group_features, axis=0)}")
            logger.info(f"  Range: [{np.min(group_features):.3f}, {np.max(group_features):.3f}]")
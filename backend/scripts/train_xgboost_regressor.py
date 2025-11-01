"""
Script de entrenamiento para XGBoost Regressor
Entrena modelo para predicción de variables CSS continuas del Frontend Efímero
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.multioutput import MultiOutputRegressor
import joblib
import json
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XGBoostRegressorTrainer:
    """
    Entrenador del XGBoost Regressor para predicción de variables CSS continuas.
    
    Implementa el requisito de "XGBoost Regressor for CSS variable prediction"
    con variables como '--font-size-base', '--spacing-factor', etc.
    """
    
    def __init__(self, data_path: str, models_dir: str = "models"):
        """
        Inicializa el entrenador.
        
        Args:
            data_path: Ruta al archivo CSV de datos sintéticos
            models_dir: Directorio donde guardar los modelos entrenados
        """
        self.data_path = Path(data_path)
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Componentes del modelo
        self.regressor = None
        self.scaler = StandardScaler()
        self.target_scaler = StandardScaler()
        
        # Métricas y resultados
        self.training_results = {}
        
        # Features que usaremos (las mismas del FeatureProcessor)
        self.feature_columns = [
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
            'viewport_width', 'viewport_height', 'viewport_aspect_ratio', 'viewport_area_normalized',
            'touch_enabled', 'device_pixel_ratio', 'prefers_dark_mode',
            'avg_session_duration', 'total_clicks_last_week', 'scroll_depth_avg', 'error_rate_last_week',
            'preferred_text_size', 'interaction_speed', 'user_group_density',
            'locale_preference', 'accessibility_needs', 'network_speed'
        ]
        
        # Variables CSS objetivo (targets para regresión)
        self.target_columns = [
            '--font-size-base',
            '--spacing-factor',
            '--color-primary-hue',
            '--border-radius',
            '--line-height'
        ]
    
    def load_and_prepare_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Carga y prepara los datos sintéticos para entrenamiento de regresión.
        
        Returns:
            Tuple[X, y]: Features y targets preparadas
        """
        logger.info(f"Cargando datos desde: {self.data_path}")
        
        # Cargar datos
        df = pd.read_csv(self.data_path)
        logger.info(f"Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
        
        # Preparar features (X)
        X = self._prepare_features(df)
        
        # Preparar targets (y) - variables CSS continuas
        y = self._prepare_targets(df)
        
        logger.info(f"Features preparadas: {X.shape}")
        logger.info(f"Targets preparados: {y.shape}")
        
        return X, y
    
    def _prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepara las features para el entrenamiento (mismo método que classifier).
        
        Args:
            df: DataFrame con los datos sintéticos
            
        Returns:
            np.ndarray: Features numéricas escaladas
        """
        # Seleccionar columnas de features
        available_features = [col for col in self.feature_columns if col in df.columns]
        missing_features = [col for col in self.feature_columns if col not in df.columns]
        
        if missing_features:
            logger.warning(f"Features faltantes en datos: {missing_features}")
        
        logger.info(f"Usando {len(available_features)} features: {available_features}")
        
        # Preparar features numéricas
        X_numeric = df[available_features].copy()
        
        # Codificar variables categóricas
        categorical_mappings = {}
        
        # touch_enabled: boolean -> float
        if 'touch_enabled' in X_numeric.columns:
            X_numeric['touch_enabled'] = X_numeric['touch_enabled'].astype(float)
        
        # prefers_dark_mode: boolean -> float
        if 'prefers_dark_mode' in X_numeric.columns:
            X_numeric['prefers_dark_mode'] = X_numeric['prefers_dark_mode'].astype(float)
        
        # user_group_density: categorical -> numeric
        if 'user_group_density' in X_numeric.columns:
            density_mapping = {'low': 0, 'medium': 1, 'high': 2}
            X_numeric['user_group_density'] = X_numeric['user_group_density'].map(density_mapping)
            categorical_mappings['user_group_density'] = density_mapping
        
        # locale_preference: categorical -> numeric
        if 'locale_preference' in X_numeric.columns:
            locale_mapping = {'en': 0, 'es': 1, 'de': 2, 'fr': 3}
            X_numeric['locale_preference'] = X_numeric['locale_preference'].map(locale_mapping).fillna(0)
            categorical_mappings['locale_preference'] = locale_mapping
        
        # accessibility_needs: boolean -> float
        if 'accessibility_needs' in X_numeric.columns:
            X_numeric['accessibility_needs'] = X_numeric['accessibility_needs'].astype(float)
        
        # network_speed: categorical -> numeric
        if 'network_speed' in X_numeric.columns:
            speed_mapping = {'slow': 0, 'medium': 1, 'fast': 2}
            X_numeric['network_speed'] = X_numeric['network_speed'].map(speed_mapping)
            categorical_mappings['network_speed'] = speed_mapping
        
        # Guardar mappings para uso posterior
        self.categorical_mappings = categorical_mappings
        
        # Verificar que no hay valores NaN
        if X_numeric.isnull().any().any():
            logger.warning("Valores NaN detectados en features, rellenando con medianas")
            X_numeric = X_numeric.fillna(X_numeric.median())
        
        # Escalar features
        X_scaled = self.scaler.fit_transform(X_numeric)
        
        logger.info(f"Features escaladas: {X_scaled.shape}")
        return X_scaled
    
    def _prepare_targets(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepara los targets (variables CSS) para regresión.
        
        Args:
            df: DataFrame con columnas de variables CSS
            
        Returns:
            np.ndarray: Targets escalados
        """
        # Verificar que todas las columnas target existen
        available_targets = [col for col in self.target_columns if col in df.columns]
        missing_targets = [col for col in self.target_columns if col not in df.columns]
        
        if missing_targets:
            logger.warning(f"Variables CSS faltantes: {missing_targets}")
            raise ValueError(f"Variables CSS requeridas no encontradas: {missing_targets}")
        
        logger.info(f"Variables CSS objetivo: {available_targets}")
        
        # Extraer targets
        y_targets = df[available_targets].copy()
        
        # Verificar rangos de valores
        for col in available_targets:
            min_val = y_targets[col].min()
            max_val = y_targets[col].max()
            logger.info(f"  {col}: rango [{min_val:.4f}, {max_val:.4f}]")
        
        # Verificar que no hay valores NaN
        if y_targets.isnull().any().any():
            logger.warning("Valores NaN detectados en targets, rellenando con medianas")
            y_targets = y_targets.fillna(y_targets.median())
        
        # Escalar targets para mejorar convergencia
        y_scaled = self.target_scaler.fit_transform(y_targets)
        
        logger.info(f"Targets escalados: {y_scaled.shape}")
        return y_scaled
    
    def train_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Entrena el modelo XGBoost Regressor con validación cruzada.
        
        Args:
            X: Features de entrenamiento
            y: Targets de entrenamiento (múltiples variables CSS)
            
        Returns:
            Dict con resultados del entrenamiento
        """
        logger.info("Iniciando entrenamiento del XGBoost Regressor")
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        logger.info(f"Train set: {X_train.shape[0]} muestras")
        logger.info(f"Test set: {X_test.shape[0]} muestras")
        
        # Definir hiperparámetros para tuning
        param_grid = {
            'estimator__n_estimators': [100, 200, 300],
            'estimator__max_depth': [3, 5, 7],
            'estimator__learning_rate': [0.05, 0.1, 0.2],
            'estimator__subsample': [0.8, 0.9, 1.0],
            'estimator__colsample_bytree': [0.8, 0.9, 1.0]
        }
        
        # Crear modelo base con MultiOutputRegressor para múltiples targets
        base_xgb = xgb.XGBRegressor(
            objective='reg:squarederror',
            random_state=42,
            n_jobs=-1,
            eval_metric='rmse'
        )
        
        # Wrapper para múltiples salidas
        self.regressor = MultiOutputRegressor(base_xgb)
        
        # Grid Search con validación cruzada
        logger.info("Ejecutando Grid Search para optimización de hiperparámetros")
        grid_search = GridSearchCV(
            self.regressor,
            param_grid,
            cv=5,
            scoring='neg_mean_squared_error',  # RMSE como especifica el requerimiento
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        # Mejor modelo
        self.regressor = grid_search.best_estimator_
        logger.info(f"Mejores hiperparámetros: {grid_search.best_params_}")
        logger.info(f"Mejor RMSE CV: {np.sqrt(-grid_search.best_score_):.4f}")
        
        # Evaluar en test set
        y_pred = self.regressor.predict(X_test)
        
        # Métricas de evaluación
        mse_test = mean_squared_error(y_test, y_pred)
        rmse_test = np.sqrt(mse_test)
        mae_test = mean_absolute_error(y_test, y_pred)
        r2_test = r2_score(y_test, y_pred)
        
        # Métricas por variable CSS individual
        target_metrics = {}
        for i, target_name in enumerate(self.target_columns):
            target_mse = mean_squared_error(y_test[:, i], y_pred[:, i])
            target_rmse = np.sqrt(target_mse)
            target_mae = mean_absolute_error(y_test[:, i], y_pred[:, i])
            target_r2 = r2_score(y_test[:, i], y_pred[:, i])
            
            target_metrics[target_name] = {
                'mse': target_mse,
                'rmse': target_rmse,
                'mae': target_mae,
                'r2_score': target_r2
            }
            
            logger.info(f"  {target_name}: RMSE={target_rmse:.4f}, R²={target_r2:.4f}")
        
        # Validación cruzada en todo el dataset
        cv_scores = cross_val_score(
            self.regressor, X, y, cv=5, scoring='neg_mean_squared_error'
        )
        cv_rmse = np.sqrt(-cv_scores)
        
        # Guardar resultados
        self.training_results = {
            'best_params': grid_search.best_params_,
            'best_cv_rmse': np.sqrt(-grid_search.best_score_),
            'test_rmse': rmse_test,
            'test_mae': mae_test,
            'test_r2_score': r2_test,
            'cv_rmse_mean': cv_rmse.mean(),
            'cv_rmse_std': cv_rmse.std(),
            'target_metrics': target_metrics,
            'n_targets': len(self.target_columns),
            'target_columns': self.target_columns
        }
        
        logger.info(f"✅ Entrenamiento completado!")
        logger.info(f"RMSE en test: {rmse_test:.4f}")
        logger.info(f"R² en test: {r2_test:.4f}")
        logger.info(f"RMSE CV: {cv_rmse.mean():.4f} (±{cv_rmse.std():.4f})")
        
        return self.training_results
    
    def save_model(self) -> None:
        """
        Guarda el modelo entrenado y componentes usando Joblib.
        """
        if self.regressor is None:
            raise ValueError("Modelo no entrenado. Ejecutar train_model() primero.")
        
        logger.info("Guardando modelo y componentes...")
        
        # Guardar modelo principal
        model_path = self.models_dir / "xgboost_regressor.joblib"
        joblib.dump(self.regressor, model_path)
        logger.info(f"✅ Modelo guardado: {model_path}")
        
        # Guardar scaler de features (reutilizar el del classifier si existe)
        scaler_path = self.models_dir / "feature_scaler_regressor.joblib"
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"✅ Feature scaler guardado: {scaler_path}")
        
        # Guardar scaler de targets
        target_scaler_path = self.models_dir / "target_scaler.joblib"
        joblib.dump(self.target_scaler, target_scaler_path)
        logger.info(f"✅ Target scaler guardado: {target_scaler_path}")
        
        # Guardar metadatos y resultados
        metadata_path = self.models_dir / "regressor_metadata.json"
        metadata = {
            'training_results': self.training_results,
            'categorical_mappings': self.categorical_mappings,
            'feature_columns': self.feature_columns,
            'target_columns': self.target_columns,
            'model_type': 'XGBoostRegressor',
            'multioutput': True
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Metadatos guardados: {metadata_path}")
    
    def load_model(self) -> None:
        """
        Carga un modelo previamente entrenado.
        """
        logger.info("Cargando modelo entrenado...")
        
        model_path = self.models_dir / "xgboost_regressor.joblib"
        scaler_path = self.models_dir / "feature_scaler_regressor.joblib"
        target_scaler_path = self.models_dir / "target_scaler.joblib"
        metadata_path = self.models_dir / "regressor_metadata.json"
        
        if not all([p.exists() for p in [model_path, scaler_path, target_scaler_path, metadata_path]]):
            raise FileNotFoundError("Archivos del modelo no encontrados")
        
        self.regressor = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.target_scaler = joblib.load(target_scaler_path)
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            self.training_results = metadata['training_results']
            self.categorical_mappings = metadata['categorical_mappings']
            self.target_columns = metadata['target_columns']
        
        logger.info("✅ Modelo cargado exitosamente")
    
    def predict(self, X: np.ndarray) -> Tuple[Dict[str, float], float]:
        """
        Realiza predicciones usando el modelo entrenado.
        
        Args:
            X: Features para predicción
            
        Returns:
            Tuple[variables_css, confianza_promedio]
        """
        if self.regressor is None:
            raise ValueError("Modelo no cargado. Ejecutar load_model() o train_model()")
        
        # Escalar features
        X_scaled = self.scaler.transform(X)
        
        # Predicción
        y_pred_scaled = self.regressor.predict(X_scaled)
        
        # Desescalar predicciones
        y_pred = self.target_scaler.inverse_transform(y_pred_scaled)
        
        # Convertir a diccionario de variables CSS
        css_variables = {}
        for i, target_name in enumerate(self.target_columns):
            value = y_pred[0, i] if y_pred.ndim > 1 else y_pred[i]
            
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
        
        # Calcular confianza basada en R² promedio del entrenamiento
        confidence = self.training_results.get('test_r2_score', 0.8)
        
        return css_variables, confidence
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Obtiene la importancia promedio de las features para todas las variables CSS.
        
        Returns:
            Dict con importancia promedio de cada feature
        """
        if self.regressor is None:
            raise ValueError("Modelo no entrenado")
        
        # Para MultiOutputRegressor, necesitamos promediar importancia entre estimadores
        importances = []
        for estimator in self.regressor.estimators_:
            importances.append(estimator.feature_importances_)
        
        # Importancia promedio
        avg_importance = np.mean(importances, axis=0)
        
        feature_names = [col for col in self.feature_columns 
                        if col in self.categorical_mappings or 
                        col in ['hour_sin', 'hour_cos', 'day_sin', 'day_cos', 
                               'viewport_width', 'viewport_height', 'viewport_aspect_ratio', 
                               'viewport_area_normalized', 'touch_enabled', 'device_pixel_ratio', 
                               'prefers_dark_mode', 'avg_session_duration', 'total_clicks_last_week', 
                               'scroll_depth_avg', 'error_rate_last_week', 'preferred_text_size', 
                               'interaction_speed']]
        
        importance_dict = dict(zip(feature_names, avg_importance))
        
        # Ordenar por importancia
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))


def main():
    """
    Función principal para entrenar el XGBoost Regressor.
    """
    # Configuración
    data_path = "../../data/synthetic_training_data.csv"
    models_dir = "../models"
    
    # Crear entrenador
    trainer = XGBoostRegressorTrainer(data_path, models_dir)
    
    try:
        # Cargar y preparar datos
        X, y = trainer.load_and_prepare_data()
        
        # Entrenar modelo
        results = trainer.train_model(X, y)
        
        # Guardar modelo
        trainer.save_model()
        
        # Mostrar feature importance
        importance = trainer.get_feature_importance()
        logger.info("\n🔍 Feature Importance (Top 10):")
        for feature, imp in list(importance.items())[:10]:
            logger.info(f"  {feature}: {imp:.4f}")
        
        # Mostrar métricas por variable CSS
        logger.info("\n📊 Métricas por Variable CSS:")
        for target, metrics in results['target_metrics'].items():
            logger.info(f"  {target}:")
            logger.info(f"    RMSE: {metrics['rmse']:.4f}")
            logger.info(f"    R²: {metrics['r2_score']:.4f}")
        
        logger.info(f"\n✅ Entrenamiento del XGBoost Regressor completado exitosamente!")
        logger.info(f"RMSE final: {results['test_rmse']:.4f}")
        logger.info(f"R² final: {results['test_r2_score']:.4f}")
        
    except Exception as e:
        logger.error(f"❌ Error durante el entrenamiento: {e}")
        raise


if __name__ == "__main__":
    main()

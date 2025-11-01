"""
Script maestro de entrenamiento para XGBoost Models (Classifier + Regressor)
Entrena ambos modelos del Frontend Efímero de manera coordinada con validación completa
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    classification_report, confusion_matrix, f1_score,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.multioutput import MultiOutputRegressor
import joblib
import json
import ast
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Any, Optional
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DualXGBoostTrainer:
    """
    Entrenador maestro para ambos modelos XGBoost del Frontend Efímero.
    
    Implementa el requisito de "DOBLE PREDICCIÓN OBLIGATORIA":
    - XGBoost Classifier para clases CSS (macro-estilo)
    - XGBoost Regressor para variables CSS (ajuste fino)
    
    Con entrenamiento coordinado y validación completa.
    """
    
    def __init__(self, data_path: str, models_dir: str = "models", config: Optional[Dict] = None):
        """
        Inicializa el entrenador dual.
        
        Args:
            data_path: Ruta al archivo CSV de datos sintéticos
            models_dir: Directorio donde guardar los modelos entrenados
            config: Configuración personalizada de entrenamiento
        """
        self.data_path = Path(data_path)
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Configuración de entrenamiento
        self.config = config or self._get_default_config()
        
        # Componentes del Classifier
        self.classifier = None
        self.classifier_scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Componentes del Regressor
        self.regressor = None
        self.regressor_scaler = StandardScaler()
        self.target_scaler = StandardScaler()
        
        # Resultados del entrenamiento
        self.training_results = {
            'classifier': {},
            'regressor': {},
            'combined': {}
        }
        
        # Features compartidas (mismo procesamiento para ambos modelos)
        self.feature_columns = [
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
            'viewport_width', 'viewport_height', 'viewport_aspect_ratio', 'viewport_area_normalized',
            'touch_enabled', 'device_pixel_ratio', 'prefers_dark_mode',
            'avg_session_duration', 'total_clicks_last_week', 'scroll_depth_avg', 'error_rate_last_week',
            'preferred_text_size', 'interaction_speed', 'user_group_density',
            'locale_preference', 'accessibility_needs', 'network_speed'
        ]
        
        # Variables CSS objetivo para regresión
        self.target_columns = [
            '--font-size-base',
            '--spacing-factor',
            '--color-primary-hue',
            '--border-radius',
            '--line-height'
        ]
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Configuración por defecto para entrenamiento.
        
        Returns:
            Dict con configuración de entrenamiento
        """
        return {
            'test_size': 0.2,
            'random_state': 42,
            'cv_folds': 5,
            'n_jobs': -1,
            'verbose': 1,
            
            # Configuración del Classifier
            'classifier_params': {
                'objective': 'multi:softprob',
                'eval_metric': 'mlogloss',
                'random_state': 42,
                'n_jobs': -1
            },
            'classifier_param_grid': {
                'n_estimators': [100, 200, 300],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.05, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0],
                'colsample_bytree': [0.8, 0.9, 1.0]
            },
            
            # Configuración del Regressor
            'regressor_params': {
                'objective': 'reg:squarederror',
                'eval_metric': 'rmse',
                'random_state': 42,
                'n_jobs': -1
            },
            'regressor_param_grid': {
                'estimator__n_estimators': [100, 200, 300],
                'estimator__max_depth': [3, 5, 7],
                'estimator__learning_rate': [0.05, 0.1, 0.2],
                'estimator__subsample': [0.8, 0.9, 1.0],
                'estimator__colsample_bytree': [0.8, 0.9, 1.0]
            }
        }
    
    def load_and_prepare_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Carga y prepara los datos para ambos modelos.
        
        Returns:
            Tuple[X, y_classifier, y_regressor]: Features y targets preparados
        """
        logger.info(f"🔄 Cargando datos desde: {self.data_path}")
        
        # Cargar datos
        df = pd.read_csv(self.data_path)
        logger.info(f"📊 Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
        
        # Preparar features (compartidas entre ambos modelos)
        X = self._prepare_features(df)
        
        # Preparar targets del classifier
        y_classifier = self._prepare_classifier_targets(df)
        
        # Preparar targets del regressor
        y_regressor = self._prepare_regressor_targets(df)
        
        logger.info(f"✅ Datos preparados:")
        logger.info(f"   Features: {X.shape}")
        logger.info(f"   Classifier targets: {y_classifier.shape}")
        logger.info(f"   Regressor targets: {y_regressor.shape}")
        
        return X, y_classifier, y_regressor
    
    def _prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepara las features compartidas para ambos modelos.
        
        Args:
            df: DataFrame con los datos sintéticos
            
        Returns:
            np.ndarray: Features numéricas escaladas
        """
        # Seleccionar columnas de features
        available_features = [col for col in self.feature_columns if col in df.columns]
        missing_features = [col for col in self.feature_columns if col not in df.columns]
        
        if missing_features:
            logger.warning(f"⚠️  Features faltantes: {missing_features}")
        
        logger.info(f"🔧 Usando {len(available_features)} features")
        
        # Preparar features numéricas
        X_numeric = df[available_features].copy()
        
        # Codificar variables categóricas
        categorical_mappings = {}
        
        # Boolean features
        for bool_col in ['touch_enabled', 'prefers_dark_mode', 'accessibility_needs']:
            if bool_col in X_numeric.columns:
                X_numeric[bool_col] = X_numeric[bool_col].astype(float)
        
        # Categorical features
        categorical_maps = {
            'user_group_density': {'low': 0, 'medium': 1, 'high': 2},
            'locale_preference': {'en': 0, 'es': 1, 'de': 2, 'fr': 3},
            'network_speed': {'slow': 0, 'medium': 1, 'fast': 2}
        }
        
        for col, mapping in categorical_maps.items():
            if col in X_numeric.columns:
                X_numeric[col] = X_numeric[col].map(mapping).fillna(0)
                categorical_mappings[col] = mapping
        
        # Guardar mappings
        self.categorical_mappings = categorical_mappings
        
        # Manejar valores NaN
        if X_numeric.isnull().any().any():
            logger.warning("⚠️  Rellenando valores NaN con medianas")
            X_numeric = X_numeric.fillna(X_numeric.median())
        
        # Escalar features (usar el mismo scaler para ambos modelos)
        X_scaled = self.classifier_scaler.fit_transform(X_numeric)
        
        logger.info(f"✅ Features escaladas: {X_scaled.shape}")
        return X_scaled
    
    def _prepare_classifier_targets(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepara las etiquetas para el clasificador.
        
        Args:
            df: DataFrame con columna 'css_classes'
            
        Returns:
            np.ndarray: Etiquetas numéricas
        """
        css_classes_list = []
        for css_string in df['css_classes']:
            try:
                classes = ast.literal_eval(css_string)
                if isinstance(classes, list):
                    class_string = '|'.join(sorted(classes))
                    css_classes_list.append(class_string)
                else:
                    css_classes_list.append('densidad-media|fuente-sans|modo-claro')
            except (ValueError, SyntaxError):
                logger.warning(f"⚠️  Error parseando CSS classes: {css_string}")
                css_classes_list.append('densidad-media|fuente-sans|modo-claro')
        
        y_encoded = self.label_encoder.fit_transform(css_classes_list)
        
        # Guardar mapeo de clases
        self.class_mappings = {
            i: classes.split('|') for i, classes in enumerate(self.label_encoder.classes_)
        }
        
        logger.info(f"🎯 Clases CSS encontradas: {len(self.label_encoder.classes_)}")
        return y_encoded
    
    def _prepare_regressor_targets(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepara los targets para el regressor.
        
        Args:
            df: DataFrame con columnas de variables CSS
            
        Returns:
            np.ndarray: Targets escalados
        """
        available_targets = [col for col in self.target_columns if col in df.columns]
        missing_targets = [col for col in self.target_columns if col not in df.columns]
        
        if missing_targets:
            raise ValueError(f"Variables CSS requeridas no encontradas: {missing_targets}")
        
        y_targets = df[available_targets].copy()
        
        # Log rangos de valores
        for col in available_targets:
            min_val = y_targets[col].min()
            max_val = y_targets[col].max()
            logger.info(f"  📏 {col}: [{min_val:.4f}, {max_val:.4f}]")
        
        # Manejar valores NaN
        if y_targets.isnull().any().any():
            logger.warning("⚠️  Rellenando valores NaN en targets")
            y_targets = y_targets.fillna(y_targets.median())
        
        # Escalar targets
        y_scaled = self.target_scaler.fit_transform(y_targets)
        
        logger.info(f"✅ Targets escalados: {y_scaled.shape}")
        return y_scaled
    
    def train_models(self, X: np.ndarray, y_classifier: np.ndarray, y_regressor: np.ndarray) -> Dict[str, Any]:
        """
        Entrena ambos modelos de manera coordinada.
        
        Args:
            X: Features de entrenamiento
            y_classifier: Targets del clasificador
            y_regressor: Targets del regressor
            
        Returns:
            Dict con resultados completos del entrenamiento
        """
        logger.info("🚀 Iniciando entrenamiento dual de modelos XGBoost")
        start_time = time.time()
        
        # Split común para ambos modelos
        X_train, X_test, y_class_train, y_class_test, y_reg_train, y_reg_test = train_test_split(
            X, y_classifier, y_regressor,
            test_size=self.config['test_size'],
            random_state=self.config['random_state'],
            stratify=y_classifier  # Estratificar por clases CSS
        )
        
        logger.info(f"📊 Train set: {X_train.shape[0]} muestras")
        logger.info(f"📊 Test set: {X_test.shape[0]} muestras")
        
        # Entrenar Classifier
        logger.info("\n🎯 Entrenando XGBoost Classifier...")
        classifier_results = self._train_classifier(
            X_train, X_test, y_class_train, y_class_test, X, y_classifier
        )
        
        # Entrenar Regressor
        logger.info("\n📈 Entrenando XGBoost Regressor...")
        regressor_results = self._train_regressor(
            X_train, X_test, y_reg_train, y_reg_test, X, y_regressor
        )
        
        # Resultados combinados
        total_time = time.time() - start_time
        combined_results = {
            'training_time_seconds': total_time,
            'training_time_formatted': f"{total_time/60:.2f} minutos",
            'training_date': datetime.now().isoformat(),
            'data_size': len(X),
            'test_size': len(X_test),
            'n_features': X.shape[1],
            'classifier_f1_score': classifier_results['test_f1_score'],
            'regressor_r2_score': regressor_results['test_r2_score'],
            'regressor_rmse': regressor_results['test_rmse']
        }
        
        # Guardar todos los resultados
        self.training_results = {
            'classifier': classifier_results,
            'regressor': regressor_results,
            'combined': combined_results
        }
        
        logger.info(f"\n✅ Entrenamiento dual completado en {total_time/60:.2f} minutos")
        logger.info(f"🎯 Classifier F1-Score: {classifier_results['test_f1_score']:.4f}")
        logger.info(f"📈 Regressor R²: {regressor_results['test_r2_score']:.4f}")
        
        return self.training_results
    
    def _train_classifier(self, X_train, X_test, y_train, y_test, X_full, y_full) -> Dict[str, Any]:
        """Entrena el modelo clasificador."""
        # Grid Search
        xgb_classifier = xgb.XGBClassifier(**self.config['classifier_params'])
        
        grid_search = GridSearchCV(
            xgb_classifier,
            self.config['classifier_param_grid'],
            cv=self.config['cv_folds'],
            scoring='f1_macro',
            n_jobs=self.config['n_jobs'],
            verbose=self.config['verbose']
        )
        
        grid_search.fit(X_train, y_train)
        self.classifier = grid_search.best_estimator_
        
        # Evaluación
        y_pred = self.classifier.predict(X_test)
        y_pred_proba = self.classifier.predict_proba(X_test)
        
        f1_test = f1_score(y_test, y_pred, average='macro')
        classification_rep = classification_report(y_test, y_pred, output_dict=True)
        
        # CV scores
        cv_scores = cross_val_score(self.classifier, X_full, y_full, cv=5, scoring='f1_macro')
        
        return {
            'best_params': grid_search.best_params_,
            'best_cv_score': grid_search.best_score_,
            'test_f1_score': f1_test,
            'cv_scores_mean': cv_scores.mean(),
            'cv_scores_std': cv_scores.std(),
            'classification_report': classification_rep,
            'feature_importance': self.classifier.feature_importances_.tolist(),
            'n_classes': len(self.label_encoder.classes_)
        }
    
    def _train_regressor(self, X_train, X_test, y_train, y_test, X_full, y_full) -> Dict[str, Any]:
        """Entrena el modelo regressor."""
        # Usar el mismo scaler que el classifier para features
        X_train_scaled = self.regressor_scaler.fit_transform(
            self.classifier_scaler.inverse_transform(X_train)
        )
        X_test_scaled = self.regressor_scaler.transform(
            self.classifier_scaler.inverse_transform(X_test)
        )
        X_full_scaled = self.regressor_scaler.transform(
            self.classifier_scaler.inverse_transform(X_full)
        )
        
        # Modelo con MultiOutput
        base_xgb = xgb.XGBRegressor(**self.config['regressor_params'])
        regressor = MultiOutputRegressor(base_xgb)
        
        grid_search = GridSearchCV(
            regressor,
            self.config['regressor_param_grid'],
            cv=self.config['cv_folds'],
            scoring='neg_mean_squared_error',
            n_jobs=self.config['n_jobs'],
            verbose=self.config['verbose']
        )
        
        grid_search.fit(X_train_scaled, y_train)
        self.regressor = grid_search.best_estimator_
        
        # Evaluación
        y_pred = self.regressor.predict(X_test_scaled)
        
        mse_test = mean_squared_error(y_test, y_pred)
        rmse_test = np.sqrt(mse_test)
        mae_test = mean_absolute_error(y_test, y_pred)
        r2_test = r2_score(y_test, y_pred)
        
        # Métricas por target
        target_metrics = {}
        for i, target_name in enumerate(self.target_columns):
            target_mse = mean_squared_error(y_test[:, i], y_pred[:, i])
            target_rmse = np.sqrt(target_mse)
            target_r2 = r2_score(y_test[:, i], y_pred[:, i])
            
            target_metrics[target_name] = {
                'mse': target_mse,
                'rmse': target_rmse,
                'r2_score': target_r2
            }
        
        # CV scores
        cv_scores = cross_val_score(
            self.regressor, X_full_scaled, y_full, cv=5, scoring='neg_mean_squared_error'
        )
        cv_rmse = np.sqrt(-cv_scores)
        
        return {
            'best_params': grid_search.best_params_,
            'best_cv_rmse': np.sqrt(-grid_search.best_score_),
            'test_rmse': rmse_test,
            'test_mae': mae_test,
            'test_r2_score': r2_test,
            'cv_rmse_mean': cv_rmse.mean(),
            'cv_rmse_std': cv_rmse.std(),
            'target_metrics': target_metrics,
            'n_targets': len(self.target_columns)
        }
    
    def save_models(self) -> None:
        """
        Guarda ambos modelos y todos los componentes.
        """
        logger.info("💾 Guardando modelos y componentes...")
        
        # Guardar classifier
        joblib.dump(self.classifier, self.models_dir / "xgboost_classifier_dual.joblib")
        joblib.dump(self.label_encoder, self.models_dir / "label_encoder_dual.joblib")
        
        # Guardar regressor
        joblib.dump(self.regressor, self.models_dir / "xgboost_regressor_dual.joblib")
        joblib.dump(self.target_scaler, self.models_dir / "target_scaler_dual.joblib")
        
        # Guardar scalers compartidos
        joblib.dump(self.classifier_scaler, self.models_dir / "feature_scaler_dual.joblib")
        joblib.dump(self.regressor_scaler, self.models_dir / "regressor_feature_scaler_dual.joblib")
        
        # Guardar metadatos completos
        metadata = {
            'training_results': self.training_results,
            'categorical_mappings': self.categorical_mappings,
            'class_mappings': {str(k): v for k, v in self.class_mappings.items()},
            'feature_columns': self.feature_columns,
            'target_columns': self.target_columns,
            'config': self.config,
            'model_type': 'DualXGBoost',
            'version': '1.0'
        }
        
        with open(self.models_dir / "dual_models_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Modelos guardados en: {self.models_dir}")
    
    def predict_dual(self, X: np.ndarray) -> Tuple[List[str], Dict[str, str], Dict[str, float]]:
        """
        Realiza predicción dual (clases + variables CSS).
        
        Args:
            X: Features para predicción
            
        Returns:
            Tuple[css_classes, css_variables, confidence_scores]
        """
        if self.classifier is None or self.regressor is None:
            raise ValueError("Modelos no entrenados")
        
        # Predicción del classifier
        X_class_scaled = self.classifier_scaler.transform(X)
        y_class_pred = self.classifier.predict(X_class_scaled)
        y_class_proba = self.classifier.predict_proba(X_class_scaled)
        
        css_classes = self.class_mappings[y_class_pred[0]]
        class_confidence = float(np.max(y_class_proba[0]))
        
        # Predicción del regressor
        X_reg_scaled = self.regressor_scaler.transform(X)
        y_reg_pred_scaled = self.regressor.predict(X_reg_scaled)
        y_reg_pred = self.target_scaler.inverse_transform(y_reg_pred_scaled)
        
        # Formatear variables CSS
        css_variables = {}
        for i, target_name in enumerate(self.target_columns):
            value = y_reg_pred[0, i]
            
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
        
        # Confianza del regressor basada en R²
        reg_confidence = self.training_results['regressor']['test_r2_score']
        
        confidence_scores = {
            'classifier_confidence': class_confidence,
            'regressor_confidence': reg_confidence,
            'combined_confidence': (class_confidence + reg_confidence) / 2
        }
        
        return css_classes, css_variables, confidence_scores


def main():
    """
    Función principal para entrenar ambos modelos XGBoost.
    """
    # Configuración
    data_path = "../../data/synthetic_training_data.csv"
    models_dir = "../models"
    
    logger.info("🎯 Iniciando entrenamiento dual XGBoost para Frontend Efímero")
    
    # Crear entrenador dual
    trainer = DualXGBoostTrainer(data_path, models_dir)
    
    try:
        # Cargar y preparar datos
        X, y_classifier, y_regressor = trainer.load_and_prepare_data()
        
        # Entrenar ambos modelos
        results = trainer.train_models(X, y_classifier, y_regressor)
        
        # Guardar modelos
        trainer.save_models()
        
        # Reporte final
        logger.info("\n" + "="*80)
        logger.info("🏆 RESUMEN FINAL DEL ENTRENAMIENTO DUAL")
        logger.info("="*80)
        
        # Resultados del Classifier
        class_results = results['classifier']
        logger.info(f"🎯 XGBoost Classifier:")
        logger.info(f"   F1-Score: {class_results['test_f1_score']:.4f}")
        logger.info(f"   CV Score: {class_results['cv_scores_mean']:.4f} ± {class_results['cv_scores_std']:.4f}")
        logger.info(f"   Clases: {class_results['n_classes']}")
        
        # Resultados del Regressor
        reg_results = results['regressor']
        logger.info(f"📈 XGBoost Regressor:")
        logger.info(f"   RMSE: {reg_results['test_rmse']:.4f}")
        logger.info(f"   R²: {reg_results['test_r2_score']:.4f}")
        logger.info(f"   Variables: {reg_results['n_targets']}")
        
        # Resultados combinados
        combined = results['combined']
        logger.info(f"⚡ Entrenamiento:")
        logger.info(f"   Tiempo total: {combined['training_time_formatted']}")
        logger.info(f"   Datos: {combined['data_size']} muestras")
        logger.info(f"   Features: {combined['n_features']}")
        
        logger.info("\n✅ Entrenamiento dual completado exitosamente!")
        
    except Exception as e:
        logger.error(f"❌ Error durante el entrenamiento: {e}")
        raise


if __name__ == "__main__":
    main()
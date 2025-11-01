"""
Script de entrenamiento para XGBoost Classifier
Entrena modelo para predicción de clases CSS del Frontend Efímero
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import joblib
import json
import ast
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XGBoostClassifierTrainer:
    """
    Entrenador del XGBoost Classifier para predicción de clases CSS.
    
    Implementa el requisito de "XGBoost Classifier for CSS class prediction"
    con clases como 'densidad-alta', 'fuente-serif', 'modo-nocturno'.
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
        self.classifier = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
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
    
    def load_and_prepare_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Carga y prepara los datos sintéticos para entrenamiento.
        
        Returns:
            Tuple[X, y]: Features y etiquetas preparadas
        """
        logger.info(f"Cargando datos desde: {self.data_path}")
        
        # Cargar datos
        df = pd.read_csv(self.data_path)
        logger.info(f"Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
        
        # Preparar features (X)
        X = self._prepare_features(df)
        
        # Preparar target (y) - convertir clases CSS a etiquetas numéricas
        y = self._prepare_target(df)
        
        logger.info(f"Features preparadas: {X.shape}")
        logger.info(f"Target preparado: {y.shape}")
        logger.info(f"Clases únicas: {len(np.unique(y))}")
        
        return X, y
    
    def _prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepara las features para el entrenamiento.
        
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
            logger.warning("Valores NaN detectados, rellenando con medianas")
            X_numeric = X_numeric.fillna(X_numeric.median())
        
        # Escalar features
        X_scaled = self.scaler.fit_transform(X_numeric)
        
        logger.info(f"Features escaladas: {X_scaled.shape}")
        return X_scaled
    
    def _prepare_target(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepara las etiquetas target convirtiendo clases CSS a números.
        
        Args:
            df: DataFrame con columna 'css_classes'
            
        Returns:
            np.ndarray: Etiquetas numéricas
        """
        # Parsear las clases CSS desde strings
        css_classes_list = []
        for css_string in df['css_classes']:
            try:
                # Convertir string representation de lista a lista real
                classes = ast.literal_eval(css_string)
                if isinstance(classes, list):
                    # Convertir lista a string concatenado para LabelEncoder
                    class_string = '|'.join(sorted(classes))
                    css_classes_list.append(class_string)
                else:
                    css_classes_list.append('densidad-media|fuente-sans|modo-claro')  # Default
            except (ValueError, SyntaxError):
                logger.warning(f"Error parseando CSS classes: {css_string}")
                css_classes_list.append('densidad-media|fuente-sans|modo-claro')  # Default
        
        # Codificar combinaciones de clases como etiquetas numéricas
        y_encoded = self.label_encoder.fit_transform(css_classes_list)
        
        # Guardar el mapeo para referencia - convertir strings de vuelta a listas
        self.class_mappings = {
            i: classes.split('|') for i, classes in enumerate(self.label_encoder.classes_)
        }
        
        logger.info(f"Clases CSS únicas encontradas: {len(self.label_encoder.classes_)}")
        for i, classes in enumerate(list(self.class_mappings.values())[:10]):  # Mostrar primeras 10
            logger.info(f"  Clase {i}: {classes}")
        
        return y_encoded
    
    def train_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Entrena el modelo XGBoost Classifier con validación cruzada.
        
        Args:
            X: Features de entrenamiento
            y: Etiquetas de entrenamiento
            
        Returns:
            Dict con resultados del entrenamiento
        """
        logger.info("Iniciando entrenamiento del XGBoost Classifier")
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"Train set: {X_train.shape[0]} muestras")
        logger.info(f"Test set: {X_test.shape[0]} muestras")
        
        # Definir hiperparámetros para tuning
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.05, 0.1, 0.2],
            'subsample': [0.8, 0.9, 1.0],
            'colsample_bytree': [0.8, 0.9, 1.0]
        }
        
        # Crear modelo base
        xgb_model = xgb.XGBClassifier(
            objective='multi:softprob',
            random_state=42,
            n_jobs=-1,
            eval_metric='mlogloss'
        )
        
        # Grid Search con validación cruzada
        logger.info("Ejecutando Grid Search para optimización de hiperparámetros")
        grid_search = GridSearchCV(
            xgb_model,
            param_grid,
            cv=5,
            scoring='f1_macro',  # F1-Score como especifica el requerimiento
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        # Mejor modelo
        self.classifier = grid_search.best_estimator_
        logger.info(f"Mejores hiperparámetros: {grid_search.best_params_}")
        logger.info(f"Mejor F1-Score CV: {grid_search.best_score_:.4f}")
        
        # Evaluar en test set
        y_pred = self.classifier.predict(X_test)
        y_pred_proba = self.classifier.predict_proba(X_test)
        
        # Métricas de evaluación
        f1_test = f1_score(y_test, y_pred, average='macro')
        classification_rep = classification_report(y_test, y_pred, output_dict=True)
        confusion_mat = confusion_matrix(y_test, y_pred)
        
        # Validación cruzada en todo el dataset
        cv_scores = cross_val_score(self.classifier, X, y, cv=5, scoring='f1_macro')
        
        # Guardar resultados
        self.training_results = {
            'best_params': grid_search.best_params_,
            'best_cv_score': grid_search.best_score_,
            'test_f1_score': f1_test,
            'cv_scores_mean': cv_scores.mean(),
            'cv_scores_std': cv_scores.std(),
            'classification_report': classification_rep,
            'confusion_matrix': confusion_mat.tolist(),
            'feature_importance': self.classifier.feature_importances_.tolist(),
            'n_classes': len(self.label_encoder.classes_),
            'class_mappings': {str(k): str(v) for k, v in self.class_mappings.items()}
        }
        
        logger.info(f"✅ Entrenamiento completado!")
        logger.info(f"F1-Score en test: {f1_test:.4f}")
        logger.info(f"F1-Score CV: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        
        return self.training_results
    
    def save_model(self) -> None:
        """
        Guarda el modelo entrenado y componentes usando Joblib.
        """
        if self.classifier is None:
            raise ValueError("Modelo no entrenado. Ejecutar train_model() primero.")
        
        logger.info("Guardando modelo y componentes...")
        
        # Guardar modelo principal
        model_path = self.models_dir / "xgboost_classifier.joblib"
        joblib.dump(self.classifier, model_path)
        logger.info(f"✅ Modelo guardado: {model_path}")
        
        # Guardar scaler
        scaler_path = self.models_dir / "feature_scaler.joblib"
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"✅ Scaler guardado: {scaler_path}")
        
        # Guardar label encoder
        encoder_path = self.models_dir / "label_encoder.joblib"
        joblib.dump(self.label_encoder, encoder_path)
        logger.info(f"✅ Label encoder guardado: {encoder_path}")
        
        # Guardar metadatos y resultados
        metadata_path = self.models_dir / "classifier_metadata.json"
        metadata = {
            'training_results': self.training_results,
            'categorical_mappings': self.categorical_mappings,
            'feature_columns': self.feature_columns,
            'model_type': 'XGBoostClassifier',
            'target_column': 'css_classes'
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Metadatos guardados: {metadata_path}")
    
    def load_model(self) -> None:
        """
        Carga un modelo previamente entrenado.
        """
        logger.info("Cargando modelo entrenado...")
        
        model_path = self.models_dir / "xgboost_classifier.joblib"
        scaler_path = self.models_dir / "feature_scaler.joblib"
        encoder_path = self.models_dir / "label_encoder.joblib"
        metadata_path = self.models_dir / "classifier_metadata.json"
        
        if not all([p.exists() for p in [model_path, scaler_path, encoder_path, metadata_path]]):
            raise FileNotFoundError("Archivos del modelo no encontrados")
        
        self.classifier = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.label_encoder = joblib.load(encoder_path)
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            self.training_results = metadata['training_results']
            self.categorical_mappings = metadata['categorical_mappings']
            
            # Reconstruir class_mappings desde los metadatos
            class_mappings_str = metadata['training_results']['class_mappings']
            self.class_mappings = {}
            for k, v in class_mappings_str.items():
                # Convertir string de vuelta a lista
                if isinstance(v, str) and v.startswith("['") and v.endswith("']"):
                    # Parse string representation of list
                    import ast
                    self.class_mappings[int(k)] = ast.literal_eval(v)
                elif '|' in str(v):
                    # Parse pipe-separated string
                    self.class_mappings[int(k)] = str(v).split('|')
                else:
                    # Fallback
                    self.class_mappings[int(k)] = str(v).split()
        
        logger.info("✅ Modelo cargado exitosamente")
    
    def predict(self, X: np.ndarray) -> Tuple[List[List[str]], np.ndarray]:
        """
        Realiza predicciones usando el modelo entrenado.
        
        Args:
            X: Features para predicción
            
        Returns:
            Tuple[clases_predichas, probabilidades]
        """
        if self.classifier is None:
            raise ValueError("Modelo no cargado. Ejecutar load_model() o train_model()")
        
        # Escalar features
        X_scaled = self.scaler.transform(X)
        
        # Predicción
        y_pred = self.classifier.predict(X_scaled)
        y_pred_proba = self.classifier.predict_proba(X_scaled)
        
        # Convertir etiquetas numéricas a clases CSS
        css_classes = [self.class_mappings[pred] for pred in y_pred]
        
        return css_classes, y_pred_proba
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Obtiene la importancia de las features del modelo entrenado.
        
        Returns:
            Dict con importancia de cada feature
        """
        if self.classifier is None:
            raise ValueError("Modelo no entrenado")
        
        feature_names = [col for col in self.feature_columns if col in self.categorical_mappings or col in ['hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'viewport_width', 'viewport_height', 'viewport_aspect_ratio', 'viewport_area_normalized', 'touch_enabled', 'device_pixel_ratio', 'prefers_dark_mode', 'avg_session_duration', 'total_clicks_last_week', 'scroll_depth_avg', 'error_rate_last_week', 'preferred_text_size', 'interaction_speed']]
        
        importance_dict = dict(zip(feature_names, self.classifier.feature_importances_))
        
        # Ordenar por importancia
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))


def main():
    """
    Función principal para entrenar el XGBoost Classifier.
    """
    # Configuración
    data_path = "../../data/synthetic_training_data.csv"
    models_dir = "../models"
    
    # Crear entrenador
    trainer = XGBoostClassifierTrainer(data_path, models_dir)
    
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
        
        logger.info("\n✅ Entrenamiento del XGBoost Classifier completado exitosamente!")
        logger.info(f"F1-Score final: {results['test_f1_score']:.4f}")
        
    except Exception as e:
        logger.error(f"❌ Error durante el entrenamiento: {e}")
        raise


if __name__ == "__main__":
    main()
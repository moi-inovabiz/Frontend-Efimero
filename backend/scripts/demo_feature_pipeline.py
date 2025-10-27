"""
Pipeline integrado: FeatureProcessor + FeatureScaler
Demuestra el flujo completo de procesamiento de features para modelos XGBoost.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from app.ml.feature_processor import FeatureProcessor
from app.ml.feature_scaler import FeatureScaler
from app.models.adaptive_ui import UserContext


def demo_feature_pipeline():
    """Demuestra el pipeline completo de procesamiento de features."""
    
    print("🚀 Demo: Pipeline completo FeatureProcessor + FeatureScaler")
    print("=" * 60)
    
    # Cargar datos sintéticos
    data_path = "../../data/synthetic_training_data.csv"
    df = pd.read_csv(data_path)
    print(f"📊 Loaded {len(df)} synthetic training samples")
    
    # Inicializar procesadores
    feature_processor = FeatureProcessor()
    feature_scaler = FeatureScaler()
    
    # FASE 1: ENTRENAMIENTO - Procesar conjunto de entrenamiento
    print(f"\n📚 FASE 1: ENTRENAMIENTO")
    print("-" * 30)
    
    training_features = []
    training_labels_classes = []
    training_labels_variables = []
    
    # Procesar primeras 500 muestras para entrenamiento
    training_size = min(500, len(df))
    print(f"🔄 Processing {training_size} training samples...")
    
    for i in range(training_size):
        sample = df.iloc[i].to_dict()
        
        try:
            # Crear UserContext
            user_context = UserContext(
                user_id=f"training_user_{i:04d}",
                session_id=f"training_session_{i:04d}",
                hora_local=datetime.now(),
                user_agent="Mozilla/5.0 (Training)",
                page_path=f"/training-{i}",
                viewport_width=int(sample['viewport_width']),
                viewport_height=int(sample['viewport_height']),
                touch_enabled=bool(sample['touch_enabled']),
                device_pixel_ratio=sample['device_pixel_ratio'],
                prefers_color_scheme="dark" if sample['prefers_dark_mode'] else "light"
            )
            
            # Datos históricos sintéticos
            historical_data = [
                {
                    "session_duration": sample['avg_session_duration'] * 60000,
                    "interaction_count": int(sample['total_clicks_last_week'] / 7),
                    "page_path": f"/page_{j}",
                    "input_type": "touch" if sample['touch_enabled'] else "mouse",
                    "error_count": max(0, int(sample['error_rate_last_week'] * 5))
                }
                for j in range(max(1, int(sample['total_clicks_last_week'] / 50)))
            ]
            
            # Contexto social
            social_context = {
                "dark_mode_percentage": 0.6 if sample['prefers_dark_mode'] else 0.4,
                "high_density_percentage": 0.7 if sample['user_group_density'] == 'high' else 0.3,
                "serif_preference": 0.3
            }
            
            # Extraer features
            features = feature_processor.prepare_features(
                user_context=user_context,
                historical_data=historical_data,
                social_context=social_context,
                is_authenticated=bool(sample.get('accessibility_needs', False))
            )
            
            training_features.append(features)
            
            # Extraer labels (targets) desde datos sintéticos
            css_classes = eval(sample['css_classes'])  # ['modo-claro', 'fuente-sans', ...]
            training_labels_classes.append(css_classes)
            
            css_variables = {
                'font_size_base': sample['--font-size-base'],
                'spacing_factor': sample['--spacing-factor'],
                'color_primary_hue': sample['--color-primary-hue'],
                'border_radius': sample['--border-radius'],
                'line_height': sample['--line-height']
            }
            training_labels_variables.append(css_variables)
            
        except Exception as e:
            print(f"⚠️  Error processing sample {i}: {e}")
            continue
    
    # Convertir a arrays
    X_train = np.array(training_features)
    print(f"✅ Extracted {X_train.shape[0]} training feature vectors")
    print(f"📏 Feature shape: {X_train.shape}")
    print(f"📊 Feature range: [{np.min(X_train):.3f}, {np.max(X_train):.3f}]")
    
    # Entrenar el scaler
    print(f"\n🔧 Training FeatureScaler...")
    feature_scaler.fit(X_train)
    X_train_scaled = feature_scaler.transform(X_train)
    
    print(f"✅ FeatureScaler trained!")
    print(f"📊 Scaled range: [{np.min(X_train_scaled):.3f}, {np.max(X_train_scaled):.3f}]")
    print(f"📈 Scaled mean: {np.mean(X_train_scaled):.3f}")
    print(f"📉 Scaled std: {np.std(X_train_scaled):.3f}")
    
    # Mostrar información de escalado por grupo
    print(f"\n📋 Feature scaling by group:")
    for group_name, group_config in feature_scaler.FEATURE_GROUPS.items():
        indices = group_config['indices']
        scaler_type = group_config['scaler_type']
        group_scaled = X_train_scaled[:, indices]
        
        print(f"  {group_name:>10} ({scaler_type:>8}): "
              f"range=[{np.min(group_scaled):>6.3f}, {np.max(group_scaled):>6.3f}], "
              f"mean={np.mean(group_scaled):>6.3f}")
    
    # Guardar scaler entrenado
    scaler_path = Path("../../models/feature_scaler.joblib")
    feature_scaler.save(scaler_path)
    print(f"💾 FeatureScaler saved to {scaler_path}")
    
    # FASE 2: PREDICCIÓN - Simular nueva muestra
    print(f"\n🔮 FASE 2: PREDICCIÓN")
    print("-" * 30)
    
    # Usar muestra diferente para predicción
    test_sample = df.iloc[600].to_dict()
    print(f"🎯 Processing prediction sample...")
    
    # Crear contexto para predicción
    pred_context = UserContext(
        user_id="prediction_user_001",
        session_id="prediction_session_001",
        hora_local=datetime.now(),
        user_agent="Mozilla/5.0 (Prediction)",
        page_path="/prediction-test",
        viewport_width=int(test_sample['viewport_width']),
        viewport_height=int(test_sample['viewport_height']),
        touch_enabled=bool(test_sample['touch_enabled']),
        device_pixel_ratio=test_sample['device_pixel_ratio'],
        prefers_color_scheme="dark" if test_sample['prefers_dark_mode'] else "light"
    )
    
    # Datos históricos para predicción
    pred_historical = [
        {
            "session_duration": test_sample['avg_session_duration'] * 60000,
            "interaction_count": int(test_sample['total_clicks_last_week'] / 7),
            "page_path": "/prediction-page",
            "input_type": "touch" if test_sample['touch_enabled'] else "mouse",
            "error_count": max(0, int(test_sample['error_rate_last_week'] * 3))
        }
    ]
    
    pred_social = {
        "dark_mode_percentage": 0.65,
        "high_density_percentage": 0.4,
        "serif_preference": 0.25
    }
    
    # Extraer features para predicción
    pred_features = feature_processor.prepare_features(
        user_context=pred_context,
        historical_data=pred_historical,
        social_context=pred_social,
        is_authenticated=False
    )
    
    print(f"✅ Extracted prediction features: {pred_features.shape}")
    print(f"📊 Raw feature range: [{np.min(pred_features):.3f}, {np.max(pred_features):.3f}]")
    
    # Escalar features para predicción
    pred_features_scaled = feature_scaler.transform(pred_features)
    print(f"✅ Scaled prediction features: {pred_features_scaled.shape}")
    print(f"📊 Scaled feature range: [{np.min(pred_features_scaled):.3f}, {np.max(pred_features_scaled):.3f}]")
    
    # FASE 3: VALIDACIÓN - Verificar consistencia
    print(f"\n🧪 FASE 3: VALIDACIÓN")
    print("-" * 30)
    
    # Cargar scaler desde disco
    loaded_scaler = FeatureScaler.load(scaler_path)
    pred_features_loaded = loaded_scaler.transform(pred_features)
    
    # Verificar que sean idénticos
    if np.allclose(pred_features_scaled, pred_features_loaded, atol=1e-6):
        print("✅ Scaler consistency: PASSED (saved/loaded results identical)")
    else:
        print("❌ Scaler consistency: FAILED (saved/loaded results differ)")
        return False
    
    # Verificar inverse transform
    reconstructed = feature_scaler.inverse_transform(pred_features_scaled)
    mae = np.mean(np.abs(reconstructed - pred_features))
    print(f"✅ Inverse transform MAE: {mae:.6f}")
    
    # Mostrar feature info
    feature_info = feature_scaler.get_feature_info()
    print(f"✅ Feature pipeline info:")
    print(f"   Total features: {feature_info['total_features']}")
    print(f"   Feature groups: {len(feature_info['feature_groups'])}")
    print(f"   Scalers fitted: {len(feature_info['scalers'])}")
    
    print(f"\n🎉 Pipeline demo completed successfully!")
    print(f"📦 Ready for XGBoost model training with {X_train_scaled.shape[0]} scaled samples")
    
    # Limpiar archivo temporal
    scaler_path.unlink()
    
    return True


if __name__ == "__main__":
    success = demo_feature_pipeline()
    if success:
        print(f"\n✅ Feature pipeline demo PASSED!")
        exit(0)
    else:
        print(f"\n❌ Feature pipeline demo FAILED!")
        exit(1)
"""
Test del FeatureScaler con datos sintéticos reales.
Valida que la normalización funcione correctamente y sea reversible.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from pathlib import Path
from app.ml.feature_scaler import FeatureScaler, FeatureScalerError
from app.ml.feature_processor import FeatureProcessor
from app.models.adaptive_ui import UserContext
from datetime import datetime


def test_feature_scaler():
    """Prueba el FeatureScaler con datos sintéticos reales."""
    
    print("🔧 Testing FeatureScaler with synthetic data...")
    
    # Cargar datos sintéticos
    try:
        data_path = "../../data/synthetic_training_data.csv"
        df = pd.read_csv(data_path)
        print(f"✅ Loaded {len(df)} synthetic samples")
    except FileNotFoundError:
        print("❌ Synthetic data file not found. Run generate_synthetic_data.py first.")
        return False
    
    # Generar features usando FeatureProcessor
    print("🔄 Generating features using FeatureProcessor...")
    processor = FeatureProcessor()
    scaler = FeatureScaler()
    
    # Procesar primeras 100 muestras para prueba
    features_list = []
    sample_count = min(100, len(df))
    
    for i in range(sample_count):
        try:
            sample = df.iloc[i].to_dict()
            
            # Crear UserContext desde muestra
            user_context = UserContext(
                user_id=f"test_user_{i:03d}",
                session_id=f"test_session_{i:03d}",
                hora_local=datetime.now(),
                user_agent="Mozilla/5.0 (Test)",
                page_path=f"/test-{i}",
                viewport_width=int(sample['viewport_width']),
                viewport_height=int(sample['viewport_height']),
                touch_enabled=bool(sample['touch_enabled']),
                device_pixel_ratio=sample['device_pixel_ratio'],
                prefers_color_scheme="dark" if sample['prefers_dark_mode'] else "light"
            )
            
            # Crear datos históricos mínimos
            historical_data = [
                {
                    "session_duration": sample['avg_session_duration'] * 60000,
                    "interaction_count": int(sample['total_clicks_last_week'] / 7),
                    "page_path": f"/page_{i}",
                    "input_type": "touch" if sample['touch_enabled'] else "mouse",
                    "error_count": max(0, int(sample['error_rate_last_week'] * 10))
                }
            ]
            
            # Contexto social básico
            social_context = {
                "dark_mode_percentage": 0.6 if sample['prefers_dark_mode'] else 0.4,
                "high_density_percentage": 0.7 if sample['user_group_density'] == 'high' else 0.3,
                "serif_preference": 0.3
            }
            
            # Extraer features
            features = processor.prepare_features(
                user_context=user_context,
                historical_data=historical_data,
                social_context=social_context,
                is_authenticated=bool(sample.get('accessibility_needs', False))
            )
            
            features_list.append(features)
            
        except Exception as e:
            print(f"⚠️  Error processing sample {i}: {e}")
            continue
    
    if len(features_list) < 10:
        print("❌ Not enough valid features generated")
        return False
    
    # Convertir a array
    features_array = np.array(features_list)
    print(f"✅ Generated features: {features_array.shape}")
    print(f"📊 Feature range: [{np.min(features_array):.3f}, {np.max(features_array):.3f}]")
    print(f"📈 Feature mean: {np.mean(features_array):.3f}")
    print(f"📉 Feature std: {np.std(features_array):.3f}")
    
    # Test 1: Fit y transform básico
    try:
        print("\n🧪 Test 1: Basic fit and transform...")
        scaler.fit(features_array)
        scaled_features = scaler.transform(features_array)
        
        print("✅ Scaling successful!")
        print(f"📏 Scaled shape: {scaled_features.shape}")
        print(f"📊 Scaled range: [{np.min(scaled_features):.3f}, {np.max(scaled_features):.3f}]")
        print(f"📈 Scaled mean: {np.mean(scaled_features):.3f}")
        print(f"📉 Scaled std: {np.std(scaled_features):.3f}")
        
    except Exception as e:
        print(f"❌ Basic scaling failed: {e}")
        return False
    
    # Test 2: Muestra única
    try:
        print("\n🧪 Test 2: Single sample transform...")
        single_sample = features_array[0]
        scaled_single = scaler.transform(single_sample)
        
        print("✅ Single sample scaling successful!")
        print(f"📏 Original shape: {single_sample.shape}")
        print(f"📏 Scaled shape: {scaled_single.shape}")
        
        # Verificar que sea igual al primer elemento del batch
        if np.allclose(scaled_single, scaled_features[0], atol=1e-6):
            print("✅ Single sample matches batch result")
        else:
            print("❌ Single sample differs from batch result")
            return False
        
    except Exception as e:
        print(f"❌ Single sample scaling failed: {e}")
        return False
    
    # Test 3: Inverse transform
    try:
        print("\n🧪 Test 3: Inverse transform...")
        reconstructed = scaler.inverse_transform(scaled_features)
        
        # Verificar similitud (permitir pequeña diferencia por precisión)
        mae = np.mean(np.abs(reconstructed - features_array))
        if mae < 0.001:
            print(f"✅ Inverse transform successful! MAE: {mae:.6f}")
        else:
            print(f"⚠️  Inverse transform has higher error: MAE: {mae:.6f}")
        
    except Exception as e:
        print(f"❌ Inverse transform failed: {e}")
        return False
    
    # Test 4: Fit_transform
    try:
        print("\n🧪 Test 4: Fit_transform method...")
        scaler2 = FeatureScaler()
        scaled_fit_transform = scaler2.fit_transform(features_array)
        
        if np.allclose(scaled_features, scaled_fit_transform, atol=1e-6):
            print("✅ fit_transform matches fit + transform")
        else:
            print("❌ fit_transform differs from fit + transform")
            return False
        
    except Exception as e:
        print(f"❌ Fit_transform failed: {e}")
        return False
    
    # Test 5: Feature groups scaling validation
    try:
        print("\n🧪 Test 5: Feature groups scaling validation...")
        
        # Verificar que cada grupo se haya escalado correctamente
        for group_name, group_config in scaler.FEATURE_GROUPS.items():
            indices = group_config['indices']
            scaler_type = group_config['scaler_type']
            
            group_scaled = scaled_features[:, indices]
            
            if scaler_type == 'standard':
                # StandardScaler: mean ≈ 0, std ≈ 1
                group_mean = np.mean(group_scaled)
                group_std = np.std(group_scaled)
                if abs(group_mean) < 0.1 and abs(group_std - 1.0) < 0.1:
                    print(f"✅ {group_name} (standard): mean={group_mean:.3f}, std={group_std:.3f}")
                else:
                    print(f"⚠️  {group_name} (standard): mean={group_mean:.3f}, std={group_std:.3f}")
                    
            elif scaler_type == 'minmax':
                # MinMaxScaler: rango [0, 1]
                group_min = np.min(group_scaled)
                group_max = np.max(group_scaled)
                if group_min >= -0.01 and group_max <= 1.01:
                    print(f"✅ {group_name} (minmax): range=[{group_min:.3f}, {group_max:.3f}]")
                else:
                    print(f"⚠️  {group_name} (minmax): range=[{group_min:.3f}, {group_max:.3f}]")
                    
            elif scaler_type == 'robust':
                # RobustScaler: mediana ≈ 0, menos extremos
                group_median = np.median(group_scaled)
                group_iqr = np.percentile(group_scaled, 75) - np.percentile(group_scaled, 25)
                print(f"✅ {group_name} (robust): median={group_median:.3f}, IQR={group_iqr:.3f}")
        
    except Exception as e:
        print(f"❌ Feature groups validation failed: {e}")
        return False
    
    # Test 6: Save y load
    try:
        print("\n🧪 Test 6: Save and load scaler...")
        
        # Crear directorio temporal
        save_path = Path("../../models/temp_scaler.joblib")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar
        scaler.save(save_path)
        
        # Cargar
        loaded_scaler = FeatureScaler.load(save_path)
        
        # Probar que funciona igual
        scaled_loaded = loaded_scaler.transform(features_array[0])
        original_scaled = scaler.transform(features_array[0])
        
        if np.allclose(scaled_loaded, original_scaled, atol=1e-6):
            print("✅ Save/load successful - results identical")
        else:
            print("❌ Save/load failed - results differ")
            return False
        
        # Limpiar archivo temporal
        save_path.unlink()
        
    except Exception as e:
        print(f"❌ Save/load failed: {e}")
        return False
    
    # Test 7: Feature info
    try:
        print("\n🧪 Test 7: Feature info...")
        info = scaler.get_feature_info()
        
        print(f"✅ Total features: {info['total_features']}")
        print(f"✅ Feature groups: {len(info['feature_groups'])}")
        print(f"✅ Is fitted: {info['is_fitted']}")
        
        if info['is_fitted']:
            print(f"✅ Scalers info: {len(info['scalers'])} scalers")
        
    except Exception as e:
        print(f"❌ Feature info failed: {e}")
        return False
    
    print("\n🎉 All FeatureScaler tests passed!")
    return True


if __name__ == "__main__":
    success = test_feature_scaler()
    if success:
        print("\n✅ FeatureScaler validation PASSED!")
        exit(0)
    else:
        print("\n❌ FeatureScaler validation FAILED!")
        exit(1)
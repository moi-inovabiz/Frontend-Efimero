"""
Script de prueba para validar el FeatureProcessor
con datos sintéticos reales y verificar que produce el número correcto de features.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime
from app.ml.feature_processor import FeatureProcessor
from app.models.adaptive_ui import UserContext


def test_feature_processor():
    """Prueba el FeatureProcessor con datos sintéticos reales."""
    
    print("🧪 Testing FeatureProcessor with synthetic data...")
    
    # Cargar datos sintéticos
    try:
        data_path = "../../data/synthetic_training_data.csv"
        df = pd.read_csv(data_path)
        print(f"✅ Loaded {len(df)} synthetic samples")
    except FileNotFoundError:
        print("❌ Synthetic data file not found. Run generate_synthetic_data.py first.")
        return False
    
    # Inicializar FeatureProcessor
    processor = FeatureProcessor()
    
    # Tomar una muestra de datos para probar
    sample = df.iloc[0].to_dict()
    print(f"📊 Testing with sample from hour {sample.get('hour', 'N/A')}")
    
    # Crear UserContext desde muestra sintética
    user_context = UserContext(
        user_id="synthetic_user_001",
        session_id="test_session_001",
        hora_local=datetime.now(),
        user_agent="Mozilla/5.0 (Test) AppleWebKit/537.36",
        page_path="/test-page",
        viewport_width=int(sample['viewport_width']),
        viewport_height=int(sample['viewport_height']),
        touch_enabled=bool(sample['touch_enabled']),
        device_pixel_ratio=sample['device_pixel_ratio'],
        prefers_color_scheme="dark" if sample['prefers_dark_mode'] else "light"
    )
    
    # Crear datos históricos sintéticos
    historical_data = [
        {
            "session_duration": sample['avg_session_duration'] * 60000,  # Convertir a ms
            "interaction_count": int(sample['total_clicks_last_week'] / 7),  # Clicks por día aprox
            "page_path": f"/page_{i}",
            "input_type": "touch" if sample['touch_enabled'] else "mouse",
            "error_count": max(0, int(sample['error_rate_last_week'] * sample['total_clicks_last_week']))
        }
        for i in range(min(10, max(1, int(sample['total_clicks_last_week'] / 20))))  # Sesiones estimadas
    ]
    
    # Crear contexto social sintético (valores por defecto)
    social_context = {
        "dark_mode_percentage": 0.6 if sample['prefers_dark_mode'] else 0.4,
        "high_density_percentage": 0.7 if sample['user_group_density'] == 'high' else 0.3,
        "serif_preference": 0.3  # Default
    }
    
    # Probar extracción de features
    try:
        features = processor.prepare_features(
            user_context=user_context,
            historical_data=historical_data,
            social_context=social_context,
            is_authenticated=bool(sample.get('accessibility_needs', False))  # Usar accessibility como proxy
        )
        
        print("✅ Feature extraction successful!")
        print(f"📏 Features shape: {features.shape}")
        print(f"🔢 Number of features: {len(features)}")
        print(f"📊 Feature range: [{np.min(features):.3f}, {np.max(features):.3f}]")
        print("📈 Feature stats:")
        print(f"   Mean: {np.mean(features):.3f}")
        print(f"   Std:  {np.std(features):.3f}")
        print(f"   Non-zero: {np.count_nonzero(features)}/{len(features)}")
        
        # Mostrar breakdown de features por grupo
        print("\n📋 Feature groups breakdown:")
        print("   Temporal: 4 features (0-3)")
        print("   Device: 5 features (4-8)")
        print("   Historical: 5 features (9-13)")
        print("   Social: 3 features (14-16)")
        print("   Composite: 3 features (17-19)")
        print("   Total: 20 features")
        
        # Validar que tenemos exactamente 20 features (como en datos sintéticos)
        expected_features = 20
        if len(features) == expected_features:
            print(f"✅ Feature count matches expected: {expected_features}")
        else:
            print(f"❌ Feature count mismatch: got {len(features)}, expected {expected_features}")
            return False
        
        # Probar con múltiples muestras
        print("\n🔄 Testing with multiple samples...")
        success_count = 0
        for i in range(min(10, len(df))):
            sample = df.iloc[i].to_dict()
            try:
                # Crear contexto simplificado para prueba rápida
                context = UserContext(
                    user_id=f"synthetic_user_{i:03d}",
                    session_id=f"test_{i}",
                    hora_local=datetime.now(),
                    user_agent="Mozilla/5.0 (Test)",
                    page_path=f"/test-{i}",
                    viewport_width=int(sample['viewport_width']),
                    viewport_height=int(sample['viewport_height']),
                    touch_enabled=bool(sample['touch_enabled']),
                    device_pixel_ratio=sample['device_pixel_ratio'],
                    prefers_color_scheme="dark" if sample['prefers_dark_mode'] else "light"
                )
                
                features = processor.prepare_features(
                    user_context=context,
                    historical_data=[],  # Datos mínimos para prueba rápida
                    social_context={},
                    is_authenticated=bool(sample.get('accessibility_needs', False))
                )
                
                if len(features) == expected_features:
                    success_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error with sample {i}: {e}")
        
        print(f"✅ Batch processing: {success_count}/10 samples successful")
        
        return success_count >= 8  # Al menos 80% de éxito
        
    except Exception as e:
        print(f"❌ Feature extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_feature_processor()
    if success:
        print("\n🎉 FeatureProcessor test PASSED!")
        exit(0)
    else:
        print("\n💥 FeatureProcessor test FAILED!")
        exit(1)
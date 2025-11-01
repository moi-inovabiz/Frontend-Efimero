#!/usr/bin/env python3
"""
Script simple para probar solo la integración básica del Feature Processor
"""

import sys
import os
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.models.adaptive_ui import UserContext
from app.ml.feature_processor import FeatureProcessor

def test_feature_processor_basic():
    """Prueba básica del Feature Processor"""
    print("🧪 Probando Feature Processor básico...")
    
    # 1. Crear Feature Processor
    fp = FeatureProcessor()
    print("✅ Feature Processor creado")
    
    # 2. Validar processor
    is_valid = fp.validate_processor()
    print(f"✅ Validación: {is_valid}")
    
    # 3. Obtener nombres de features
    feature_names = fp.get_feature_names()
    print(f"✅ Features disponibles: {len(feature_names)}")
    for i, name in enumerate(feature_names):
        print(f"   {i+1:2d}. {name}")
    
    # 4. Crear contexto de prueba
    context = UserContext(
        hora_local=datetime.now(),
        prefers_color_scheme="dark",
        viewport_width=1920,
        viewport_height=1080,
        touch_enabled=False,
        device_pixel_ratio=1.0,
        user_agent="test-agent",
        session_id="test-session",
        page_path="/test"
    )
    print("✅ Contexto de prueba creado")
    
    # 5. Procesar features
    try:
        features = fp.prepare_features(
            user_context=context,
            historical_data=[],
            social_context={},
            is_authenticated=True
        )
        print(f"✅ Features procesadas: {len(features)} valores")
        print(f"   Rango: [{features.min():.3f}, {features.max():.3f}]")
        print(f"   Primeros 5: {features[:5]}")
        
    except Exception as e:
        print(f"❌ Error procesando features: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_feature_processor_basic()
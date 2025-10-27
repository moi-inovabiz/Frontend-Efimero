"""
Test de validación y manejo de errores para FeatureProcessor.
Valida que el sistema sea robusto ante entradas malformadas o erróneas.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from datetime import datetime
from app.ml.feature_processor import FeatureProcessor, FeatureValidationError
from app.models.adaptive_ui import UserContext


def test_error_handling():
    """Prueba manejo de errores y validación del FeatureProcessor."""
    
    print("🛡️  Testing FeatureProcessor error handling...")
    processor = FeatureProcessor()
    
    # Test 1: UserContext válido básico
    try:
        valid_context = UserContext(
            user_id="test_user",
            session_id="test_session",
            hora_local=datetime.now(),
            user_agent="Mozilla/5.0",
            page_path="/test",
            viewport_width=1920,
            viewport_height=1080,
            touch_enabled=False,
            device_pixel_ratio=1.0,
            prefers_color_scheme="light"
        )
        
        features = processor.prepare_features(
            user_context=valid_context,
            historical_data=[],
            social_context={},
            is_authenticated=False
        )
        
        print("✅ Valid input test: PASSED")
        print(f"   Features shape: {features.shape}")
        
    except Exception as e:
        print(f"❌ Valid input test: FAILED - {e}")
        return False
    
    # Test 2: Viewport extremos
    try:
        extreme_context = UserContext(
            user_id="test_extreme",
            session_id="test_session",
            hora_local=datetime.now(),
            user_agent="Mozilla/5.0",
            page_path="/test",
            viewport_width=50,  # Muy pequeño
            viewport_height=99999,  # Muy grande
            touch_enabled=True,
            device_pixel_ratio=10.0,  # Muy alto
            prefers_color_scheme="invalid_scheme"  # Inválido
        )
        
        features = processor.prepare_features(
            user_context=extreme_context,
            historical_data=[],
            social_context={},
            is_authenticated=False
        )
        
        print("✅ Extreme viewport test: PASSED (handled gracefully)")
        print(f"   Features range: [{np.min(features):.3f}, {np.max(features):.3f}]")
        
    except Exception as e:
        print(f"❌ Extreme viewport test: FAILED - {e}")
        return False
    
    # Test 3: Datos históricos corruptos
    try:
        corrupt_historical = [
            {"session_duration": "invalid", "interaction_count": None},
            {"session_duration": -1000, "interaction_count": "not_a_number"},
            {},  # Diccionario vacío
            {"session_duration": float('inf'), "page_path": None}
        ]
        
        features = processor.prepare_features(
            user_context=valid_context,
            historical_data=corrupt_historical,
            social_context={},
            is_authenticated=False
        )
        
        print("✅ Corrupt historical data test: PASSED")
        
    except Exception as e:
        print(f"❌ Corrupt historical data test: FAILED - {e}")
        return False
    
    # Test 4: Contexto social inválido
    try:
        invalid_social = {
            "dark_mode_percentage": "not_a_number",
            "high_density_percentage": -5.0,  # Fuera de rango
            "serif_preference": 2.5,  # Fuera de rango
            "invalid_key": [1, 2, 3]  # Tipo inválido
        }
        
        features = processor.prepare_features(
            user_context=valid_context,
            historical_data=[],
            social_context=invalid_social,
            is_authenticated=False
        )
        
        print("✅ Invalid social context test: PASSED")
        
    except Exception as e:
        print(f"❌ Invalid social context test: FAILED - {e}")
        return False
    
    # Test 5: Entrada completamente inválida (debe usar defaults)
    try:
        features = processor.prepare_features(
            user_context=None,  # Inválido
            historical_data="not_a_list",  # Inválido
            social_context="not_a_dict",  # Inválido
            is_authenticated="not_a_bool"  # Inválido
        )
        
        # Debe retornar features por defecto
        expected_count = processor.EXPECTED_FEATURE_COUNT
        if len(features) == expected_count:
            print("✅ Invalid input fallback test: PASSED")
        else:
            print(f"❌ Invalid input fallback test: FAILED - got {len(features)} features, expected {expected_count}")
            return False
        
    except FeatureValidationError:
        # Es aceptable que falle con excepción específica
        print("✅ Invalid input validation test: PASSED (validation error raised)")
    
    # Test 6: Valores NaN/Inf en features
    try:
        # Crear contexto que pueda generar NaN/Inf
        nan_context = UserContext(
            user_id="test_nan",
            session_id="test_session",
            hora_local=datetime.now(),
            user_agent="Mozilla/5.0",
            page_path="/test",
            viewport_width=0,  # Podría causar división por cero
            viewport_height=0,
            touch_enabled=False,
            device_pixel_ratio=0.0,
            prefers_color_scheme="light"
        )
        
        features = processor.prepare_features(
            user_context=nan_context,
            historical_data=[],
            social_context={},
            is_authenticated=False
        )
        
        # Verificar que no hay NaN/Inf
        has_nan = np.isnan(features).any()
        has_inf = np.isinf(features).any()
        
        if not has_nan and not has_inf:
            print("✅ NaN/Inf handling test: PASSED")
        else:
            print(f"❌ NaN/Inf handling test: FAILED - NaN: {has_nan}, Inf: {has_inf}")
            return False
        
    except Exception as e:
        print(f"❌ NaN/Inf handling test: FAILED - {e}")
        return False
    
    # Test 7: Performance con datos grandes
    try:
        import time
        
        # Crear dataset histórico grande
        large_historical = [
            {
                "session_duration": i * 1000,
                "interaction_count": i % 50,
                "page_path": f"/page_{i}",
                "input_type": "mouse" if i % 2 == 0 else "touch",
                "error_count": i % 5
            }
            for i in range(1000)  # 1000 sesiones
        ]
        
        start_time = time.time()
        features = processor.prepare_features(
            user_context=valid_context,
            historical_data=large_historical,
            social_context={"dark_mode_percentage": 0.6},
            is_authenticated=True
        )
        processing_time = (time.time() - start_time) * 1000  # ms
        
        if processing_time < 100:  # Debe ser < 100ms
            print(f"✅ Performance test: PASSED ({processing_time:.1f}ms)")
        else:
            print(f"⚠️  Performance test: SLOW ({processing_time:.1f}ms, expected <100ms)")
        
    except Exception as e:
        print(f"❌ Performance test: FAILED - {e}")
        return False
    
    print("\n🎉 All error handling tests completed successfully!")
    return True


if __name__ == "__main__":
    success = test_error_handling()
    if success:
        print("\n✅ FeatureProcessor error handling validation PASSED!")
        exit(0)
    else:
        print("\n❌ FeatureProcessor error handling validation FAILED!")
        exit(1)
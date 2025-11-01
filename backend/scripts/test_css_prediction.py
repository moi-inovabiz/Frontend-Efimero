"""
Test script para validar la integración del Label Encoder en predicciones CSS
Verifica que las clases CSS se generen correctamente usando modelos reales
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime

# Añadir el directorio padre al path para imports
sys.path.append(str(Path(__file__).parent.parent))

from app.ml.model_manager import ModelManager
from app.models.adaptive_ui import UserContext
from app.core.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_label_encoder_loading():
    """Test carga del label encoder"""
    print("\n" + "="*60)
    print("🔍 TEST 1: Label Encoder Loading")
    print("="*60)
    
    try:
        # Limpiar estado y recargar modelos
        ModelManager.cleanup()
        await ModelManager.load_models()
        
        # Verificar que el label encoder se cargó
        health = ModelManager.get_system_health()
        has_label_encoder = ModelManager._label_encoder is not None
        
        print(f"✅ Modelos cargados: {health['is_loaded']}")
        print(f"✅ Label encoder cargado: {has_label_encoder}")
        print(f"   Status general: {health['overall_status']}")
        
        if has_label_encoder:
            # Obtener clases disponibles del label encoder
            try:
                classes = ModelManager._label_encoder.classes_
                print(f"   🎯 Clases disponibles ({len(classes)}): {list(classes)}")
                return True
            except Exception as e:
                print(f"   ⚠️  Error obteniendo clases: {e}")
                return False
        else:
            print(f"   ❌ Label encoder no está disponible")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de carga: {e}")
        return False


async def test_css_class_prediction():
    """Test predicción de clases CSS con datos reales"""
    print("\n" + "="*60)
    print("🔍 TEST 2: CSS Class Prediction")
    print("="*60)
    
    try:
        # Crear contexto de usuario de test
        test_context = UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme="light",
            viewport_width=1366,
            viewport_height=768,
            touch_enabled=False,
            device_pixel_ratio=1.0,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            session_id="test_css_prediction",
            page_path="/test-css-classes",
            referer=None
        )
        
        # Ejecutar predicción dual
        prediction_result = ModelManager.predict_dual(
            user_context=test_context,
            historical_data=[],
            social_context={},
            is_authenticated=False
        )
        
        print(f"✅ Predicción dual ejecutada")
        print(f"   🎨 CSS Classes: {prediction_result['css_classes']}")
        print(f"   📊 CSS Variables: {list(prediction_result['css_variables'].keys())}")
        
        # Manejar confianza que puede ser dict o float
        confidence = prediction_result['confidence']
        if isinstance(confidence, dict):
            print(f"   🎯 Confianza clasificador: {confidence.get('classifier', 0):.1f}%")
            print(f"   🎯 Confianza regressor: {confidence.get('regressor', 0):.1f}%")
            print(f"   🎯 Confianza combinada: {confidence.get('combined', 0):.1f}%")
        else:
            print(f"   🎯 Confianza: {confidence:.1f}%")
        
        # Validar que las clases sean strings válidos
        css_classes = prediction_result['css_classes']
        valid_classes = all(isinstance(cls, str) and len(cls) > 0 for cls in css_classes)
        
        print(f"   ✅ Clases válidas: {valid_classes}")
        
        return len(css_classes) > 0 and valid_classes
        
    except Exception as e:
        print(f"❌ Error en predicción CSS: {e}")
        return False


async def test_multiple_predictions():
    """Test múltiples predicciones con diferentes contextos"""
    print("\n" + "="*60)
    print("🔍 TEST 3: Multiple Predictions")
    print("="*60)
    
    test_scenarios = [
        {
            "name": "Desktop Usuario",
            "context": UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="light",
                viewport_width=1920,
                viewport_height=1080,
                touch_enabled=False,
                device_pixel_ratio=1.0,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                session_id="test_desktop",
                page_path="/desktop-test"
            )
        },
        {
            "name": "Mobile Usuario",
            "context": UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="dark", 
                viewport_width=375,
                viewport_height=812,
                touch_enabled=True,
                device_pixel_ratio=2.0,
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)",
                session_id="test_mobile",
                page_path="/mobile-test"
            )
        },
        {
            "name": "Tablet Usuario",
            "context": UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="auto",
                viewport_width=768,
                viewport_height=1024,
                touch_enabled=True,
                device_pixel_ratio=1.5,
                user_agent="Mozilla/5.0 (iPad; CPU OS 14_0)",
                session_id="test_tablet",
                page_path="/tablet-test"
            )
        }
    ]
    
    successful_predictions = 0
    
    for scenario in test_scenarios:
        try:
            print(f"\n📱 Scenario: {scenario['name']}")
            
            result = ModelManager.predict_dual(
                user_context=scenario['context'],
                historical_data=[],
                social_context={},
                is_authenticated=False
            )
            
            css_classes = result['css_classes']
            confidence = result['confidence']
            
            print(f"   🎨 Classes: {css_classes}")
            # Manejar confianza que puede ser dict o float
            if isinstance(confidence, dict):
                combined_confidence = confidence.get('combined', 0)
                print(f"   🎯 Confidence: {combined_confidence:.1f}%")
            else:
                print(f"   🎯 Confidence: {confidence:.1f}%")
            
            # Validar resultado
            conf_value = confidence.get('combined', confidence) if isinstance(confidence, dict) else confidence
            if len(css_classes) > 0 and conf_value > 0:
                successful_predictions += 1
                print(f"   ✅ Predicción exitosa")
            else:
                print(f"   ❌ Predicción inválida")
                
        except Exception as e:
            print(f"   ❌ Error en scenario {scenario['name']}: {e}")
    
    success_rate = (successful_predictions / len(test_scenarios)) * 100
    print(f"\n📊 Success Rate: {successful_predictions}/{len(test_scenarios)} ({success_rate:.1f}%)")
    
    return successful_predictions == len(test_scenarios)


async def test_label_encoder_fallback():
    """Test comportamiento cuando label encoder no está disponible"""
    print("\n" + "="*60)
    print("🔍 TEST 4: Label Encoder Fallback")
    print("="*60)
    
    try:
        # Temporalmente remover label encoder
        original_encoder = ModelManager._label_encoder
        ModelManager._label_encoder = None
        
        print("🔄 Label encoder temporalmente deshabilitado")
        
        # Crear contexto de test
        test_context = UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme="light",
            viewport_width=1280,
            viewport_height=720,
            touch_enabled=False,
            device_pixel_ratio=1.0,
            user_agent="Mozilla/5.0 (Test Browser)",
            session_id="test_fallback",
            page_path="/fallback-test"
        )
        
        # Ejecutar predicción sin label encoder
        result = ModelManager.predict_dual(
            user_context=test_context,
            historical_data=[],
            social_context={},
            is_authenticated=False
        )
        
        print(f"✅ Predicción fallback ejecutada")
        print(f"   🎨 Fallback Classes: {result['css_classes']}")
        
        # Manejar confianza que puede ser dict o float
        confidence = result['confidence']
        if isinstance(confidence, dict):
            combined_confidence = confidence.get('combined', 0)
            print(f"   🎯 Confidence: {combined_confidence:.1f}%")
        else:
            print(f"   🎯 Confidence: {confidence:.1f}%")
        
        # Restaurar label encoder
        ModelManager._label_encoder = original_encoder
        print("🔄 Label encoder restaurado")
        
        # Verificar que las clases fallback son válidas
        fallback_valid = len(result['css_classes']) > 0
        print(f"   ✅ Fallback funcional: {fallback_valid}")
        
        return fallback_valid
        
    except Exception as e:
        # Asegurar restauración en caso de error
        ModelManager._label_encoder = original_encoder
        print(f"❌ Error en test fallback: {e}")
        return False


async def main():
    """Ejecuta todos los tests de CSS class prediction"""
    print("🚀 INICIANDO TESTS DE CSS CLASS PREDICTION")
    print("="*80)
    
    tests = [
        ("Label Encoder Loading", test_label_encoder_loading),
        ("CSS Class Prediction", test_css_class_prediction),
        ("Multiple Predictions", test_multiple_predictions),
        ("Label Encoder Fallback", test_label_encoder_fallback)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "="*80)
    print("📋 RESUMEN DE TESTS CSS CLASS PREDICTION")
    print("="*80)
    
    passed = 0
    for test_name, result in results:
        icon = "✅" if result else "❌"
        status = "PASS" if result else "FAIL"
        print(f"{icon} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ¡Todos los tests de CSS class prediction pasaron!")
        print("   El sistema de predicción de clases CSS está funcionando correctamente.")
    else:
        print("⚠️  Algunos tests fallaron. Revisar logs para detalles.")
    
    return passed == len(tests)


if __name__ == "__main__":
    asyncio.run(main())
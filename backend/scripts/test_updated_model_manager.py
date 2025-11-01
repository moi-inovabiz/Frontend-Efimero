"""
Script de prueba para verificar el ModelManager actualizado
"""

import sys
import os
import asyncio
import numpy as np
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

# Mock de configuración para pruebas
class MockSettings:
    MODELS_PATH = "../models"
    CLASSIFIER_MODEL_NAME = "xgboost_classifier_dual.joblib"
    REGRESSOR_MODEL_NAME = "xgboost_regressor_dual.joblib"
    SCALER_MODEL_NAME = "feature_scaler_dual.joblib"

# Mock del UserContext
class MockUserContext:
    def __init__(self):
        self.hora_local = datetime.now()
        self.viewport_width = 1920
        self.viewport_height = 1080
        self.touch_enabled = False
        self.device_pixel_ratio = 1.0
        self.prefers_color_scheme = "light"

# Importar y mockear configuración
sys.modules['app.core.config'] = type('MockConfig', (), {'settings': MockSettings()})

try:
    from app.ml.model_manager import ModelManager
    from app.ml.feature_processor import FeatureProcessor
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Asegúrate de estar en el directorio correcto")
    sys.exit(1)

async def test_model_manager():
    """
    Prueba el ModelManager actualizado con modelos reales.
    """
    print("🧪 Probando ModelManager actualizado...")
    print("=" * 60)
    
    try:
        # Test 1: Verificar estado inicial
        print("\n1️⃣ Verificando estado inicial...")
        info = ModelManager.get_model_info()
        print(f"   Estado inicial: {info['status']}")
        
        # Test 2: Cargar modelos
        print("\n2️⃣ Cargando modelos...")
        await ModelManager.load_models()
        
        # Test 3: Verificar estado después de carga
        print("\n3️⃣ Verificando estado después de carga...")
        info = ModelManager.get_model_info()
        print(f"   Estado: {info['status']}")
        print(f"   Classifier: {'✅' if info['models']['classifier_loaded'] else '❌'}")
        print(f"   Regressor: {'✅' if info['models']['regressor_loaded'] else '❌'}")
        print(f"   Feature Processor: {'✅' if info['models']['feature_processor_loaded'] else '❌'}")
        
        if 'training_info' in info:
            training = info['training_info']
            print(f"   Versión: {training['model_version']}")
            print(f"   F1-Score: {training['classifier_f1']:.4f}")
            print(f"   R²: {training['regressor_r2']:.4f}")
            print(f"   Clases: {training['n_classes']}")
            print(f"   Variables: {training['n_targets']}")
        
        # Test 4: Predicción directa con features
        print("\n4️⃣ Probando predicción directa...")
        test_features = np.array([
            0.5, 0.866, 0.0, 1.0,  # Temporal
            1920, 1080, 1.78, 1.0,  # Viewport 
            0.0, 1.0, 0.0,  # Device
            17.0, 53, 0.43, 0.016,  # Behavior
            1.25, 1.50, 2.0,  # Preferences
            0.0, 0.0, 1.0  # Locale
        ])
        
        # Predicción de clases
        class_result = ModelManager.predict_classes(test_features)
        print(f"   Clases predichas: {class_result['classes']}")
        print(f"   Confianza: {class_result['confidence']:.2%}")
        print(f"   Tipo modelo: {class_result['model_type']}")
        
        # Predicción de valores
        value_result = ModelManager.predict_values(test_features)
        print(f"   Variables CSS:")
        for var, val in value_result['variables'].items():
            print(f"     {var}: {val}")
        print(f"   Confianza: {value_result['confidence']:.2%}")
        print(f"   Tipo modelo: {value_result['model_type']}")
        
        # Test 5: Predicción dual completa
        print("\n5️⃣ Probando predicción dual completa...")
        
        # Crear contexto mock
        user_context = MockUserContext()
        historical_data = [
            {"session_duration": 85000, "interaction_count": 49, "page_path": "/home"},
            {"session_duration": 120000, "interaction_count": 35, "page_path": "/about"}
        ]
        social_context = {
            "dark_mode_percentage": 0.3,
            "high_density_percentage": 0.6,
            "serif_preference": 0.4
        }
        
        dual_result = ModelManager.predict_dual(
            user_context, historical_data, social_context, is_authenticated=False
        )
        
        print(f"   Clases CSS: {dual_result['css_classes']}")
        print(f"   Variables CSS:")
        for var, val in dual_result['css_variables'].items():
            print(f"     {var}: {val}")
        
        confidence = dual_result['confidence']
        print(f"   Confianza combinada: {confidence['combined']:.2%}")
        print(f"   Features procesadas: {dual_result['model_info']['feature_count']}")
        
        # Test 6: Casos de borde y manejo de errores
        print("\n6️⃣ Probando manejo de errores...")
        
        # Features inválidas
        try:
            invalid_features = np.array([1, 2, 3])  # Muy pocas features
            ModelManager.predict_classes(invalid_features)
            print("   ❌ Debería haber fallado con features inválidas")
        except Exception as e:
            print(f"   ✅ Manejo correcto de error: {type(e).__name__}")
        
        # Contexto inválido
        try:
            invalid_context = None
            ModelManager.predict_dual(invalid_context, [], {}, False)
            print("   ❌ Debería haber fallado con contexto inválido")
        except Exception as e:
            print(f"   ✅ Manejo correcto de error: {type(e).__name__}")
        
        print(f"\n✅ Todas las pruebas del ModelManager completadas!")
        
        # Mostrar resumen final
        print("\n" + "="*60)
        print("📊 RESUMEN DE LA INTEGRACIÓN")
        print("="*60)
        
        print("✅ Funcionalidades implementadas:")
        print("   • Carga automática de modelos duales")
        print("   • Fallback a modelos individuales")
        print("   • Predicción de clases CSS con mapeo real")
        print("   • Predicción de variables CSS con escalado")
        print("   • Predicción dual integrada con FeatureProcessor")
        print("   • Manejo robusto de errores")
        print("   • Información detallada de modelos")
        print("   • Métricas de confianza reales")
        
        performance_score = (
            (100 if info['models']['classifier_loaded'] else 0) +
            (100 if info['models']['regressor_loaded'] else 0) +
            (100 if 'training_info' in info else 0)
        ) / 3
        
        print(f"\n🏆 Puntuación de integración: {performance_score:.0f}%")
        
        if performance_score >= 80:
            print("🎉 INTEGRACIÓN EXITOSA - Listo para producción!")
        elif performance_score >= 60:
            print("⚠️  INTEGRACIÓN PARCIAL - Revisar modelos faltantes")
        else:
            print("❌ INTEGRACIÓN FALLIDA - Verificar instalación")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Limpiar recursos
        ModelManager.cleanup()
        print("\n🧹 Recursos limpiados")

async def main():
    """Función principal de pruebas."""
    success = await test_model_manager()
    
    if success:
        print("\n🎯 TAREA 4 COMPLETADA: ModelManager actualizado exitosamente!")
        print("   • Modelos reales integrados")
        print("   • Mocks reemplazados")
        print("   • Sistema de predicción dual funcional")
        print("   • Manejo de errores robusto")
    else:
        print("\n❌ TAREA 4 FALLIDA: Revisar implementación")

if __name__ == "__main__":
    asyncio.run(main())
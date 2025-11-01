"""
Test script para el sistema de health checks del ML pipeline
Valida todas las funcionalidades de monitoreo y validación
"""

import asyncio
import sys
import logging
from pathlib import Path

# Añadir el directorio padre al path para imports
sys.path.append(str(Path(__file__).parent.parent))

from app.ml.model_manager import ModelManager
from app.core.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_basic_health_check():
    """Test básico de health check"""
    print("\n" + "="*60)
    print("🔍 TEST 1: Basic Health Check")
    print("="*60)
    
    try:
        health = ModelManager.get_system_health()
        print(f"✅ Health check básico ejecutado")
        print(f"   Status: {health['overall_status']}")
        print(f"   Loaded: {health['is_loaded']}")
        print(f"   Emergency: {health['emergency_mode']}")
        print(f"   Components: {health['components']}")
        return True
    except Exception as e:
        print(f"❌ Error en health check básico: {e}")
        return False


async def test_model_integrity_validation():
    """Test validación de integridad de modelos"""
    print("\n" + "="*60)
    print("🔍 TEST 2: Model Integrity Validation")
    print("="*60)
    
    try:
        # Asegurar que los modelos estén cargados primero
        if not ModelManager._is_loaded:
            await ModelManager.load_models()
        
        validation = await ModelManager.validate_model_integrity()
        print(f"✅ Validación de integridad ejecutada")
        print(f"   Success: {validation['success']}")
        print(f"   Timestamp: {validation['timestamp']}")
        
        # Revisar cada componente
        for comp_name, comp_data in validation['components'].items():
            status_icon = "✅" if comp_data['status'] == 'healthy' else "❌"
            print(f"   {status_icon} {comp_name}: {comp_data['status']}")
            if comp_data.get('error'):
                print(f"      Error: {comp_data['error']}")
        
        # Métricas de performance
        perf = validation['performance_metrics']
        print(f"   ⏱️  Inference time: {perf['inference_time_ms']}ms")
        print(f"   🧠 Memory usage: {perf['memory_usage_mb']}MB")
        
        # Predicciones de test
        if validation['predictions']['classifier_test']:
            cls_test = validation['predictions']['classifier_test']
            print(f"   🎯 Classifier test: {cls_test['class']} (conf: {cls_test['confidence']:.3f})")
        
        if validation['predictions']['regressor_test']:
            reg_test = validation['predictions']['regressor_test']
            print(f"   📊 Regressor test: {reg_test:.3f}")
        
        return validation['success']
    except Exception as e:
        print(f"❌ Error en validación de integridad: {e}")
        return False


async def test_detailed_health_report():
    """Test reporte detallado de salud"""
    print("\n" + "="*60)
    print("🔍 TEST 3: Detailed Health Report")
    print("="*60)
    
    try:
        detailed = await ModelManager.get_detailed_health_report()
        print(f"✅ Reporte detallado generado")
        print(f"   Overall status: {detailed['overall_status']}")
        print(f"   Validation success: {detailed['detailed_validation']['success']}")
        
        # Alertas
        if detailed.get('alerts'):
            print(f"   🚨 Alerts ({len(detailed['alerts'])}):")
            for alert in detailed['alerts']:
                print(f"      - {alert['level']}: {alert['message']}")
        
        # Recomendaciones
        if detailed.get('recommendations'):
            print(f"   💡 Recommendations ({len(detailed['recommendations'])}):")
            for rec in detailed['recommendations']:
                print(f"      - {rec}")
        
        return True
    except Exception as e:
        print(f"❌ Error en reporte detallado: {e}")
        return False


async def test_model_loading_scenarios():
    """Test diferentes escenarios de carga de modelos"""
    print("\n" + "="*60)
    print("🔍 TEST 4: Model Loading Scenarios")
    print("="*60)
    
    # Test 1: Sistema cargado normalmente
    try:
        await ModelManager.load_models()
        health_after_load = ModelManager.get_system_health()
        print(f"✅ Carga normal completada")
        print(f"   Status después de carga: {health_after_load['overall_status']}")
        print(f"   Emergency mode: {health_after_load['emergency_mode']}")
        return True
    except Exception as e:
        print(f"❌ Error en carga normal: {e}")
        return False


async def test_recovery_mechanism():
    """Test mecanismo de recuperación"""
    print("\n" + "="*60)
    print("🔍 TEST 5: Recovery Mechanism")
    print("="*60)
    
    try:
        recovery = await ModelManager.attempt_model_recovery()
        print(f"✅ Recuperación ejecutada")
        print(f"   Success: {recovery['success']}")
        print(f"   Message: {recovery.get('message', 'N/A')}")
        print(f"   Loaded components: {recovery.get('loaded_components', 'N/A')}")
        return recovery['success']
    except Exception as e:
        print(f"❌ Error en recuperación: {e}")
        return False


async def test_performance_requirements():
    """Test cumplimiento de requirements de performance"""
    print("\n" + "="*60)
    print("🔍 TEST 6: Performance Requirements")
    print("="*60)
    
    try:
        # Ejecutar múltiples validaciones para obtener métricas promedio
        times = []
        for i in range(5):
            validation = await ModelManager.validate_model_integrity()
            if validation['performance_metrics']['inference_time_ms']:
                times.append(validation['performance_metrics']['inference_time_ms'])
        
        if times:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            print(f"✅ Performance test completado ({len(times)} runs)")
            print(f"   Tiempo promedio: {avg_time:.2f}ms")
            print(f"   Tiempo mínimo: {min_time:.2f}ms")
            print(f"   Tiempo máximo: {max_time:.2f}ms")
            
            # Verificar requirement <100ms
            requirement_met = avg_time < 100
            req_icon = "✅" if requirement_met else "❌"
            print(f"   {req_icon} Requirement <100ms: {'MET' if requirement_met else 'FAILED'}")
            
            return requirement_met
        else:
            print(f"❌ No se pudieron obtener métricas de tiempo")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de performance: {e}")
        return False


async def main():
    """Ejecuta todos los tests del sistema de health checks"""
    print("🚀 INICIANDO TESTS DEL SISTEMA DE HEALTH CHECKS")
    print("="*80)
    
    tests = [
        ("Basic Health Check", test_basic_health_check),
        ("Model Integrity Validation", test_model_integrity_validation),
        ("Detailed Health Report", test_detailed_health_report),
        ("Model Loading Scenarios", test_model_loading_scenarios),
        ("Recovery Mechanism", test_recovery_mechanism),
        ("Performance Requirements", test_performance_requirements)
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
    print("📋 RESUMEN DE TESTS")
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
        print("🎉 ¡Todos los tests del sistema de health checks pasaron!")
        print("   El sistema de monitoreo está funcionando correctamente.")
    else:
        print("⚠️  Algunos tests fallaron. Revisar logs para detalles.")
    
    return passed == len(tests)


if __name__ == "__main__":
    asyncio.run(main())
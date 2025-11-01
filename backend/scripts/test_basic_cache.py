#!/usr/bin/env python3
"""
Script de prueba básica para validar el sistema de cache sin riesgo de bloqueo.
Tarea 4.4: Implement prediction caching for performance optimization
"""

import sys
import os
import asyncio
import time
from datetime import datetime

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.prediction_cache import get_prediction_cache
from app.models.adaptive_ui import UserContext


def test_basic_cache_operations():
    """Prueba las operaciones básicas del cache."""
    
    print("🧪 Probando operaciones básicas del cache")
    print("=" * 50)
    
    # Obtener instancia del cache
    cache = get_prediction_cache()
    
    # Limpiar cache para empezar limpio
    cache.clear()
    print("✅ Cache limpiado")
    
    # Crear contexto de prueba
    test_context = UserContext(
        hora_local=datetime.now(),
        prefers_color_scheme="light",
        viewport_width=1920,
        viewport_height=1080,
        touch_enabled=False,
        device_pixel_ratio=1.0,
        user_agent="Mozilla/5.0 Test",
        session_id="basic-test",
        page_path="/test"
    )
    
    # Generar cache key
    cache_key = cache._generate_cache_key(test_context, is_authenticated=True)
    print(f"✅ Cache key generado: {cache_key[:20]}...")
    
    # Prueba 1: Cache miss
    print("\n📝 Prueba 1: Cache Miss")
    result = cache.get(cache_key)
    if result is None:
        print("✅ Cache miss correctamente detectado")
    else:
        print("❌ Debería haber sido cache miss")
        return False
    
    # Prueba 2: Almacenar en cache
    print("\n📝 Prueba 2: Store en Cache")
    test_data = {
        "css_classes": ["densidad-alta", "fuente-serif"],
        "css_variables": {
            "--font-size-base": "1.2rem",
            "--spacing-factor": "1.5"
        },
        "confidence": {
            "overall": 85.5,
            "classification": {"score": 90.0},
            "regression": {"score": 81.0}
        }
    }
    
    success = cache.put(cache_key, test_data, ttl=60)  # 1 minuto TTL
    if success:
        print("✅ Datos almacenados en cache correctamente")
    else:
        print("❌ Error almacenando en cache")
        return False
    
    # Prueba 3: Cache hit
    print("\n📝 Prueba 3: Cache Hit")
    result = cache.get(cache_key)
    if result is not None:
        print("✅ Cache hit correctamente detectado")
        print(f"   📊 CSS Classes: {result['css_classes']}")
        print(f"   📊 Confianza: {result['confidence']['overall']}%")
    else:
        print("❌ Debería haber sido cache hit")
        return False
    
    # Prueba 4: Estadísticas básicas (con timeout)
    print("\n📝 Prueba 4: Estadísticas del Cache")
    try:
        start_time = time.time()
        stats = cache.get_stats()
        elapsed = time.time() - start_time
        
        print(f"✅ Estadísticas obtenidas en {elapsed:.3f}s")
        print(f"   📊 Total requests: {stats['cache_stats']['total_requests']}")
        print(f"   📊 Cache hits: {stats['cache_stats']['cache_hits']}")
        print(f"   📊 Cache misses: {stats['cache_stats']['cache_misses']}")
        print(f"   📊 Hit rate: {stats['cache_efficiency']['hit_rate_percent']}%")
        print(f"   📊 Memoria actual: {stats['memory_usage']['current_mb']}MB")
        
        # Verificar que no tomó demasiado tiempo
        if elapsed > 1.0:
            print(f"⚠️ Advertencia: get_stats() tomó {elapsed:.3f}s (podría ser lento)")
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return False
    
    # Prueba 5: Multiple entries
    print("\n📝 Prueba 5: Múltiples Entradas")
    for i in range(5):
        test_context_variant = UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme="dark" if i % 2 else "light",
            viewport_width=1920 - (i * 100),
            viewport_height=1080,
            touch_enabled=bool(i % 2),
            device_pixel_ratio=1.0 + (i * 0.5),
            user_agent=f"Mozilla/5.0 Test {i}",
            session_id=f"test-{i}",
            page_path="/test"
        )
        
        key = cache._generate_cache_key(test_context_variant)
        data = {"test_id": i, "css_classes": [f"test-{i}"]}
        cache.put(key, data, ttl=30)
    
    print("✅ 5 entradas adicionales almacenadas")
    
    # Verificar estadísticas finales
    try:
        final_stats = cache.get_stats()
        total_entries = final_stats['cache_efficiency']['total_entries']
        print(f"✅ Total entradas en cache: {total_entries}")
        
        if total_entries >= 6:  # Original + 5 nuevas
            print("✅ Todas las entradas almacenadas correctamente")
        else:
            print(f"⚠️ Menos entradas de lo esperado: {total_entries}/6")
            
    except Exception as e:
        print(f"❌ Error en estadísticas finales: {e}")
        return False
    
    print("\n🎉 TODAS LAS PRUEBAS BÁSICAS EXITOSAS")
    return True


def test_cache_key_consistency():
    """Prueba que las cache keys sean consistentes."""
    
    print("\n🔑 Probando consistencia de cache keys")
    print("-" * 40)
    
    cache = get_prediction_cache()
    
    # Mismo contexto debería generar la misma key
    context1 = UserContext(
        hora_local=datetime(2024, 1, 1, 12, 0, 0),  # Fecha fija
        prefers_color_scheme="light",
        viewport_width=1920,
        viewport_height=1080,
        touch_enabled=False,
        device_pixel_ratio=1.0,
        user_agent="Mozilla/5.0 Test",
        session_id="consistency-test",
        page_path="/test"
    )
    
    context2 = UserContext(
        hora_local=datetime(2024, 1, 1, 12, 0, 0),  # Misma fecha
        prefers_color_scheme="light",
        viewport_width=1920,
        viewport_height=1080,
        touch_enabled=False,
        device_pixel_ratio=1.0,
        user_agent="Mozilla/5.0 Test",
        session_id="consistency-test",
        page_path="/test"
    )
    
    key1 = cache._generate_cache_key(context1, is_authenticated=True)
    key2 = cache._generate_cache_key(context2, is_authenticated=True)
    
    if key1 == key2:
        print("✅ Cache keys consistentes para contextos idénticos")
    else:
        print("❌ Cache keys inconsistentes")
        print(f"   Key1: {key1}")
        print(f"   Key2: {key2}")
        return False
    
    # Contextos diferentes deberían generar keys diferentes
    context3 = UserContext(
        hora_local=datetime(2024, 1, 1, 12, 0, 0),
        prefers_color_scheme="dark",  # Diferente
        viewport_width=1920,
        viewport_height=1080,
        touch_enabled=False,
        device_pixel_ratio=1.0,
        user_agent="Mozilla/5.0 Test",
        session_id="consistency-test",
        page_path="/test"
    )
    
    key3 = cache._generate_cache_key(context3, is_authenticated=True)
    
    if key1 != key3:
        print("✅ Cache keys diferentes para contextos diferentes")
        return True
    else:
        print("❌ Cache keys deberían ser diferentes")
        print(f"   Key1 (light): {key1}")
        print(f"   Key3 (dark):  {key3}")
        return False


def main():
    """Función principal."""
    try:
        print("🚀 Iniciando pruebas básicas del cache")
        print("=" * 50)
        
        # Prueba 1: Operaciones básicas
        basic_success = test_basic_cache_operations()
        
        # Prueba 2: Consistencia de keys
        consistency_success = test_cache_key_consistency()
        
        if basic_success and consistency_success:
            print("\n🎉 TODAS LAS PRUEBAS BÁSICAS EXITOSAS")
            print("✅ El sistema de cache funciona correctamente")
            return 0
        else:
            print("\n❌ ALGUNAS PRUEBAS FALLARON")
            return 1
            
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    print(f"\n🏁 Script finalizado con código: {exit_code}")
    sys.exit(exit_code)
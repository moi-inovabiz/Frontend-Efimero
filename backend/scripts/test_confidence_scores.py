#!/usr/bin/env python3
"""
Script de prueba para validar el sistema de confianza detallada mejorado.
Tarea 4.3: Add prediction confidence scores to API response
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.adaptive_ui_service import AdaptiveUIService
from app.models.adaptive_ui import UserContext


async def test_confidence_system():
    """Prueba integral del sistema de confianza detallada."""
    
    print("🧪 Probando sistema de confianza detallada (Tarea 4.3)")
    print("=" * 60)
    
    # Inicializar servicio
    service = AdaptiveUIService()
    
    # Contextos de prueba diversos
    test_contexts = [
        {
            "name": "Desktop High-End",
            "context": UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="light",
                viewport_width=1920,
                viewport_height=1080,
                touch_enabled=False,
                device_pixel_ratio=1.0,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                session_id="test-desktop-001",
                page_path="/test"
            )
        },
        {
            "name": "Mobile Dark Mode",
            "context": UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="dark",
                viewport_width=375,
                viewport_height=812,
                touch_enabled=True,
                device_pixel_ratio=3.0,
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
                session_id="test-mobile-001",
                page_path="/test"
            )
        },
        {
            "name": "Tablet Medium",
            "context": UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="no-preference",
                viewport_width=768,
                viewport_height=1024,
                touch_enabled=True,
                device_pixel_ratio=2.0,
                user_agent="Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)",
                session_id="test-tablet-001",
                page_path="/test"
            )
        }
    ]
    
    test_results = []
    
    # Ejecutar pruebas
    for i, test_case in enumerate(test_contexts, 1):
        print(f"\n📱 Prueba {i}/3: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Generar predicción con confianza detallada
            response = await service.generate_adaptive_design(
                user_context=test_case["context"],
                user_id="test-user-confidence",
                is_authenticated=True
            )
            
            # Extraer información de confianza
            confidence = response.prediction_confidence
            
            # Validar estructura de confianza
            structure_valid = validate_confidence_structure(confidence)
            
            test_result = {
                "test_name": test_case["name"],
                "success": True,
                "structure_valid": structure_valid,
                "confidence_data": confidence,
                "design_tokens": {
                    "css_classes": response.design_tokens.css_classes,
                    "css_variables": list(response.design_tokens.css_variables.keys())
                },
                "processing_time": response.processing_time_ms
            }
            
            # Mostrar resultados
            print_confidence_summary(confidence, test_case["name"])
            
        except Exception as e:
            print(f"❌ Error en prueba {test_case['name']}: {e}")
            test_result = {
                "test_name": test_case["name"],
                "success": False,
                "error": str(e)
            }
        
        test_results.append(test_result)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS DE CONFIANZA")
    print("=" * 60)
    
    successful_tests = sum(1 for result in test_results if result.get("success", False))
    total_tests = len(test_results)
    
    print(f"✅ Pruebas exitosas: {successful_tests}/{total_tests}")
    
    if successful_tests > 0:
        # Análisis de diversidad de confianza
        analyze_confidence_diversity(test_results)
        
        # Validación de métricas
        validate_confidence_metrics(test_results)
    
    return successful_tests == total_tests


def validate_confidence_structure(confidence: Dict[str, Any]) -> bool:
    """Valida que la estructura de confianza sea correcta."""
    
    required_keys = ["classification", "regression", "overall", "detailed"]
    
    # Verificar claves principales
    if not all(key in confidence for key in required_keys):
        print("❌ Estructura de confianza incompleta")
        return False
    
    # Verificar estructura de clasificación
    classification = confidence["classification"]
    if isinstance(classification, dict):
        required_class_keys = ["score", "quality", "metrics", "prediction_certainty"]
        if not all(key in classification for key in required_class_keys):
            print("❌ Estructura de confianza de clasificación incompleta")
            return False
    
    # Verificar estructura de regresión
    regression = confidence["regression"]
    if isinstance(regression, dict):
        required_reg_keys = ["score", "quality", "metrics"]
        if not all(key in regression for key in required_reg_keys):
            print("❌ Estructura de confianza de regresión incompleta")
            return False
    
    # Verificar estructura detallada
    detailed = confidence["detailed"]
    required_detailed_keys = ["classifier_quality", "regressor_quality", "combined_quality"]
    if not all(key in detailed for key in required_detailed_keys):
        print("❌ Estructura de confianza detallada incompleta")
        return False
    
    print("✅ Estructura de confianza válida")
    return True


def print_confidence_summary(confidence: Dict[str, Any], test_name: str):
    """Imprime un resumen legible de la confianza."""
    
    print(f"📊 Confianza para {test_name}:")
    
    # Overall score
    overall = confidence.get("overall", 0)
    print(f"   🎯 Score general: {overall:.1f}%")
    
    # Clasificación
    classification = confidence.get("classification", {})
    if isinstance(classification, dict):
        class_score = classification.get("score", 0)
        class_quality = classification.get("quality", "unknown")
        class_certainty = classification.get("prediction_certainty", "unknown")
        print(f"   🏷️  Clasificación: {class_score:.1f}% ({class_quality}, {class_certainty})")
    else:
        print(f"   🏷️  Clasificación: {classification:.1f}% (legacy)")
    
    # Regresión
    regression = confidence.get("regression", {})
    if isinstance(regression, dict):
        reg_score = regression.get("score", 0)
        reg_quality = regression.get("quality", "unknown")
        print(f"   📈 Regresión: {reg_score:.1f}% ({reg_quality})")
    else:
        print(f"   📈 Regresión: {regression:.1f}% (legacy)")
    
    # Detalles adicionales
    detailed = confidence.get("detailed", {})
    if detailed:
        combined_quality = detailed.get("combined_quality", "unknown")
        print(f"   🔗 Calidad combinada: {combined_quality}")
        
        reliability = detailed.get("reliability_summary", {})
        if reliability:
            trustworthiness = reliability.get("overall_trustworthiness", "unknown")
            print(f"   🛡️  Confiabilidad: {trustworthiness}")


def analyze_confidence_diversity(test_results):
    """Analiza la diversidad en los scores de confianza."""
    
    print("\n🔍 ANÁLISIS DE DIVERSIDAD DE CONFIANZA")
    print("-" * 40)
    
    scores = []
    qualities = []
    
    for result in test_results:
        if result.get("success") and "confidence_data" in result:
            confidence = result["confidence_data"]
            overall = confidence.get("overall", 0)
            scores.append(overall)
            
            detailed = confidence.get("detailed", {})
            quality = detailed.get("combined_quality", "unknown")
            qualities.append(quality)
    
    if scores:
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        score_range = max_score - min_score
        
        print(f"📊 Scores de confianza:")
        print(f"   • Promedio: {avg_score:.1f}%")
        print(f"   • Rango: {min_score:.1f}% - {max_score:.1f}%")
        print(f"   • Variación: {score_range:.1f}%")
        
        print(f"🎯 Calidades observadas: {set(qualities)}")
        
        # Verificar diversidad
        if score_range > 10:
            print("✅ Diversidad de confianza adecuada")
        else:
            print("⚠️ Baja diversidad en scores de confianza")


def validate_confidence_metrics(test_results):
    """Valida que las métricas de confianza sean sensatas."""
    
    print("\n🔬 VALIDACIÓN DE MÉTRICAS")
    print("-" * 40)
    
    valid_metrics = 0
    total_metrics = 0
    
    for result in test_results:
        if result.get("success") and "confidence_data" in result:
            confidence = result["confidence_data"]
            
            # Validar score overall
            overall = confidence.get("overall", 0)
            if 0 <= overall <= 100:
                valid_metrics += 1
            total_metrics += 1
            
            # Validar scores individuales
            classification = confidence.get("classification", {})
            if isinstance(classification, dict):
                class_score = classification.get("score", 0)
                if 0 <= class_score <= 100:
                    valid_metrics += 1
                total_metrics += 1
            
            regression = confidence.get("regression", {})
            if isinstance(regression, dict):
                reg_score = regression.get("score", 0)
                if 0 <= reg_score <= 100:
                    valid_metrics += 1
                total_metrics += 1
    
    print(f"📐 Métricas válidas: {valid_metrics}/{total_metrics}")
    
    if valid_metrics == total_metrics:
        print("✅ Todas las métricas están en rangos válidos")
    else:
        print("⚠️ Algunas métricas fuera de rango")


async def main():
    """Función principal."""
    try:
        success = await test_confidence_system()
        
        if success:
            print("\n🎉 TODAS LAS PRUEBAS DE CONFIANZA EXITOSAS")
            print("✅ Sistema de confianza detallada funcionando correctamente")
            exit_code = 0
        else:
            print("\n❌ ALGUNAS PRUEBAS FALLARON")
            exit_code = 1
            
    except Exception as e:
        print(f"\n💥 Error crítico en pruebas: {e}")
        exit_code = 1
    
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    print(f"\n🏁 Script finalizado con código: {exit_code}")
    sys.exit(exit_code)
"""
Test script para validar las predicciones de variables CSS con XGBoost regressor
Verifica que las variables CSS se generen correctamente con valores realistas
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


async def test_target_columns_loading():
    """Test carga de target_columns desde metadata"""
    print("\n" + "="*60)
    print("🔍 TEST 1: Target Columns Loading")
    print("="*60)
    
    try:
        # Limpiar estado y recargar modelos
        ModelManager.cleanup()
        await ModelManager.load_models()
        
        # Verificar que target_columns se cargaron
        target_columns = ModelManager._target_columns
        has_target_columns = target_columns is not None
        
        print(f"✅ Modelos cargados: {ModelManager._is_loaded}")
        print(f"✅ Target columns cargadas: {has_target_columns}")
        
        if has_target_columns:
            print(f"   🎯 Target columns ({len(target_columns)}): {target_columns}")
            
            # Verificar que son las variables CSS esperadas
            expected_vars = ['--font-size-base', '--spacing-factor', '--color-primary-hue', '--border-radius', '--line-height']
            all_expected = all(var in target_columns for var in expected_vars)
            print(f"   ✅ Variables CSS esperadas presentes: {all_expected}")
            
            return True
        else:
            print(f"   ❌ Target columns no están disponibles")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de target columns: {e}")
        return False


async def test_css_variable_predictions():
    """Test predicciones de variables CSS con diferentes contextos"""
    print("\n" + "="*60)
    print("🔍 TEST 2: CSS Variable Predictions")
    print("="*60)
    
    test_scenarios = [
        {
            "name": "Desktop Normal",
            "context": UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="light",
                viewport_width=1920,
                viewport_height=1080,
                touch_enabled=False,
                device_pixel_ratio=1.0,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                session_id="test_desktop_css",
                page_path="/desktop-css"
            )
        },
        {
            "name": "Mobile Compact",
            "context": UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="dark",
                viewport_width=375,
                viewport_height=812,
                touch_enabled=True,
                device_pixel_ratio=3.0,
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0)",
                session_id="test_mobile_css",
                page_path="/mobile-css"
            )
        },
        {
            "name": "Tablet Medium",
            "context": UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="auto",
                viewport_width=1024,
                viewport_height=768,
                touch_enabled=True,
                device_pixel_ratio=2.0,
                user_agent="Mozilla/5.0 (iPad; CPU OS 15_0)",
                session_id="test_tablet_css",
                page_path="/tablet-css"
            )
        },
        {
            "name": "Wide Screen",
            "context": UserContext(
                hora_local=datetime.now(),
                prefers_color_scheme="light",
                viewport_width=2560,
                viewport_height=1440,
                touch_enabled=False,
                device_pixel_ratio=1.5,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                session_id="test_wide_css",
                page_path="/wide-css"
            )
        }
    ]
    
    successful_predictions = 0
    
    for scenario in test_scenarios:
        try:
            print(f"\n📱 Scenario: {scenario['name']}")
            
            # Ejecutar predicción dual
            result = ModelManager.predict_dual(
                user_context=scenario['context'],
                historical_data=[],
                social_context={},
                is_authenticated=False
            )
            
            css_variables = result['css_variables']
            confidence = result['confidence']
            
            print(f"   🎨 CSS Variables:")
            for var_name, var_value in css_variables.items():
                print(f"      {var_name}: {var_value}")
            
            # Obtener confianza del regressor
            regressor_confidence = confidence.get('regressor', 0) if isinstance(confidence, dict) else confidence
            print(f"   🎯 Regressor Confidence: {regressor_confidence:.1f}%")
            
            # Validar que las variables tienen valores razonables
            validation_results = validate_css_variable_values(css_variables)
            print(f"   ✅ Variables válidas: {validation_results['all_valid']}")
            
            if validation_results['all_valid'] and len(css_variables) > 0:
                successful_predictions += 1
            else:
                print(f"   ❌ Problemas encontrados: {validation_results['issues']}")
                
        except Exception as e:
            print(f"   ❌ Error en scenario {scenario['name']}: {e}")
    
    success_rate = (successful_predictions / len(test_scenarios)) * 100
    print(f"\n📊 Success Rate: {successful_predictions}/{len(test_scenarios)} ({success_rate:.1f}%)")
    
    return successful_predictions >= len(test_scenarios) * 0.75  # 75% success rate mínimo


def validate_css_variable_values(css_variables: dict) -> dict:
    """Valida que los valores de variables CSS estén en rangos apropiados"""
    validation_rules = {
        '--font-size-base': {
            'type': 'rem',
            'min': 0.75,
            'max': 2.0,
            'extract': lambda v: float(v.replace('rem', ''))
        },
        '--spacing-factor': {
            'type': 'number',
            'min': 0.5,
            'max': 2.5,
            'extract': lambda v: float(v)
        },
        '--color-primary-hue': {
            'type': 'degrees',
            'min': 0,
            'max': 360,
            'extract': lambda v: float(v)
        },
        '--border-radius': {
            'type': 'rem',
            'min': 0.0,
            'max': 1.5,
            'extract': lambda v: float(v.replace('rem', ''))
        },
        '--line-height': {
            'type': 'ratio',
            'min': 1.0,
            'max': 2.5,
            'extract': lambda v: float(v)
        }
    }
    
    issues = []
    valid_count = 0
    
    for var_name, var_value in css_variables.items():
        if var_name in validation_rules:
            rule = validation_rules[var_name]
            try:
                numeric_value = rule['extract'](var_value)
                
                if rule['min'] <= numeric_value <= rule['max']:
                    valid_count += 1
                else:
                    issues.append(f"{var_name}: {var_value} fuera del rango [{rule['min']}, {rule['max']}]")
                    
            except (ValueError, AttributeError) as e:
                issues.append(f"{var_name}: Error parseando valor '{var_value}': {e}")
        else:
            # Variables no reconocidas también se consideran válidas
            valid_count += 1
    
    return {
        'all_valid': len(issues) == 0,
        'valid_count': valid_count,
        'total_count': len(css_variables),
        'issues': issues
    }


async def test_css_variable_diversity():
    """Test que las predicciones de CSS variables muestren diversidad entre contextos"""
    print("\n" + "="*60)
    print("🔍 TEST 3: CSS Variable Diversity")
    print("="*60)
    
    # Crear contextos muy diferentes para ver si las predicciones varían
    contexts = [
        # Contexto 1: Móvil pequeño, modo oscuro
        UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme="dark",
            viewport_width=320,
            viewport_height=568,
            touch_enabled=True,
            device_pixel_ratio=2.0,
            user_agent="Mozilla/5.0 (iPhone SE)",
            session_id="diversity_test_1",
            page_path="/diversity-1"
        ),
        # Contexto 2: Desktop grande, modo claro
        UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme="light",
            viewport_width=3440,
            viewport_height=1440,
            touch_enabled=False,
            device_pixel_ratio=1.0,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            session_id="diversity_test_2",
            page_path="/diversity-2"
        ),
        # Contexto 3: Tablet mediano
        UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme="auto",
            viewport_width=768,
            viewport_height=1024,
            touch_enabled=True,
            device_pixel_ratio=2.0,
            user_agent="Mozilla/5.0 (iPad)",
            session_id="diversity_test_3",
            page_path="/diversity-3"
        )
    ]
    
    all_predictions = []
    
    for i, context in enumerate(contexts, 1):
        try:
            result = ModelManager.predict_dual(
                user_context=context,
                historical_data=[],
                social_context={},
                is_authenticated=False
            )
            
            css_variables = result['css_variables']
            all_predictions.append(css_variables)
            
            print(f"📱 Context {i} CSS Variables:")
            for var_name, var_value in css_variables.items():
                print(f"   {var_name}: {var_value}")
            
        except Exception as e:
            print(f"❌ Error en contexto {i}: {e}")
            return False
    
    # Analizar diversidad
    if len(all_predictions) >= 2:
        diversity_analysis = analyze_prediction_diversity(all_predictions)
        print(f"\n📊 Análisis de Diversidad:")
        print(f"   Diferencias encontradas: {diversity_analysis['differences_found']}")
        print(f"   Variables únicas: {diversity_analysis['unique_values']}")
        
        return diversity_analysis['differences_found'] > 0
    
    return False


def analyze_prediction_diversity(predictions: list) -> dict:
    """Analiza si hay diversidad en las predicciones"""
    if len(predictions) < 2:
        return {'differences_found': 0, 'unique_values': 0}
    
    differences_found = 0
    unique_values = 0
    
    # Comparar todas las variables CSS entre predicciones
    if predictions[0]:  # Si hay al menos una predicción válida
        for var_name in predictions[0].keys():
            values = [pred.get(var_name, '') for pred in predictions]
            unique_vals = set(values)
            
            if len(unique_vals) > 1:
                differences_found += 1
            
            unique_values += len(unique_vals)
    
    return {
        'differences_found': differences_found,
        'unique_values': unique_values
    }


async def main():
    """Ejecuta todos los tests de CSS variable prediction"""
    print("🚀 INICIANDO TESTS DE CSS VARIABLE PREDICTION")
    print("="*80)
    
    tests = [
        ("Target Columns Loading", test_target_columns_loading),
        ("CSS Variable Predictions", test_css_variable_predictions),
        ("CSS Variable Diversity", test_css_variable_diversity)
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
    print("📋 RESUMEN DE TESTS CSS VARIABLE PREDICTION")
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
        print("🎉 ¡Todos los tests de CSS variable prediction pasaron!")
        print("   El sistema de predicción de variables CSS está funcionando correctamente.")
    else:
        print("⚠️  Algunos tests fallaron. Revisar logs para detalles.")
    
    return passed == len(tests)


if __name__ == "__main__":
    asyncio.run(main())
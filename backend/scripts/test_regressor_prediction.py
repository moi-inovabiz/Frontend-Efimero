"""
Script de prueba para verificar el XGBoost Regressor entrenado
"""

import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.train_xgboost_regressor import XGBoostRegressorTrainer

def test_regressor():
    """
    Prueba el modelo XGBoost Regressor entrenado con datos de muestra.
    """
    print("🧪 Probando XGBoost Regressor entrenado...")
    
    # Configuración
    models_dir = "../models"
    
    # Crear trainer y cargar modelo
    trainer = XGBoostRegressorTrainer("dummy_path", models_dir)
    
    try:
        # Cargar modelo entrenado
        trainer.load_model()
        print("✅ Modelo cargado exitosamente")
        
        # Datos de prueba simulando diferentes contextos de usuario
        test_cases = [
            {
                "name": "Usuario móvil nocturno",
                "features": np.array([
                    [0.5, 0.866, 0.0, 1.0,  # Temporal: ~8 PM, domingo
                     390, 844, 0.46, 0.16,  # Móvil pequeño
                     1.0, 1.5, 1.0,  # Touch, pixel ratio, dark mode
                     85.0, 49, 0.39, 0.003,  # Comportamiento
                     0.87, 1.07, 1.0,  # Preferencias
                     1.0, 1.0, 2.0]  # Locale, accessibility, network
                ])
            },
            {
                "name": "Usuario desktop diurno",
                "features": np.array([
                    [-0.707, -0.707, 0.78, 0.62,  # Temporal: ~3 PM, lunes
                     1920, 1080, 1.78, 1.0,  # Desktop grande
                     0.0, 1.0, 0.0,  # No touch, standard ratio, light mode
                     17.0, 53, 0.43, 0.016,  # Comportamiento
                     1.25, 1.50, 2.0,  # Preferencias
                     0.0, 0.0, 1.0]  # Locale, accessibility, network
                ])
            },
            {
                "name": "Usuario tablet medio",
                "features": np.array([
                    [0.0, 1.0, -0.43, -0.90,  # Temporal: ~12 PM, jueves
                     768, 1024, 0.75, 0.38,  # Tablet
                     1.0, 2.0, 0.5,  # Touch, high DPI, no preference
                     72.5, 50, 0.43, 0.004,  # Comportamiento
                     0.92, 1.08, 1.0,  # Preferencias
                     1.0, 0.0, 2.0]  # Locale, accessibility, network
                ])
            }
        ]
        
        print("\n📱 Predicciones de Variables CSS para diferentes contextos:")
        print("=" * 80)
        
        for test_case in test_cases:
            print(f"\n🔍 {test_case['name']}:")
            
            # Hacer predicción
            css_variables, confidence = trainer.predict(test_case['features'])
            
            # Mostrar resultados
            print(f"  🎯 Confianza (R²): {confidence:.1%}")
            print(f"  📋 Variables CSS predichas:")
            
            for var_name, var_value in css_variables.items():
                print(f"    {var_name}: {var_value}")
            
            # Análisis de las predicciones
            print(f"  📝 Análisis:")
            font_size = float(css_variables['--font-size-base'].replace('rem', ''))
            spacing = float(css_variables['--spacing-factor'])
            hue = float(css_variables['--color-primary-hue'])
            
            if font_size > 1.1:
                print(f"    └─ Fuente grande ({font_size:.2f}rem) - bueno para legibilidad")
            elif font_size < 0.9:
                print(f"    └─ Fuente pequeña ({font_size:.2f}rem) - conserva espacio")
            else:
                print(f"    └─ Fuente estándar ({font_size:.2f}rem) - equilibrado")
            
            if spacing > 1.2:
                print(f"    └─ Espaciado amplio ({spacing:.2f}) - interfaz relajada")
            elif spacing < 0.8:
                print(f"    └─ Espaciado compacto ({spacing:.2f}) - información densa")
            else:
                print(f"    └─ Espaciado normal ({spacing:.2f}) - estándar")
            
            # Color hue analysis
            if 0 <= hue < 60:
                color_name = "Rojo-Naranja"
            elif 60 <= hue < 120:
                color_name = "Amarillo-Verde"
            elif 120 <= hue < 180:
                color_name = "Verde-Cian"
            elif 180 <= hue < 240:
                color_name = "Cian-Azul"
            elif 240 <= hue < 300:
                color_name = "Azul-Magenta"
            else:
                color_name = "Magenta-Rojo"
            
            print(f"    └─ Color primario: {color_name} ({hue:.0f}°)")
        
        # Mostrar estadísticas del modelo
        print(f"\n📊 Estadísticas del modelo:")
        print(f"  🏆 RMSE: {trainer.training_results['test_rmse']:.4f}")
        print(f"  📈 R²: {trainer.training_results['test_r2_score']:.4f}")
        print(f"  🔄 RMSE CV: {trainer.training_results['cv_rmse_mean']:.4f} ± {trainer.training_results['cv_rmse_std']:.4f}")
        print(f"  📝 Variables: {trainer.training_results['n_targets']}")
        
        # Feature importance
        print(f"\n🔍 Top 5 Features más importantes:")
        importance = trainer.get_feature_importance()
        for i, (feature, imp) in enumerate(list(importance.items())[:5]):
            print(f"  {i+1}. {feature}: {imp:.4f}")
        
        # Rendimiento por variable
        print(f"\n📊 Rendimiento por Variable CSS:")
        for target, metrics in trainer.training_results['target_metrics'].items():
            r2 = metrics['r2_score']
            rmse = metrics['rmse']
            
            if r2 > 0.6:
                performance = "Excelente"
            elif r2 > 0.4:
                performance = "Bueno"
            elif r2 > 0.2:
                performance = "Regular"
            else:
                performance = "Necesita mejora"
            
            print(f"  {target}: R²={r2:.3f}, RMSE={rmse:.3f} ({performance})")
        
        print(f"\n✅ Prueba completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_regressor()
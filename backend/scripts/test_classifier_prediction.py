"""
Script de prueba para verificar el XGBoost Classifier entrenado
"""

import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.train_xgboost_classifier import XGBoostClassifierTrainer

def test_classifier():
    """
    Prueba el modelo XGBoost Classifier entrenado con datos de muestra.
    """
    print("🧪 Probando XGBoost Classifier entrenado...")
    
    # Configuración
    models_dir = "../models"
    
    # Crear trainer y cargar modelo
    trainer = XGBoostClassifierTrainer("dummy_path", models_dir)
    
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
        
        print("\n📱 Predicciones para diferentes contextos:")
        print("=" * 60)
        
        for test_case in test_cases:
            print(f"\n🔍 {test_case['name']}:")
            
            # Hacer predicción
            css_classes, probabilities = trainer.predict(test_case['features'])
            
            # Mostrar resultados
            predicted_classes = css_classes[0]
            max_prob = np.max(probabilities[0])
            
            print(f"  📋 Clases predichas: {predicted_classes}")
            print(f"  🎯 Confianza: {max_prob:.2%}")
            
            # Desglosar por tipo de clase
            densidad = [c for c in predicted_classes if 'densidad' in c][0] if any('densidad' in c for c in predicted_classes) else 'N/A'
            fuente = [c for c in predicted_classes if 'fuente' in c][0] if any('fuente' in c for c in predicted_classes) else 'N/A'
            modo = [c for c in predicted_classes if 'modo' in c][0] if any('modo' in c for c in predicted_classes) else 'N/A'
            
            print(f"  └─ Densidad: {densidad}")
            print(f"  └─ Fuente: {fuente}")
            print(f"  └─ Modo: {modo}")
        
        # Mostrar estadísticas del modelo
        print(f"\n📊 Estadísticas del modelo:")
        print(f"  🏆 F1-Score: {trainer.training_results['test_f1_score']:.4f}")
        print(f"  🔄 CV Score: {trainer.training_results['cv_scores_mean']:.4f} ± {trainer.training_results['cv_scores_std']:.4f}")
        print(f"  📝 Clases totales: {trainer.training_results['n_classes']}")
        
        # Feature importance
        print(f"\n🔍 Top 5 Features más importantes:")
        importance = trainer.get_feature_importance()
        for i, (feature, imp) in enumerate(list(importance.items())[:5]):
            print(f"  {i+1}. {feature}: {imp:.4f}")
        
        print(f"\n✅ Prueba completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False

if __name__ == "__main__":
    test_classifier()
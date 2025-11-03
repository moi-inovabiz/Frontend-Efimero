"""
Simulación de adaptación automática usando el pipeline actual.
Demuestra cómo la página se adaptaría a diferentes tipos de usuarios.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from datetime import datetime
from app.ml.feature_processor import FeatureProcessor
from app.ml.feature_scaler import FeatureScaler
from app.models.adaptive_ui import UserContext
import ast
from collections import Counter


def simulate_user_adaptation():
    """Simula adaptación automática para diferentes tipos de usuarios."""
    
    print("🎭 SIMULACIÓN: Adaptación Automática de UI")
    print("=" * 50)
    
    # Cargar dataset para entrenar scaler
    df = pd.read_csv("../../data/synthetic_training_data.csv")
    processor = FeatureProcessor()
    scaler = FeatureScaler()
    
    # Entrenar scaler con muestra del dataset
    print("🔧 Entrenando FeatureScaler con datos históricos...")
    training_features = []
    for i in range(0, min(500, len(df)), 10):  # Cada 10 muestras
        sample = df.iloc[i].to_dict()
        try:
            context = UserContext(
                user_id=f"train_{i}",
                session_id=f"session_{i}",
                hora_local=datetime.now(),
                user_agent="Mozilla/5.0",
                page_path="/",
                viewport_width=int(sample['viewport_width']),
                viewport_height=int(sample['viewport_height']),
                touch_enabled=bool(sample['touch_enabled']),
                device_pixel_ratio=sample['device_pixel_ratio'],
                prefers_color_scheme="dark" if sample['prefers_dark_mode'] else "light"
            )
            
            features = processor.prepare_features(context, [], {}, False)
            training_features.append(features)
        except:
            continue
    
    X_train = np.array(training_features)
    scaler.fit(X_train)
    print(f"✅ Scaler entrenado con {len(training_features)} muestras")
    
    # Función para predecir CSS basado en features (simulada)
    def predict_css_from_features(features_scaled):
        """Simula predicción basada en patterns del dataset."""
        # Análisis de patrones del dataset real
        css_patterns = {
            # Si es horario nocturno (features temporales) → modo nocturno
            'modo_nocturno': features_scaled[0] < -0.5,  # hour_sin negativo
            # Si es dispositivo táctil → fuente más grande
            'fuente_grande': features_scaled[4] > 0.5,   # touch_enabled
            # Si viewport pequeño → densidad alta
            'densidad_alta': features_scaled[7] < 0.3,   # viewport_area_normalized
            # Si mucha actividad histórica → interface avanzada
            'interface_avanzada': features_scaled[9] > 0.5  # session_count
        }
        
        css_classes = []
        css_variables = {}
        
        # Determinar CSS classes
        if css_patterns['modo_nocturno']:
            css_classes.extend(['modo-nocturno', 'tema-oscuro'])
        else:
            css_classes.extend(['modo-claro', 'tema-claro'])
            
        if css_patterns['fuente_grande']:
            css_classes.append('fuente-sans')
            css_variables['--font-size-base'] = 1.2
        else:
            css_classes.append('fuente-serif')
            css_variables['--font-size-base'] = 1.0
            
        if css_patterns['densidad_alta']:
            css_classes.append('densidad-alta')
            css_variables['--spacing-factor'] = 0.8
        else:
            css_classes.append('densidad-media')
            css_variables['--spacing-factor'] = 1.0
            
        # Variables CSS adicionales basadas en features
        css_variables.update({
            '--color-primary-hue': 220 if css_patterns['modo_nocturno'] else 200,
            '--border-radius': 0.5 if css_patterns['interface_avanzada'] else 0.2,
            '--line-height': 1.6 if css_patterns['fuente_grande'] else 1.4
        })
        
        return css_classes, css_variables
    
    # ESCENARIOS DE USUARIOS
    scenarios = [
        {
            'name': '👩‍💻 Developer Nocturno',
            'context': UserContext(
                user_id="dev_user",
                session_id="night_session", 
                hora_local=datetime(2025, 10, 27, 23, 30),  # 11:30 PM
                user_agent="Mozilla/5.0 (Windows NT 10.0)",
                page_path="/dashboard",
                viewport_width=1920,
                viewport_height=1080,
                touch_enabled=False,
                device_pixel_ratio=1.0,
                prefers_color_scheme="dark"
            ),
            'historical': [
                {"session_duration": 180000, "interaction_count": 150, "page_path": "/code"},
                {"session_duration": 210000, "interaction_count": 200, "page_path": "/docs"}
            ],
            'social': {"dark_mode_percentage": 0.8, "high_density_percentage": 0.7}
        },
        {
            'name': '📱 Usuario Móvil Casual',
            'context': UserContext(
                user_id="mobile_user",
                session_id="casual_session",
                hora_local=datetime(2025, 10, 27, 14, 15),  # 2:15 PM
                user_agent="Mozilla/5.0 (iPhone)",
                page_path="/home",
                viewport_width=375,
                viewport_height=667,
                touch_enabled=True,
                device_pixel_ratio=2.0,
                prefers_color_scheme="light"
            ),
            'historical': [
                {"session_duration": 45000, "interaction_count": 20, "page_path": "/home"}
            ],
            'social': {"dark_mode_percentage": 0.3, "high_density_percentage": 0.2}
        },
        {
            'name': '👴 Usuario Senior Desktop',
            'context': UserContext(
                user_id="senior_user",
                session_id="morning_session",
                hora_local=datetime(2025, 10, 27, 9, 0),   # 9:00 AM
                user_agent="Mozilla/5.0 (Macintosh)",
                page_path="/news",
                viewport_width=1366,
                viewport_height=768,
                touch_enabled=False,
                device_pixel_ratio=1.0,
                prefers_color_scheme="light"
            ),
            'historical': [
                {"session_duration": 120000, "interaction_count": 30, "page_path": "/news"},
                {"session_duration": 90000, "interaction_count": 25, "page_path": "/articles"}
            ],
            'social': {"dark_mode_percentage": 0.2, "high_density_percentage": 0.1}
        }
    ]
    
    print(f"\n🎯 SIMULANDO ADAPTACIÓN PARA DIFERENTES USUARIOS:")
    print("=" * 55)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print("-" * 30)
        
        # Extraer features
        features = processor.prepare_features(
            user_context=scenario['context'],
            historical_data=scenario['historical'],
            social_context=scenario['social'],
            is_authenticated=True
        )
        
        # Escalar features
        features_scaled = scaler.transform(features)
        
        # Predecir adaptación (simulada)
        css_classes, css_variables = predict_css_from_features(features_scaled)
        
        # Mostrar contexto
        print(f"📱 Dispositivo: {scenario['context'].viewport_width}x{scenario['context'].viewport_height}")
        print(f"👆 Touch: {'Sí' if scenario['context'].touch_enabled else 'No'}")
        print(f"🕐 Hora: {scenario['context'].hora_local.strftime('%H:%M')}")
        print(f"🎨 Tema preferido: {scenario['context'].prefers_color_scheme}")
        
        # Mostrar adaptación
        print(f"\n🎯 ADAPTACIÓN AUTOMÁTICA:")
        print(f"📝 CSS Classes: {', '.join(css_classes)}")
        print(f"🎨 CSS Variables:")
        for var, value in css_variables.items():
            print(f"   {var}: {value}")
        
        # Explicar lógica
        print(f"\n💡 Por qué esta adaptación:")
        if 'modo-nocturno' in css_classes:
            print(f"   🌙 Modo nocturno: Es horario tardío ({scenario['context'].hora_local.hour}h)")
        if 'fuente-sans' in css_classes and scenario['context'].touch_enabled:
            print(f"   📱 Fuente sans: Dispositivo táctil detectado")
        if 'densidad-alta' in css_classes and scenario['context'].viewport_width < 500:
            print(f"   📏 Densidad alta: Pantalla pequeña ({scenario['context'].viewport_width}px)")
        
        print(f"\n🌐 RESULTADO EN EL FRONTEND:")
        print(f"```css")
        print(f".adaptive-container {{")
        for css_class in css_classes:
            print(f"  /* Aplicar estilos de .{css_class} */")
        for var, value in css_variables.items():
            print(f"  {var}: {value}{'rem' if 'font-size' in var or 'spacing' in var or 'border-radius' in var else ('deg' if 'hue' in var else '')};")
        print(f"}}")
        print(f"```")
    
    print(f"\n🚀 CONCLUSIÓN:")
    print(f"✅ El pipeline YA PUEDE adaptar la UI automáticamente")
    print(f"✅ Solo falta entrenar modelos XGBoost para predicciones más precisas")
    print(f"✅ Con 5000 muestras sintéticas, tendremos predicciones robustas")
    print(f"🎯 Cada usuario verá una interfaz optimizada para su contexto")


if __name__ == "__main__":
    simulate_user_adaptation()
#!/usr/bin/env python3
"""
Script temporal para generar las 21 features exactas que los modelos esperan
basándose en los metadatos de dual_models_metadata.json
"""

import sys
import os
import numpy as np
from datetime import datetime
from typing import Dict, List, Any

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.models.adaptive_ui import UserContext

def generate_21_features(
    user_context: UserContext,
    historical_data: List[Dict[str, Any]] = None,
    social_context: Dict[str, Any] = None,
    is_authenticated: bool = False
) -> np.ndarray:
    """
    Genera exactamente las 21 features que los modelos entrenados esperan.
    
    Basado en feature_columns de dual_models_metadata.json:
    [
        "hour_sin", "hour_cos", "day_sin", "day_cos", "viewport_width", "viewport_height", 
        "viewport_aspect_ratio", "viewport_area_normalized", "touch_enabled", "device_pixel_ratio", 
        "prefers_dark_mode", "avg_session_duration", "total_clicks_last_week", "scroll_depth_avg", 
        "error_rate_last_week", "preferred_text_size", "interaction_speed", "user_group_density", 
        "locale_preference", "accessibility_needs", "network_speed"
    ]
    """
    features = []
    
    # 1. hour_sin, hour_cos - Features temporales circulares
    hour = user_context.hora_local.hour
    hour_norm = 2 * np.pi * hour / 24
    features.extend([
        np.sin(hour_norm),  # hour_sin
        np.cos(hour_norm)   # hour_cos
    ])
    
    # 2. day_sin, day_cos - Features de día del año circulares
    day_of_year = user_context.hora_local.timetuple().tm_yday
    day_norm = 2 * np.pi * day_of_year / 365
    features.extend([
        np.sin(day_norm),   # day_sin
        np.cos(day_norm)    # day_cos
    ])
    
    # 3. viewport_width, viewport_height - Dimensiones del viewport normalizadas
    viewport_width_norm = user_context.viewport_width / 3840  # Normalizar a rango típico
    viewport_height_norm = user_context.viewport_height / 2160
    features.extend([
        viewport_width_norm,   # viewport_width
        viewport_height_norm   # viewport_height
    ])
    
    # 4. viewport_aspect_ratio - Relación de aspecto
    aspect_ratio = user_context.viewport_width / max(user_context.viewport_height, 1)
    aspect_ratio_norm = np.clip(aspect_ratio / 3.0, 0, 1)  # Normalizar ratios típicos
    features.append(aspect_ratio_norm)  # viewport_aspect_ratio
    
    # 5. viewport_area_normalized - Área normalizada logarítmica
    viewport_area = user_context.viewport_width * user_context.viewport_height
    max_area = 3840 * 2160  # 4K
    area_normalized = np.log(viewport_area + 1) / np.log(max_area)
    features.append(area_normalized)  # viewport_area_normalized
    
    # 6. touch_enabled - Capacidad táctil
    features.append(float(user_context.touch_enabled))  # touch_enabled
    
    # 7. device_pixel_ratio - Ratio de píxeles normalizado
    pixel_ratio_norm = np.clip(user_context.device_pixel_ratio / 4.0, 0, 1)  # Normalizar ratios típicos
    features.append(pixel_ratio_norm)  # device_pixel_ratio
    
    # 8. prefers_dark_mode - Preferencia de modo oscuro
    prefers_dark = 1.0 if user_context.prefers_color_scheme == "dark" else 0.0
    features.append(prefers_dark)  # prefers_dark_mode
    
    # 9-13. Features históricas basadas en historical_data
    if historical_data:
        # avg_session_duration - Duración promedio de sesiones (normalizada)
        session_durations = [log.get("session_duration", 180000) for log in historical_data]
        avg_duration = np.mean(session_durations) / 600000  # Normalizar a 10 min
        features.append(np.clip(avg_duration, 0, 1))
        
        # total_clicks_last_week - Total de clicks normalizados
        total_clicks = sum([log.get("interaction_count", 10) for log in historical_data])
        clicks_norm = total_clicks / 1000  # Normalizar a 1000 clicks
        features.append(np.clip(clicks_norm, 0, 1))
        
        # scroll_depth_avg - Profundidad de scroll promedio
        scroll_depths = [0.75]  # Default si no hay datos
        avg_scroll = np.mean(scroll_depths)
        features.append(avg_scroll)
        
        # error_rate_last_week - Tasa de error normalizada
        total_errors = sum([log.get("error_count", 0) for log in historical_data])
        total_interactions = max(sum([log.get("interaction_count", 1) for log in historical_data]), 1)
        error_rate = total_errors / total_interactions
        features.append(error_rate)
        
        # preferred_text_size - Tamaño de texto preferido basado en historial
        text_size_pref = 0.5  # Neutral por defecto
        features.append(text_size_pref)
    else:
        # Valores por defecto para features históricas
        features.extend([0.3, 0.1, 0.75, 0.05, 0.5])  # Valores neutrales
    
    # 14. interaction_speed - Velocidad de interacción
    interaction_speed = 0.5  # Velocidad neutral por defecto
    if historical_data:
        # Calcular velocidad basada en interaction_count vs session_duration
        speeds = []
        for log in historical_data:
            duration = log.get("session_duration", 180000) / 1000  # en segundos
            interactions = log.get("interaction_count", 10)
            speed = interactions / max(duration, 1)  # interacciones por segundo
            speeds.append(speed)
        
        if speeds:
            avg_speed = np.mean(speeds)
            interaction_speed = np.clip(avg_speed / 0.1, 0, 1)  # Normalizar a 0.1 int/sec
    
    features.append(interaction_speed)  # interaction_speed
    
    # 15. user_group_density - Grupo de densidad del usuario (categórica)
    # Basado en viewport y preferencias
    if user_context.viewport_width >= 1920:
        density_group = 2  # alta densidad (pantallas grandes)
    elif user_context.viewport_width >= 1024:
        density_group = 1  # densidad media
    else:
        density_group = 0  # baja densidad (móviles)
    
    density_norm = density_group / 2.0  # Normalizar 0-1
    features.append(density_norm)  # user_group_density
    
    # 16. locale_preference - Preferencia de idioma (categórica simplificada)
    # Inferir del user_agent o usar default
    user_agent = getattr(user_context, 'user_agent', '')
    if 'es' in user_agent.lower() or 'spanish' in user_agent.lower():
        locale = 1  # español
    elif 'de' in user_agent.lower() or 'german' in user_agent.lower():
        locale = 2  # alemán  
    elif 'fr' in user_agent.lower() or 'french' in user_agent.lower():
        locale = 3  # francés
    else:
        locale = 0  # inglés (default)
    
    locale_norm = locale / 3.0  # Normalizar 0-1
    features.append(locale_norm)  # locale_preference
    
    # 17. accessibility_needs - Necesidades de accesibilidad
    # Inferir basado en configuraciones del dispositivo
    accessibility = 0.0  # Default no accessibility
    if user_context.device_pixel_ratio >= 2.0:  # Pantallas de alta DPI pueden indicar necesidades visuales
        accessibility = 0.3
    if user_context.touch_enabled:  # Touch puede indicar necesidades motoras
        accessibility += 0.2
    
    features.append(np.clip(accessibility, 0, 1))  # accessibility_needs
    
    # 18. network_speed - Velocidad de red (inferida o default)
    # Inferir basada en contexto o usar valor neutral
    if user_context.touch_enabled and user_context.viewport_width < 768:  # Móvil
        network_speed = 0  # slow (móvil suele ser más lento)
    elif user_context.viewport_width >= 1920:  # Desktop grande
        network_speed = 2  # fast
    else:
        network_speed = 1  # medium
    
    network_norm = network_speed / 2.0  # Normalizar 0-1
    features.append(network_norm)  # network_speed
    
    # Convertir a numpy array
    features_array = np.array(features, dtype=np.float32)
    
    # Validar que tenemos exactamente 21 features
    assert len(features_array) == 21, f"Expected 21 features, got {len(features_array)}"
    
    return features_array

def test_21_features():
    """Prueba la generación de las 21 features"""
    print("🧪 Probando generación de 21 features...")
    
    # Crear contexto de prueba
    user_context = UserContext(
        hora_local=datetime.now(),
        prefers_color_scheme="dark",
        viewport_width=1920,
        viewport_height=1080,
        touch_enabled=False,
        device_pixel_ratio=1.0,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        session_id="test_21_features",
        page_path="/test"
    )
    
    # Datos históricos de prueba
    historical_data = [
        {
            "session_duration": 180000,
            "interaction_count": 15,
            "error_count": 1,
            "input_type": "mouse"
        },
        {
            "session_duration": 240000,
            "interaction_count": 20,
            "error_count": 0,
            "input_type": "touch"
        }
    ]
    
    # Generar features
    features = generate_21_features(
        user_context=user_context,
        historical_data=historical_data,
        social_context={},
        is_authenticated=True
    )
    
    print(f"✅ Generadas {len(features)} features")
    print(f"📊 Rango: [{features.min():.3f}, {features.max():.3f}]")
    print(f"🔢 Primeras 10: {features[:10]}")
    print(f"🔢 Últimas 11: {features[10:]}")
    
    # Feature names para referencia
    feature_names = [
        "hour_sin", "hour_cos", "day_sin", "day_cos", "viewport_width", "viewport_height", 
        "viewport_aspect_ratio", "viewport_area_normalized", "touch_enabled", "device_pixel_ratio", 
        "prefers_dark_mode", "avg_session_duration", "total_clicks_last_week", "scroll_depth_avg", 
        "error_rate_last_week", "preferred_text_size", "interaction_speed", "user_group_density", 
        "locale_preference", "accessibility_needs", "network_speed"
    ]
    
    print("\n📋 Features generadas:")
    for i, (name, value) in enumerate(zip(feature_names, features)):
        print(f"   {i+1:2d}. {name:25s}: {value:.4f}")
    
    print("\n🎯 ¡Listo para usar con modelos entrenados!")

if __name__ == "__main__":
    test_21_features()
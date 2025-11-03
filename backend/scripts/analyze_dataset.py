"""
Análisis Exploratorio del Dataset Sintético
Revela patrones de comportamiento y distribuciones para validar calidad de datos.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import ast


def analyze_synthetic_dataset():
    """Análisis exploratorio completo del dataset sintético."""
    
    print("📊 ANÁLISIS EXPLORATORIO DEL DATASET SINTÉTICO")
    print("=" * 55)
    
    # Cargar datos
    df = pd.read_csv("../../data/synthetic_training_data.csv")
    print(f"📈 Dataset: {len(df)} muestras, {len(df.columns)} columnas")
    
    # 1. ANÁLISIS TEMPORAL
    print(f"\n🕐 1. ANÁLISIS TEMPORAL")
    print("-" * 25)
    print(f"Distribución por hora:")
    hour_counts = df['hour'].value_counts().sort_index()
    for hour, count in hour_counts.items():
        bar = "█" * int(count / 50)  # Escala visual
        print(f"  {hour:2d}h: {count:3d} {bar}")
    
    print(f"\nDistribución por día de semana:")
    day_names = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    day_counts = df['day_of_week'].value_counts().sort_index()
    for day, count in day_counts.items():
        bar = "█" * int(count / 30)
        print(f"  {day_names[day]}: {count:3d} {bar}")
    
    # 2. ANÁLISIS DE DISPOSITIVOS
    print(f"\n📱 2. ANÁLISIS DE DISPOSITIVOS")
    print("-" * 30)
    
    # Touch vs No-touch
    touch_counts = df['touch_enabled'].value_counts()
    print(f"Touch habilitado: {touch_counts.get(True, 0)} ({touch_counts.get(True, 0)/len(df)*100:.1f}%)")
    print(f"Solo mouse/trackpad: {touch_counts.get(False, 0)} ({touch_counts.get(False, 0)/len(df)*100:.1f}%)")
    
    # Viewport sizes (categorizar)
    def categorize_viewport(row):
        width, height = row['viewport_width'], row['viewport_height']
        if width <= 768:
            return "Mobile"
        elif width <= 1024:
            return "Tablet"
        elif width <= 1920:
            return "Desktop"
        else:
            return "Large Desktop"
    
    df['device_category'] = df.apply(categorize_viewport, axis=1)
    device_counts = df['device_category'].value_counts()
    print(f"\nCategorías de dispositivo:")
    for device, count in device_counts.items():
        print(f"  {device}: {count} ({count/len(df)*100:.1f}%)")
    
    # Device pixel ratio
    pixel_ratio_dist = df['device_pixel_ratio'].value_counts().sort_index()
    print(f"\nDevice Pixel Ratio:")
    for ratio, count in pixel_ratio_dist.items():
        print(f"  {ratio}x: {count}")
    
    # 3. ANÁLISIS DE PREFERENCIAS
    print(f"\n🎨 3. ANÁLISIS DE PREFERENCIAS")
    print("-" * 32)
    
    # Modo oscuro vs claro
    dark_mode_counts = df['prefers_dark_mode'].value_counts()
    print(f"Modo oscuro: {dark_mode_counts.get(True, 0)} ({dark_mode_counts.get(True, 0)/len(df)*100:.1f}%)")
    print(f"Modo claro: {dark_mode_counts.get(False, 0)} ({dark_mode_counts.get(False, 0)/len(df)*100:.1f}%)")
    
    # Densidad de usuario
    density_counts = df['user_group_density'].value_counts()
    print(f"\nDensidad de interfaz:")
    for density, count in density_counts.items():
        print(f"  {density}: {count} ({count/len(df)*100:.1f}%)")
    
    # Idiomas
    locale_counts = df['locale_preference'].value_counts()
    print(f"\nIdiomas preferidos:")
    for locale, count in locale_counts.items():
        print(f"  {locale}: {count} ({count/len(df)*100:.1f}%)")
    
    # 4. ANÁLISIS DE COMPORTAMIENTO
    print(f"\n👆 4. ANÁLISIS DE COMPORTAMIENTO")
    print("-" * 35)
    
    # Estadísticas de sesión
    print(f"Duración promedio de sesión: {df['avg_session_duration'].mean():.1f} minutos")
    print(f"Clicks promedio por semana: {df['total_clicks_last_week'].mean():.1f}")
    print(f"Profundidad de scroll promedio: {df['scroll_depth_avg'].mean():.2f}")
    print(f"Tasa de error promedio: {df['error_rate_last_week'].mean():.3f}")
    
    # Distribución de velocidad de interacción
    speed_stats = df['interaction_speed'].describe()
    print(f"\nVelocidad de interacción:")
    print(f"  Mínima: {speed_stats['min']:.2f}")
    print(f"  Mediana: {speed_stats['50%']:.2f}")
    print(f"  Máxima: {speed_stats['max']:.2f}")
    
    # 5. ANÁLISIS DE CSS CLASSES (TARGETS)
    print(f"\n🎯 5. ANÁLISIS DE TARGETS (CSS)")
    print("-" * 32)
    
    # Parsear CSS classes
    all_css_classes = []
    for css_str in df['css_classes']:
        try:
            classes = ast.literal_eval(css_str)
            all_css_classes.extend(classes)
        except:
            continue
    
    css_counter = Counter(all_css_classes)
    print(f"CSS Classes más frecuentes:")
    for css_class, count in css_counter.most_common(10):
        print(f"  {css_class}: {count} ({count/len(df)*100:.1f}%)")
    
    # 6. ANÁLISIS DE CSS VARIABLES (TARGETS)
    print(f"\nCSS Variables (distribución):")
    css_vars = ['--font-size-base', '--spacing-factor', '--color-primary-hue', '--border-radius', '--line-height']
    for var in css_vars:
        stats = df[var].describe()
        print(f"  {var}:")
        print(f"    Range: [{stats['min']:.3f}, {stats['max']:.3f}]")
        print(f"    Mean: {stats['mean']:.3f} ± {stats['std']:.3f}")
    
    # 7. CORRELACIONES INTERESANTES
    print(f"\n🔗 6. CORRELACIONES INTERESANTES")
    print("-" * 36)
    
    # Correlación touch vs hora
    touch_by_hour = df.groupby('hour')['touch_enabled'].mean()
    peak_touch_hour = touch_by_hour.idxmax()
    print(f"Hora con más uso táctil: {peak_touch_hour}h ({touch_by_hour[peak_touch_hour]:.1%})")
    
    # Correlación modo oscuro vs hora
    dark_by_hour = df.groupby('hour')['prefers_dark_mode'].mean()
    peak_dark_hour = dark_by_hour.idxmax()
    print(f"Hora con más modo oscuro: {peak_dark_hour}h ({dark_by_hour[peak_dark_hour]:.1%})")
    
    # Correlación dispositivo vs densidad
    density_by_device = df.groupby('device_category')['user_group_density'].apply(lambda x: (x == 'high').mean())
    print(f"\nPorcentaje de alta densidad por dispositivo:")
    for device, pct in density_by_device.items():
        print(f"  {device}: {pct:.1%}")
    
    # 8. CALIDAD DEL DATASET
    print(f"\n✅ 7. CALIDAD DEL DATASET")
    print("-" * 28)
    
    # Valores faltantes
    missing_values = df.isnull().sum()
    if missing_values.sum() == 0:
        print("✅ Sin valores faltantes")
    else:
        print(f"⚠️ Valores faltantes encontrados:")
        for col, missing in missing_values[missing_values > 0].items():
            print(f"  {col}: {missing}")
    
    # Valores duplicados
    duplicates = df.duplicated().sum()
    print(f"✅ Filas duplicadas: {duplicates}")
    
    # Distribuciones válidas
    print("✅ Validaciones:")
    print(f"  Horas válidas (0-23): {(df['hour'] >= 0).all() and (df['hour'] <= 23).all()}")
    print(f"  Días válidos (0-6): {(df['day_of_week'] >= 0).all() and (df['day_of_week'] <= 6).all()}")
    print(f"  Viewports positivos: {(df['viewport_width'] > 0).all() and (df['viewport_height'] > 0).all()}")
    print(f"  Pixel ratio válido: {(df['device_pixel_ratio'] > 0).all()}")
    
    print(f"\n🎉 ANÁLISIS COMPLETADO")
    print(f"📊 Dataset listo para entrenamiento de modelos ML")
    
    return df


if __name__ == "__main__":
    df = analyze_synthetic_dataset()
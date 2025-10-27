"""
Generador de datos sintéticos para entrenamiento de modelos XGBoost
Frontend Efímero - Sistema de Adaptación Predictiva Profunda de UI

Genera datos de comportamiento de usuario realistas para entrenar:
- XGBoost Classifier (CSS classes)
- XGBoost Regressor (CSS variables)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Tuple
import random


class SyntheticDataGenerator:
    """Generador de datos sintéticos para Frontend Efímero"""
    
    def __init__(self, num_samples: int = 5000):
        self.num_samples = num_samples
        self.css_classes = [
            "densidad-baja", "densidad-media", "densidad-alta",
            "fuente-sans", "fuente-serif", "fuente-mono",
            "modo-claro", "modo-nocturno", "modo-auto"
        ]
        
        # Rangos para variables CSS (valores típicos)
        self.css_variable_ranges = {
            "--font-size-base": (0.75, 1.5),      # rem
            "--spacing-factor": (0.5, 2.0),       # multiplicador
            "--color-primary-hue": (0, 360),      # grados
            "--border-radius": (0.0, 1.0),        # rem
            "--line-height": (1.2, 1.8),          # ratio
        }
        
    def generate_temporal_features(self) -> pd.DataFrame:
        """Genera features temporales realistas"""
        data = []
        
        for _ in range(self.num_samples):
            # Hora aleatoria pero con patrones realistas
            hour = np.random.choice(range(24), p=self._get_hour_probabilities())
            day_of_week = np.random.randint(0, 7)
            
            # Encoding seno/coseno para ciclicidad
            hour_sin = np.sin(2 * np.pi * hour / 24)
            hour_cos = np.cos(2 * np.pi * hour / 24)
            day_sin = np.sin(2 * np.pi * day_of_week / 7)
            day_cos = np.cos(2 * np.pi * day_of_week / 7)
            
            data.append({
                'hour': hour,
                'day_of_week': day_of_week,
                'hour_sin': hour_sin,
                'hour_cos': hour_cos,
                'day_sin': day_sin,
                'day_cos': day_cos,
            })
            
        return pd.DataFrame(data)
    
    def generate_device_features(self) -> pd.DataFrame:
        """Genera features de dispositivo realistas"""
        data = []
        
        # Distribuciones realistas de dispositivos
        viewports = [
            (1920, 1080), (1366, 768), (1536, 864), (1440, 900),  # Desktop
            (390, 844), (393, 851), (414, 896), (375, 667),       # Mobile
            (768, 1024), (834, 1194), (1024, 768)                 # Tablet
        ]
        
        for _ in range(self.num_samples):
            viewport = random.choice(viewports)
            
            # Determinar si es móvil basado en viewport
            is_mobile = viewport[0] < 600
            
            data.append({
                'viewport_width': viewport[0],
                'viewport_height': viewport[1],
                'viewport_aspect_ratio': viewport[0] / viewport[1],
                'viewport_area_normalized': min((viewport[0] * viewport[1]) / 2073600, 1.0),
                'touch_enabled': is_mobile or random.random() < 0.1,  # Móviles + algunos laptops táctiles
                'device_pixel_ratio': np.random.choice([1.0, 1.5, 2.0, 3.0], 
                                                     p=[0.3, 0.2, 0.4, 0.1]),
                'prefers_dark_mode': random.random() < 0.4,  # 40% prefiere modo oscuro
            })
            
        return pd.DataFrame(data)
    
    def generate_behavioral_features(self) -> pd.DataFrame:
        """Genera features de comportamiento histórico"""
        data = []
        
        for _ in range(self.num_samples):
            # Patrones de uso que influyen en preferencias de UI
            data.append({
                'avg_session_duration': np.random.lognormal(4, 1),  # minutos
                'total_clicks_last_week': np.random.poisson(50),
                'scroll_depth_avg': np.random.beta(2, 2),  # 0-1
                'error_rate_last_week': np.random.exponential(0.02),  # tasa de error
                'preferred_text_size': np.random.normal(1.0, 0.2),  # factor
                'interaction_speed': np.random.gamma(2, 0.5),  # clicks por minuto
            })
            
        return pd.DataFrame(data)
    
    def generate_social_context(self) -> pd.DataFrame:
        """Genera features de contexto social/ambiental"""
        data = []
        
        for _ in range(self.num_samples):
            data.append({
                'user_group_density': np.random.choice(['low', 'medium', 'high'], 
                                                     p=[0.3, 0.4, 0.3]),
                'locale_preference': np.random.choice(['es', 'en', 'fr', 'de'], 
                                                    p=[0.4, 0.4, 0.1, 0.1]),
                'accessibility_needs': random.random() < 0.15,  # 15% necesidades especiales
                'network_speed': np.random.choice(['slow', 'medium', 'fast'], 
                                                p=[0.2, 0.3, 0.5]),
            })
            
        return pd.DataFrame(data)
    
    def generate_target_labels(self, features_df: pd.DataFrame) -> Tuple[List[List[str]], Dict[str, List[float]]]:
        """Genera labels objetivo basadas en las features usando reglas realistas"""
        css_classes_targets = []
        css_variables_targets = {}
        
        # Inicializar listas para variables CSS
        for var_name in self.css_variable_ranges.keys():
            css_variables_targets[var_name] = []
        
        for idx, row in features_df.iterrows():
            # Reglas para CSS classes basadas en contexto
            classes = []
            
            # Densidad basada en viewport y dispositivo
            if row['viewport_width'] < 600:  # Móvil
                classes.append("densidad-alta")
            elif row['viewport_width'] > 1400:  # Desktop grande
                classes.append("densidad-baja")
            else:
                classes.append("densidad-media")
            
            # Fuente basada en tiempo y contexto
            if row['hour'] >= 18 or row['hour'] <= 6:  # Noche
                classes.append("fuente-serif")  # Más legible en condiciones de poca luz
            elif row['touch_enabled']:
                classes.append("fuente-sans")   # Mejor para táctil
            else:
                classes.append(random.choice(["fuente-sans", "fuente-mono"]))
            
            # Modo de color basado en hora y preferencias
            if row['prefers_dark_mode'] or (20 <= row['hour'] or row['hour'] <= 6):
                classes.append("modo-nocturno")
            elif 6 < row['hour'] < 20:
                classes.append("modo-claro")
            else:
                classes.append("modo-auto")
            
            css_classes_targets.append(classes)
            
            # Variables CSS basadas en contexto y preferencias
            # Font size: más grande en móviles y para adultos mayores
            base_font_size = 1.0
            if row['viewport_width'] < 600:
                base_font_size *= 1.1
            if row.get('accessibility_needs', False):
                base_font_size *= 1.2
            
            css_variables_targets['--font-size-base'].append(
                np.clip(base_font_size + np.random.normal(0, 0.1), 0.75, 1.5)
            )
            
            # Spacing: más espacioso en pantallas grandes
            spacing_factor = 1.0
            if row['viewport_width'] > 1400:
                spacing_factor *= 1.3
            elif row['viewport_width'] < 600:
                spacing_factor *= 0.8
                
            css_variables_targets['--spacing-factor'].append(
                np.clip(spacing_factor + np.random.normal(0, 0.15), 0.5, 2.0)
            )
            
            # Color hue: basado en hora del día
            hour_hue = (row['hour'] * 15) % 360  # Cada hora = 15 grados
            css_variables_targets['--color-primary-hue'].append(
                (hour_hue + np.random.normal(0, 30)) % 360
            )
            
            # Border radius: más redondeado en móviles
            border_radius = 0.25
            if row['touch_enabled']:
                border_radius *= 1.5
                
            css_variables_targets['--border-radius'].append(
                np.clip(border_radius + np.random.normal(0, 0.1), 0.0, 1.0)
            )
            
            # Line height: mayor para legibilidad en dispositivos pequeños
            line_height = 1.4
            if row['viewport_width'] < 600:
                line_height += 0.2
                
            css_variables_targets['--line-height'].append(
                np.clip(line_height + np.random.normal(0, 0.1), 1.2, 1.8)
            )
        
        return css_classes_targets, css_variables_targets
    
    def _get_hour_probabilities(self) -> List[float]:
        """Distribución realista de horas de uso (más actividad en horas de trabajo)"""
        probs = [0.01] * 24  # Base mínima
        
        # Horas de trabajo (9-17): mayor probabilidad
        for hour in range(9, 18):
            probs[hour] = 0.06
            
        # Noche (19-23): actividad moderada
        for hour in range(19, 24):
            probs[hour] = 0.04
            
        # Normalizar
        total = sum(probs)
        return [p / total for p in probs]
    
    def generate_complete_dataset(self) -> pd.DataFrame:
        """Genera el dataset completo con features y targets"""
        print(f"🏗️ Generando {self.num_samples} muestras sintéticas...")
        
        # Generar todas las features
        temporal_df = self.generate_temporal_features()
        device_df = self.generate_device_features()
        behavioral_df = self.generate_behavioral_features()
        social_df = self.generate_social_context()
        
        # Combinar features
        features_df = pd.concat([temporal_df, device_df, behavioral_df, social_df], axis=1)
        
        print("🎯 Generando targets basados en reglas realistas...")
        
        # Generar targets
        css_classes_targets, css_variables_targets = self.generate_target_labels(features_df)
        
        # Añadir targets al DataFrame
        features_df['css_classes'] = css_classes_targets
        
        # Añadir variables CSS como columnas separadas
        for var_name, values in css_variables_targets.items():
            features_df[var_name] = values
        
        print(f"✅ Dataset generado: {features_df.shape[0]} muestras, {features_df.shape[1]} columnas")
        
        return features_df
    
    def save_dataset(self, df: pd.DataFrame, output_dir: str = "../data"):
        """Guarda el dataset en archivos CSV y JSON"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Guardar CSV completo
        csv_path = os.path.join(output_dir, "synthetic_training_data.csv")
        df.to_csv(csv_path, index=False)
        print(f"💾 Dataset guardado en: {csv_path}")
        
        # Guardar metadatos
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "num_samples": len(df),
            "features": list(df.columns),
            "css_classes_vocabulary": self.css_classes,
            "css_variables_ranges": self.css_variable_ranges,
            "description": "Synthetic training data for Frontend Efímero XGBoost models"
        }
        
        metadata_path = os.path.join(output_dir, "dataset_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"📋 Metadatos guardados en: {metadata_path}")
        
        return csv_path, metadata_path


def main():
    """Función principal para generar datos sintéticos"""
    print("🚀 Iniciando generación de datos sintéticos para Frontend Efímero")
    
    # Generar dataset
    generator = SyntheticDataGenerator(num_samples=5000)
    dataset = generator.generate_complete_dataset()
    
    # Mostrar estadísticas
    print("\n📊 Estadísticas del dataset:")
    print(f"Forma: {dataset.shape}")
    print(f"Columnas: {list(dataset.columns)}")
    
    # Mostrar distribución de CSS classes
    print("\n🎨 Distribución de CSS classes:")
    css_classes_flat = [cls for sublist in dataset['css_classes'] for cls in sublist]
    from collections import Counter
    class_counts = Counter(css_classes_flat)
    for cls, count in class_counts.most_common():
        print(f"  {cls}: {count}")
    
    # Guardar dataset
    csv_path, metadata_path = generator.save_dataset(dataset)
    
    print(f"\n✅ Generación completada!")
    print(f"📁 Archivos creados:")
    print(f"  - {csv_path}")
    print(f"  - {metadata_path}")


if __name__ == "__main__":
    main()
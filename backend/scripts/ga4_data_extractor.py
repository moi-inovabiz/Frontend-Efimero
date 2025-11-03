"""
GA4 Data Pipeline para entrenar modelos XGBoost con datos reales
Extrae eventos de GA4 y los convierte en dataset de entrenamiento.
"""

import pandas as pd
import numpy as np
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from datetime import datetime, timedelta
import os
import json


class GA4DataExtractor:
    """
    Extrae datos de GA4 para entrenar modelos XGBoost.
    Convierte eventos anónimos en features ML.
    """
    
    def __init__(self, property_id: str, credentials_path: str):
        """
        Inicializar extractor GA4.
        
        Args:
            property_id: ID de propiedad GA4
            credentials_path: Ruta a las credenciales de servicio
        """
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        self.client = BetaAnalyticsDataClient()
        self.property_id = property_id
    
    def extract_adaptive_ui_events(self, days_back: int = 30) -> pd.DataFrame:
        """
        Extrae eventos de adaptive_ui_load de los últimos N días.
        
        Args:
            days_back: Días hacia atrás para extraer datos
            
        Returns:
            DataFrame con eventos procesados para ML
        """
        
        # Configurar fechas
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Configurar request GA4
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )],
            
            # Dimensiones (categorías)
            dimensions=[
                Dimension(name="eventName"),
                Dimension(name="customEvent:user_temp_id"),
                Dimension(name="customEvent:session_id"),
                Dimension(name="customEvent:device_category"),
                Dimension(name="customEvent:viewport_width"),
                Dimension(name="customEvent:viewport_height"),
                Dimension(name="customEvent:touch_enabled"),
                Dimension(name="customEvent:color_scheme_preference"),
                Dimension(name="customEvent:css_classes_applied"),
                Dimension(name="customEvent:css_variables_count"),
                Dimension(name="customEvent:prediction_confidence_classes"),
                Dimension(name="hour"),
                Dimension(name="dayOfWeek"),
                Dimension(name="country"),
                Dimension(name="deviceCategory"),
                Dimension(name="operatingSystem"),
                Dimension(name="browser"),
            ],
            
            # Métricas (valores numéricos)
            metrics=[
                Metric(name="eventCount"),
                Metric(name="engagementRate"),
                Metric(name="averageSessionDuration"),
                Metric(name="screenPageViews"),
            ],
            
            # Filtrar solo eventos de adaptive UI
            dimension_filter=DimensionFilter(
                filter=Filter(
                    field_name="eventName",
                    string_filter=StringFilter(
                        match_type=StringFilter.MatchType.EXACT,
                        value="adaptive_ui_load"
                    )
                )
            )
        )
        
        # Ejecutar query
        response = self.client.run_report(request)
        
        # Procesar respuesta
        data = []
        for row in response.rows:
            # Extraer dimensiones
            dimensions = {
                'event_name': row.dimension_values[0].value,
                'user_temp_id': row.dimension_values[1].value,
                'session_id': row.dimension_values[2].value,
                'device_category': row.dimension_values[3].value,
                'viewport_width': int(row.dimension_values[4].value or 0),
                'viewport_height': int(row.dimension_values[5].value or 0),
                'touch_enabled': row.dimension_values[6].value == 'true',
                'color_scheme_preference': row.dimension_values[7].value,
                'css_classes_applied': row.dimension_values[8].value,
                'css_variables_count': int(row.dimension_values[9].value or 0),
                'prediction_confidence': float(row.dimension_values[10].value or 0),
                'hour': int(row.dimension_values[11].value),
                'day_of_week': int(row.dimension_values[12].value),
                'country': row.dimension_values[13].value,
                'device_category_ga': row.dimension_values[14].value,
                'operating_system': row.dimension_values[15].value,
                'browser': row.dimension_values[16].value,
            }
            
            # Extraer métricas
            metrics = {
                'event_count': int(row.metric_values[0].value),
                'engagement_rate': float(row.metric_values[1].value),
                'avg_session_duration': float(row.metric_values[2].value),
                'page_views': int(row.metric_values[3].value),
            }
            
            # Combinar
            data.append({**dimensions, **metrics})
        
        df = pd.DataFrame(data)
        return self.process_for_ml(df)
    
    def extract_interaction_patterns(self, days_back: int = 30) -> pd.DataFrame:
        """
        Extrae eventos de interaction_pattern para análisis de comportamiento.
        """
        # Similar al anterior pero para eventos 'interaction_pattern'
        # Devuelve datos de comportamiento del usuario
        pass
    
    def process_for_ml(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Procesa datos GA4 para que sean compatibles con FeatureProcessor.
        
        Args:
            df: DataFrame con eventos GA4 crudos
            
        Returns:
            DataFrame procesado para entrenamiento ML
        """
        
        # 1. Limpiar y validar datos
        df = df.dropna(subset=['user_temp_id', 'viewport_width', 'viewport_height'])
        df = df[df['viewport_width'] > 0]
        df = df[df['viewport_height'] > 0]
        
        # 2. Crear features adicionales
        df['viewport_aspect_ratio'] = df['viewport_width'] / df['viewport_height']
        df['viewport_area_normalized'] = (df['viewport_width'] * df['viewport_height']) / 2073600
        df['device_pixel_ratio'] = 1.0  # Default, mejorará con más datos
        
        # 3. Mapear color scheme
        df['prefers_dark_mode'] = df['color_scheme_preference'] == 'dark'
        
        # 4. Procesar CSS classes (target para Classifier)
        df['css_classes'] = df['css_classes_applied'].apply(self.parse_css_classes)
        
        # 5. Generar features temporales
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # 6. Crear variables comportamentales (basadas en GA4)
        df['avg_session_duration'] = df['avg_session_duration'] / 60  # Convertir a minutos
        df['engagement_score'] = df['engagement_rate'] * df['page_views']
        
        # 7. Mapear categorías de dispositivo
        device_map = {'mobile': 'mobile', 'tablet': 'tablet', 'desktop': 'desktop'}
        df['device_type'] = df['device_category_ga'].map(device_map).fillna('desktop')
        
        return df
    
    def parse_css_classes(self, css_string: str) -> list:
        """
        Parsea string de CSS classes desde GA4.
        
        Args:
            css_string: String JSON con clases CSS
            
        Returns:
            Lista de clases CSS
        """
        try:
            if css_string and css_string != '(not set)':
                return json.loads(css_string)
            return []
        except json.JSONDecodeError:
            return []
    
    def create_training_dataset(self, days_back: int = 30) -> pd.DataFrame:
        """
        Crea dataset completo para entrenamiento XGBoost.
        
        Args:
            days_back: Días de datos históricos
            
        Returns:
            DataFrame listo para FeatureProcessor + XGBoost
        """
        
        # Extraer eventos principales
        ui_events = self.extract_adaptive_ui_events(days_back)
        
        if len(ui_events) < 100:
            print(f"⚠️ Solo {len(ui_events)} eventos encontrados. Se recomienda mínimo 100.")
            return ui_events
        
        print(f"✅ Extraídos {len(ui_events)} eventos de GA4")
        print(f"📊 Rango de fechas: {days_back} días")
        print(f"👥 Usuarios únicos: {ui_events['user_temp_id'].nunique()}")
        print(f"🌍 Países: {ui_events['country'].nunique()}")
        
        return ui_events


def main():
    """Ejemplo de uso del extractor GA4."""
    
    # Configuración
    PROPERTY_ID = "123456789"  # Tu GA4 Property ID
    CREDENTIALS_PATH = "path/to/service-account-key.json"
    
    # Extraer datos
    extractor = GA4DataExtractor(PROPERTY_ID, CREDENTIALS_PATH)
    dataset = extractor.create_training_dataset(days_back=30)
    
    # Guardar dataset
    output_path = "../../data/ga4_training_data.csv"
    dataset.to_csv(output_path, index=False)
    print(f"💾 Dataset guardado en {output_path}")
    
    return dataset


if __name__ == "__main__":
    dataset = main()
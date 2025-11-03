/**
 * Google Analytics 4 Configuration for Frontend Efímero
 * Configuración de eventos personalizados para captura de datos ML
 */

// Configuración GA4
export const GA4_CONFIG = {
  measurement_id: process.env.NEXT_PUBLIC_GA4_MEASUREMENT_ID || 'G-XXXXXXXXXX',
  
  // Eventos personalizados para ML
  custom_events: [
    'adaptive_ui_load',      // UI adaptativa aplicada
    'design_token_applied',  // Tokens CSS aplicados
    'interaction_pattern',   // Patrones de interacción
    'viewport_change',       // Cambios de viewport
    'preference_detected',   // Preferencias detectadas
    'model_prediction',      // Predicción ML aplicada
  ],
  
  // Configuración de privacidad
  privacy_config: {
    anonymize_ip: true,
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    cookie_domain: 'auto',
    cookie_expires: 63072000, // 2 años
    cookie_update: true,
  }
};

// Estructura de eventos personalizados
export const CUSTOM_EVENTS = {
  adaptive_ui_load: {
    description: 'UI adaptativa aplicada al usuario',
    parameters: {
      user_temp_id: 'string',           // UUID anónimo
      css_classes_applied: 'array',     // ['modo-claro', 'densidad-media']
      css_variables_applied: 'object',  // {--font-size-base: '1.067rem'}
      prediction_confidence: 'number',  // 0.89
      device_context: 'object',         // {viewport_width: 1366, ...}
      processing_time_ms: 'number',     // Tiempo de procesamiento ML
    }
  },
  
  interaction_pattern: {
    description: 'Patrón de interacción del usuario',
    parameters: {
      user_temp_id: 'string',
      element_type: 'string',           // 'button', 'link', 'form'
      interaction_action: 'string',     // 'click', 'hover', 'focus'
      element_classes: 'string',        // Clases CSS del elemento
      time_on_page: 'number',           // Segundos en la página
      scroll_depth: 'number',           // Profundidad de scroll (0-1)
    }
  },
  
  viewport_change: {
    description: 'Cambio de viewport/dispositivo',
    parameters: {
      user_temp_id: 'string',
      old_viewport_width: 'number',
      old_viewport_height: 'number',
      new_viewport_width: 'number',
      new_viewport_height: 'number',
      device_category_changed: 'boolean',
    }
  },
  
  model_prediction: {
    description: 'Predicción realizada por modelo ML',
    parameters: {
      user_temp_id: 'string',
      feature_count: 'number',
      predicted_classes_count: 'number',
      predicted_variables_count: 'number',
      model_version: 'string',
      prediction_confidence: 'number',
      processing_time_ms: 'number',
    }
  }
};

// Mapeo de parámetros personalizados
export const CUSTOM_PARAMETERS = {
  user_temp_id: 'custom_user_temp_id',
  session_id: 'custom_session_id', 
  device_category: 'custom_device_category',
  ui_density: 'custom_ui_density',
  color_scheme: 'custom_color_scheme',
  viewport_category: 'custom_viewport_category',
  interaction_speed: 'custom_interaction_speed',
  scroll_behavior: 'custom_scroll_behavior',
  prediction_accuracy: 'custom_prediction_accuracy',
};
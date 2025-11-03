/**
 * Google Analytics 4 Enhanced Tracking for Frontend Efímero
 * Recolecta datos anónimos de comportamiento para entrenar modelos XGBoost
 */

// Función simple para generar UUID (evita dependencia externa)
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replaceAll(/[xy]/g, function(c) {
    const r = Math.trunc(Math.random() * 16);
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Configuración GA4
const GA4_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA4_MEASUREMENT_ID || 'G-XXXXXXXXXX';

class AdaptiveUIAnalytics {
  constructor() {
    this.userTempId = this.getUserTempId();
    this.sessionId = this.generateSessionId();
    this.isInitialized = false;
    this.pageStartTime = Date.now();
    this.totalInteractions = 0;
    this.pagesViewed = new Set([globalThis.location?.pathname || '/']);
    this.maxScrollDepth = 0;
    this.viewportChanges = 0;
    this.uiAdaptationsCount = 0;
  }

  /**
   * Inicializar GA4 con configuración personalizada
   */
  async initialize() {
    if (this.isInitialized) return;

    // Cargar gtag
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${GA4_MEASUREMENT_ID}`;
    document.head.appendChild(script);

    // Configurar gtag
    globalThis.dataLayer = globalThis.dataLayer || [];
    globalThis.gtag = function() { globalThis.dataLayer.push(arguments); };
    
    globalThis.gtag('js', new Date());
    globalThis.gtag('config', GA4_MEASUREMENT_ID, {
      // Privacidad mejorada
      anonymize_ip: true,
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      
      // ID anónimo personalizado
      user_id: this.userTempId,
      
      // Parámetros personalizados por defecto
      custom_map: {
        'custom_user_temp_id': 'user_temp_id',
        'custom_session_id': 'session_id',
        'custom_device_category': 'device_category',
        'custom_ui_density': 'ui_density',
        'custom_color_scheme': 'color_scheme'
      }
    });

    this.isInitialized = true;
    console.log('🔍 GA4 Analytics initialized for Frontend Efímero');
  }

  /**
   * Obtener o generar user_temp_id anónimo
   */
  getUserTempId() {
    const COOKIE_NAME = 'frontend_efimero_temp_id';
    const EXPIRY_DAYS = 30;

    // Intentar obtener de cookie existente
    const existingId = this.getCookie(COOKIE_NAME);
    if (existingId) {
      return existingId;
    }

    // Generar nuevo ID anónimo
    const newId = `efimero_${generateUUID()}`;
    this.setCookie(COOKIE_NAME, newId, EXPIRY_DAYS);
    return newId;
  }

  /**
   * Generar session_id único por sesión
   */
  generateSessionId() {
    const sessionKey = 'frontend_efimero_session_id';
    let sessionId = sessionStorage.getItem(sessionKey);
    
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem(sessionKey, sessionId);
    }
    
    return sessionId;
  }

  /**
   * Evento: UI Adaptativa aplicada
   */
  trackAdaptiveUILoad(designTokens, userContext, predictionData) {
    if (!this.isInitialized) return;

    globalThis.gtag('event', 'adaptive_ui_load', {
      // IDs anónimos
      user_temp_id: this.userTempId,
      session_id: this.sessionId,
      
      // Tokens aplicados
      css_classes_applied: JSON.stringify(designTokens.css_classes),
      css_variables_count: Object.keys(designTokens.css_variables).length,
      
      // Contexto del usuario (anónimo)
      device_category: this.categorizeDevice(userContext.viewport_width),
      viewport_width: userContext.viewport_width,
      viewport_height: userContext.viewport_height,
      touch_enabled: userContext.touch_enabled,
      device_pixel_ratio: userContext.device_pixel_ratio,
      color_scheme_preference: userContext.prefers_color_scheme,
      
      // Datos de predicción ML
      prediction_confidence_classes: predictionData?.confidence?.css_classes || 0,
      prediction_confidence_variables: predictionData?.confidence?.css_variables || 0,
      processing_time_ms: predictionData?.processing_time_ms || 0,
      
      // Metadatos
      timestamp: new Date().toISOString(),
      page_url: globalThis.location.href,
      referrer: document.referrer || 'direct'
    });

    console.log('📊 Tracked adaptive_ui_load event');
  }

  /**
   * Evento: Interacción del usuario con elementos adaptativos
   */
  trackInteractionPattern(elementType, action, context) {
    if (!this.isInitialized) return;

    globalThis.gtag('event', 'interaction_pattern', {
      user_temp_id: this.userTempId,
      session_id: this.sessionId,
      
      // Detalles de interacción
      element_type: elementType,  // 'button', 'link', 'form', etc.
      interaction_action: action, // 'click', 'hover', 'focus', etc.
      
      // Contexto del elemento
      element_classes: context.elementClasses,
      element_position: context.position, // 'header', 'sidebar', 'content'
      
      // Timing
      time_on_page: this.getTimeOnPage(),
      scroll_depth: this.getScrollDepth(),
      
      // Estado de UI actual
      current_ui_density: context.currentDensity,
      current_color_scheme: context.currentColorScheme,
      
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Evento: Cambio de viewport/responsive
   */
  trackViewportChange(oldViewport, newViewport) {
    if (!this.isInitialized) return;

    globalThis.gtag('event', 'viewport_change', {
      user_temp_id: this.userTempId,
      session_id: this.sessionId,
      
      // Cambio de viewport
      old_viewport_width: oldViewport.width,
      old_viewport_height: oldViewport.height,
      new_viewport_width: newViewport.width,
      new_viewport_height: newViewport.height,
      
      // Categorización
      old_device_category: this.categorizeDevice(oldViewport.width),
      new_device_category: this.categorizeDevice(newViewport.width),
      
      // ¿Cambió la categoría de dispositivo?
      device_category_changed: this.categorizeDevice(oldViewport.width) !== this.categorizeDevice(newViewport.width),
      
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Evento: Predicción ML realizada
   */
  trackModelPrediction(inputFeatures, prediction, modelMetrics) {
    if (!this.isInitialized) return;

    globalThis.gtag('event', 'model_prediction', {
      user_temp_id: this.userTempId,
      session_id: this.sessionId,
      
      // Input del modelo
      feature_count: inputFeatures.length,
      feature_temporal_hour: inputFeatures[0], // hour_sin
      feature_device_touch: inputFeatures[4],  // touch_enabled
      feature_viewport_aspect: inputFeatures[6], // viewport_aspect_ratio
      
      // Output del modelo
      predicted_classes_count: prediction.css_classes.length,
      predicted_variables_count: Object.keys(prediction.css_variables).length,
      
      // Métricas del modelo
      model_version: modelMetrics.version,
      prediction_confidence: modelMetrics.confidence,
      processing_time_ms: modelMetrics.processing_time_ms,
      
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Evento: Sesión completada (para análisis de comportamiento)
   */
  trackSessionSummary() {
    if (!this.isInitialized) return;

    const sessionData = {
      user_temp_id: this.userTempId,
      session_id: this.sessionId,
      
      // Métricas de sesión
      session_duration_seconds: this.getSessionDuration(),
      total_interactions: this.getTotalInteractions(),
      pages_viewed: this.getPagesViewed(),
      max_scroll_depth: this.getMaxScrollDepth(),
      
      // Contexto promedio de la sesión
      avg_viewport_width: this.getAvgViewportWidth(),
      device_changes: this.getDeviceChanges(),
      
      // Adaptaciones aplicadas
      ui_adaptations_count: this.getUIAdaptationsCount(),
      
      timestamp: new Date().toISOString()
    };

    globalThis.gtag('event', 'session_summary', sessionData);

    // Guardar en localStorage para futuras sesiones
    this.saveSessionData(sessionData);
  }

  // Métodos auxiliares
  categorizeDevice(width) {
    if (width <= 768) return 'mobile';
    if (width <= 1024) return 'tablet';
    if (width <= 1920) return 'desktop';
    return 'large_desktop';
  }

  getTimeOnPage() {
    return Math.floor((Date.now() - this.pageStartTime) / 1000);
  }

  getScrollDepth() {
    const scrolled = globalThis.scrollY;
    const total = document.documentElement.scrollHeight - globalThis.innerHeight;
    return total > 0 ? Math.round((scrolled / total) * 100) / 100 : 0;
  }

  // Utilidades de cookies
  setCookie(name, value, days) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Lax`;
  }

  getCookie(name) {
    return document.cookie.split('; ').reduce((r, v) => {
      const parts = v.split('=');
      return parts[0] === name ? decodeURIComponent(parts[1]) : r;
    }, '');
  }

  // Métodos para métricas de sesión
  getSessionDuration() {
    return Math.floor((Date.now() - this.pageStartTime) / 1000);
  }

  getTotalInteractions() {
    return this.totalInteractions;
  }

  incrementInteractions() {
    this.totalInteractions++;
  }

  getPagesViewed() {
    return this.pagesViewed.size;
  }

  addPageView(path) {
    this.pagesViewed.add(path);
  }

  getMaxScrollDepth() {
    const currentDepth = this.getScrollDepth();
    this.maxScrollDepth = Math.max(this.maxScrollDepth, currentDepth);
    return this.maxScrollDepth;
  }

  getAvgViewportWidth() {
    return globalThis.innerWidth || 1366; // Default
  }

  getDeviceChanges() {
    return this.viewportChanges;
  }

  incrementViewportChanges() {
    this.viewportChanges++;
  }

  getUIAdaptationsCount() {
    return this.uiAdaptationsCount;
  }

  incrementUIAdaptations() {
    this.uiAdaptationsCount++;
  }

  saveSessionData(sessionData) {
    try {
      const existingSessions = JSON.parse(localStorage.getItem('frontend_efimero_sessions') || '[]');
      existingSessions.push(sessionData);
      
      // Mantener solo las últimas 10 sesiones
      const recentSessions = existingSessions.slice(-10);
      localStorage.setItem('frontend_efimero_sessions', JSON.stringify(recentSessions));
    } catch (error) {
      console.warn('Error saving session data:', error);
    }
  }
}

// Instancia global
const analytics = new AdaptiveUIAnalytics();

export default analytics;
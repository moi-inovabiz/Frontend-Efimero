/**
 * Custom Hook para captura de datos efímeros EXPANDIDOS (FASE 1)
 * Captura 46+ puntos de datos del navegador sin requerir permisos
 */

import { useEffect, useState } from 'react';
import { 
  getBrowser, 
  getOS, 
  getDeviceType,
  getConnectionInfo,
  getTimezone,
  getLocale,
  getHardwareInfo,
  getAccessibilityPreferences,
  getZoomLevel,
  isPWA,
  getScreenOrientation,
  getStorageInfo,
  isModernBrowser
} from '@/lib/browser-detection';
import { getBehaviorMetrics } from '@/lib/analytics/behavior-tracker';

export interface UserContextData {
  // ========== DATOS BÁSICOS (Existentes) ==========
  hora_local: string;
  prefers_color_scheme: 'light' | 'dark' | 'no-preference';
  viewport_width: number;
  viewport_height: number;
  touch_enabled: boolean;
  device_pixel_ratio: number;
  user_agent: string;
  session_id: string;
  page_path: string;
  
  // ========== GEOLOCALIZACIÓN (Sin GPS) ==========
  timezone: string;                    // "America/Santiago"
  locale: string;                      // "es-CL"
  languages: string[];                 // ["es-CL", "es", "en"]
  
  // ========== HARDWARE ==========
  cpu_cores: number;                   // 8, 4, 2
  device_memory: number;               // GB: 8, 4, 2
  max_touch_points: number;            // 0, 1, 5, 10
  
  // ========== RED ==========
  connection_type: string;             // "4g", "3g", "wifi", "unknown"
  connection_effective_type: string;   // "4g", "3g", "2g", "slow-2g"
  connection_downlink: number;         // Mbps
  connection_rtt: number;              // Round-trip time (ms)
  save_data_mode: boolean;             // Modo ahorro de datos
  
  // ========== ACCESIBILIDAD ==========
  prefers_contrast: boolean;           // Contraste alto
  prefers_reduced_motion: boolean;     // Reducir animaciones
  prefers_reduced_transparency: boolean; // Reducir transparencias
  
  // ========== VISUAL ==========
  zoom_level: number;                  // 1.0, 1.5, 2.0
  screen_orientation: string;          // "portrait-primary", "landscape-primary"
  
  // ========== DISPOSITIVO ==========
  os_name: string;                     // "Windows", "iOS", "Android", "macOS"
  os_version: string;                  // "10/11", "14.6", "12"
  browser_name: string;                // "Chrome", "Safari", "Firefox"
  browser_version: string;             // "110.0"
  browser_major_version: number;       // 110
  device_type: 'mobile' | 'tablet' | 'desktop';
  is_mobile_os: boolean;
  is_touch_device: boolean;
  is_modern_browser: boolean;
  
  // ========== STORAGE Y PRIVACIDAD ==========
  cookies_enabled: boolean;
  do_not_track: string;                // "1", "0", "unspecified"
  is_pwa: boolean;                     // Instalada como PWA
  
  // ========== COMPORTAMIENTO (Métricas continuas) ==========
  idle_time_seconds?: number;          // Tiempo inactivo
  avg_scroll_speed?: number;           // Velocidad de scroll
  avg_typing_speed?: number;           // WPM
  error_rate?: number;                 // Tasa de errores
  prefers_keyboard?: boolean;          // Preferencia teclado vs mouse
  max_scroll_depth?: number;           // Profundidad máxima de scroll
  total_interactions?: number;         // Total de interacciones
  session_duration_seconds?: number;   // Duración de sesión
}

export function useEphemeralContext(): UserContextData | null {
  const [contextData, setContextData] = useState<UserContextData | null>(null);

  useEffect(() => {
    /**
     * FASE 1 EXPANDIDA: Captura de 46+ datos efímeros del navegador
     * Sin requerir permisos del usuario
     */
    
    const captureContext = (): UserContextData => {
      // Generar session_id único para esta sesión
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      // Obtener información del navegador usando helpers
      const browserInfo = getBrowser();
      const osInfo = getOS();
      const deviceInfo = getDeviceType();
      const connectionInfo = getConnectionInfo();
      const localeInfo = getLocale();
      const hardwareInfo = getHardwareInfo();
      const accessibilityInfo = getAccessibilityPreferences();
      const storageInfo = getStorageInfo();
      
      // Datos básicos (existentes)
      const basicContext = {
        // Contexto temporal
        hora_local: new Date().toISOString(),
        
        // Preferencias del sistema
        prefers_color_scheme: (() => {
          if (typeof globalThis.window !== 'undefined' && globalThis.window.matchMedia) {
            if (globalThis.window.matchMedia('(prefers-color-scheme: dark)').matches) {
              return 'dark' as const;
            } else if (globalThis.window.matchMedia('(prefers-color-scheme: light)').matches) {
              return 'light' as const;
            }
          }
          return 'no-preference' as const;
        })(),
        
        // Viewport y dispositivo
        viewport_width: typeof globalThis.window !== 'undefined' ? globalThis.window.innerWidth : 0,
        viewport_height: typeof globalThis.window !== 'undefined' ? globalThis.window.innerHeight : 0,
        device_pixel_ratio: typeof globalThis.window !== 'undefined' ? globalThis.window.devicePixelRatio : 1,
        
        // Capacidades táctiles
        touch_enabled: typeof globalThis.window !== 'undefined' && ('ontouchstart' in globalThis.window || navigator.maxTouchPoints > 0),
        
        // Metadatos de red
        user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
        
        // Sesión y navegación
        session_id: sessionId,
        page_path: typeof globalThis.window !== 'undefined' ? globalThis.window.location.pathname : '/'
      };
      
      // Datos expandidos (nuevos)
      const expandedContext: UserContextData = {
        ...basicContext,
        
        // Geolocalización (sin GPS)
        timezone: getTimezone(),
        locale: localeInfo.primary,
        languages: localeInfo.languages,
        
        // Hardware
        cpu_cores: hardwareInfo.cpuCores,
        device_memory: hardwareInfo.deviceMemory,
        max_touch_points: hardwareInfo.maxTouchPoints,
        
        // Red
        connection_type: connectionInfo.type,
        connection_effective_type: connectionInfo.effectiveType,
        connection_downlink: connectionInfo.downlink,
        connection_rtt: connectionInfo.rtt,
        save_data_mode: connectionInfo.saveData,
        
        // Accesibilidad
        prefers_contrast: accessibilityInfo.prefersContrast,
        prefers_reduced_motion: accessibilityInfo.prefersReducedMotion,
        prefers_reduced_transparency: accessibilityInfo.prefersReducedTransparency,
        
        // Visual
        zoom_level: getZoomLevel(),
        screen_orientation: getScreenOrientation(),
        
        // Dispositivo
        os_name: osInfo.name,
        os_version: osInfo.version,
        browser_name: browserInfo.name,
        browser_version: browserInfo.version,
        browser_major_version: browserInfo.major_version,
        device_type: deviceInfo.type,
        is_mobile_os: deviceInfo.is_mobile_os,
        is_touch_device: deviceInfo.is_touch_device,
        is_modern_browser: isModernBrowser(browserInfo),
        
        // Storage y privacidad
        cookies_enabled: storageInfo.cookiesEnabled,
        do_not_track: storageInfo.doNotTrack,
        is_pwa: isPWA(),
        
        // Comportamiento (se actualizará después)
        idle_time_seconds: 0,
        avg_scroll_speed: 0,
        avg_typing_speed: 0,
        error_rate: 0,
        prefers_keyboard: false,
        max_scroll_depth: 0,
        total_interactions: 0,
        session_duration_seconds: 0
      };
      
      return expandedContext;
    };

    // Capturar contexto inmediatamente
    const context = captureContext();
    setContextData(context);
    
    console.log('📊 Contexto efímero expandido capturado:', {
      basic: '9 campos',
      geolocation: '3 campos (timezone, locale, languages)',
      hardware: '3 campos (CPU, RAM, touch points)',
      network: '5 campos (type, speed, latency, save data)',
      accessibility: '3 campos (contrast, motion, transparency)',
      visual: '2 campos (zoom, orientation)',
      device: '9 campos (OS, browser, device type)',
      storage: '3 campos (cookies, DNT, PWA)',
      behavior: '8 campos (idle, scroll, typing, errors)',
      total: '45+ campos capturados'
    });

    // Listener para cambios de viewport (responsive)
    const handleResize = () => {
      setContextData(prev => prev ? {
        ...prev,
        viewport_width: globalThis.window.innerWidth,
        viewport_height: globalThis.window.innerHeight,
        screen_orientation: getScreenOrientation()
      } : null);
    };

    // Listener para cambios de color scheme
    const darkModeQuery = globalThis.window.matchMedia('(prefers-color-scheme: dark)');
    const lightModeQuery = globalThis.window.matchMedia('(prefers-color-scheme: light)');
    
    const handleColorSchemeChange = () => {
      setContextData(prev => prev ? {
        ...prev,
        prefers_color_scheme: (() => {
          if (darkModeQuery.matches) return 'dark' as const;
          if (lightModeQuery.matches) return 'light' as const;
          return 'no-preference' as const;
        })()
      } : null);
    };
    
    // Actualizar métricas de comportamiento cada 10 segundos
    const behaviorInterval = setInterval(() => {
      try {
        const behaviorMetrics = getBehaviorMetrics();
        setContextData(prev => prev ? {
          ...prev,
          idle_time_seconds: behaviorMetrics.idle_time_seconds,
          avg_scroll_speed: behaviorMetrics.avg_scroll_speed,
          avg_typing_speed: behaviorMetrics.avg_typing_speed,
          error_rate: behaviorMetrics.error_rate,
          prefers_keyboard: behaviorMetrics.prefers_keyboard,
          max_scroll_depth: behaviorMetrics.max_scroll_depth,
          total_interactions: behaviorMetrics.total_interactions,
          session_duration_seconds: behaviorMetrics.session_duration_seconds
        } : null);
      } catch (error) {
        console.warn('Error actualizando métricas de comportamiento:', error);
      }
    }, 10000); // Cada 10 segundos

    // Registrar listeners
    globalThis.window.addEventListener('resize', handleResize);
    darkModeQuery.addEventListener('change', handleColorSchemeChange);
    lightModeQuery.addEventListener('change', handleColorSchemeChange);

    // Cleanup
    return () => {
      globalThis.window.removeEventListener('resize', handleResize);
      darkModeQuery.removeEventListener('change', handleColorSchemeChange);
      lightModeQuery.removeEventListener('change', handleColorSchemeChange);
      clearInterval(behaviorInterval);
    };
  }, []);

  return contextData;
}
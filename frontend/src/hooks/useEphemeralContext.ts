/**
 * Custom Hook para captura de datos efímeros (FASE 1)
 * Implementa la captura JS del contexto del usuario
 */

import { useEffect, useState } from 'react';

export interface UserContextData {
  hora_local: string;
  prefers_color_scheme: 'light' | 'dark' | 'no-preference';
  viewport_width: number;
  viewport_height: number;
  touch_enabled: boolean;
  device_pixel_ratio: number;
  user_agent: string;
  session_id: string;
  page_path: string;
}

export function useEphemeralContext(): UserContextData | null {
  const [contextData, setContextData] = useState<UserContextData | null>(null);

  useEffect(() => {
    /**
     * FASE 1: Captura de datos efímeros del navegador
     * Siguiendo las especificaciones del Frontend Efímero
     */
    
    const captureContext = (): UserContextData => {
      // Generar session_id único para esta sesión
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      return {
        // Contexto temporal
        hora_local: new Date().toISOString(),
        
        // Preferencias del sistema
        prefers_color_scheme: (() => {
          if (typeof window !== 'undefined' && window.matchMedia) {
            if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
              return 'dark';
            } else if (window.matchMedia('(prefers-color-scheme: light)').matches) {
              return 'light';
            }
          }
          return 'no-preference';
        })(),
        
        // Viewport y dispositivo
        viewport_width: typeof window !== 'undefined' ? window.innerWidth : 0,
        viewport_height: typeof window !== 'undefined' ? window.innerHeight : 0,
        device_pixel_ratio: typeof window !== 'undefined' ? window.devicePixelRatio : 1,
        
        // Capacidades táctiles
        touch_enabled: typeof window !== 'undefined' && ('ontouchstart' in window || navigator.maxTouchPoints > 0),
        
        // Metadatos de red
        user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
        
        // Sesión y navegación
        session_id: sessionId,
        page_path: typeof window !== 'undefined' ? window.location.pathname : '/'
      };
    };

    // Capturar contexto inmediatamente
    const context = captureContext();
    setContextData(context);

    // Listener para cambios de viewport (responsive)
    const handleResize = () => {
      setContextData(prev => prev ? {
        ...prev,
        viewport_width: window.innerWidth,
        viewport_height: window.innerHeight
      } : null);
    };

    // Listener para cambios de color scheme
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const lightModeQuery = window.matchMedia('(prefers-color-scheme: light)');
    
    const handleColorSchemeChange = () => {
      setContextData(prev => prev ? {
        ...prev,
        prefers_color_scheme: (() => {
          if (darkModeQuery.matches) return 'dark';
          if (lightModeQuery.matches) return 'light';
          return 'no-preference';
        })()
      } : null);
    };

    // Registrar listeners
    window.addEventListener('resize', handleResize);
    darkModeQuery.addEventListener('change', handleColorSchemeChange);
    lightModeQuery.addEventListener('change', handleColorSchemeChange);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      darkModeQuery.removeEventListener('change', handleColorSchemeChange);
      lightModeQuery.removeEventListener('change', handleColorSchemeChange);
    };
  }, []);

  return contextData;
}
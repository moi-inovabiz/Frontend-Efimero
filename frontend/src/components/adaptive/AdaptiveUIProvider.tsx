/**
 * Componente principal AdaptiveUI
 * Orquesta las 3 fases del Frontend Efímero
 */

'use client';

import React, { useEffect, useState, ReactNode } from 'react';
import { useEphemeralContext, UserContextData } from '@/hooks/useEphemeralContext';
import { usePersona } from '@/hooks/usePersona';
import { AdaptiveUIClient } from '@/lib/api-client';
import { DesignTokens } from '@/types/adaptive-ui';
import { startBehaviorTracking, stopBehaviorTracking } from '@/lib/analytics/behavior-tracker';
import { PersonaSimulada } from '@/types/persona';

interface AdaptiveUIProviderProps {
  children: ReactNode;
}

interface AdaptiveUIContextType {
  designTokens: DesignTokens | null;
  isLoading: boolean;
  error: string | null;
  persona: PersonaSimulada | null;
  sendFeedback: (action: string, elementId?: string, elementClass?: string) => void;
  refreshPersona: () => Promise<void>;
}

const AdaptiveUIContext = React.createContext<AdaptiveUIContextType | null>(null);

export function AdaptiveUIProvider({ children }: AdaptiveUIProviderProps) {
  const ephemeralContext = useEphemeralContext();
  const { persona, isLoading: personaLoading, error: personaError, refreshPersona } = usePersona();
  const [designTokens, setDesignTokens] = useState<DesignTokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMounted, setIsMounted] = useState(false);
  const [hasFetchedDesign, setHasFetchedDesign] = useState(false);

  // Protección contra hydration mismatch
  useEffect(() => {
    setIsMounted(true);
  }, []);
  
  // Log persona cuando se carga
  useEffect(() => {
    if (persona && isMounted) {
      console.log('👤 Persona asignada:', {
        nombre: `${persona.nombre} ${persona.apellido}`,
        tipo: persona.tipo_cliente,
        edad: persona.edad,
        region: persona.region,
        preferencias: {
          densidad: persona.densidad_informacion,
          tipografia: persona.estilo_tipografia,
          animaciones: persona.nivel_animaciones,
          layout: persona.preferencia_layout
        }
      });
    }
  }, [persona, isMounted]);
  
  // Iniciar behavior tracking al montar el componente
  useEffect(() => {
    if (!isMounted) return;
    
    console.log('🎯 Iniciando behavior tracking...');
    startBehaviorTracking();
    
    return () => {
      console.log('🎯 Deteniendo behavior tracking...');
      stopBehaviorTracking();
    };
  }, [isMounted]);

  useEffect(() => {
    /**
     * Ejecutar FASE 2: Decisión Inteligente
     * Solo cuando el contexto efímero Y la persona estén disponibles Y el componente esté montado
     */
    console.log('🔍 [AdaptiveUI] Estado actual:', {
      isMounted,
      hasEphemeralContext: !!ephemeralContext,
      hasPersona: !!persona,
      personaLoading,
      hasFetchedDesign
    });
    
    // Evitar múltiples ejecuciones
    if (hasFetchedDesign) {
      return;
    }
    
    if (!ephemeralContext || !isMounted || !persona) {
      if (isMounted && !ephemeralContext) {
        console.log('⏳ [AdaptiveUI] Esperando contexto efímero...');
      }
      if (isMounted && !persona && !personaLoading) {
        console.log('⏳ [AdaptiveUI] Esperando persona simulada...');
      }
      return;
    }

    const requestAdaptiveDesign = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const request = {
          user_context: ephemeralContext,
          user_temp_id: AdaptiveUIClient.getUserTempId(),
          // Incluir datos de la persona simulada para predicciones consistentes
          persona_data: {
            edad: persona.edad,
            region: persona.region,
            tipo_cliente: persona.tipo_cliente,
            interes_principal: persona.interes_principal,
            uso_previsto: persona.uso_previsto,
            presupuesto: persona.presupuesto,
            tiene_vehiculo_actual: persona.tiene_vehiculo_actual,
            tamano_flota: persona.tamano_flota
          }
        };

        console.log('🎯 Solicitando diseño adaptativo con contexto expandido + persona simulada...', {
          basic_fields: 9,
          geolocation_fields: 3,
          hardware_fields: 3,
          network_fields: 5,
          accessibility_fields: 3,
          visual_fields: 2,
          device_fields: 9,
          storage_fields: 3,
          behavior_fields: 8,
          persona_fields: 8,
          total_fields: 53
        });

        const response = await AdaptiveUIClient.requestAdaptiveDesign(request);
        
        console.log('✅ Diseño adaptativo recibido:', response);
        console.log(`⚡ Procesado en ${response.processing_time_ms.toFixed(2)}ms`);

        setDesignTokens(response.design_tokens);
        setHasFetchedDesign(true); // Marcar como ejecutado

        // FASE 3: Inyectar tokens inmediatamente
        injectDesignTokens(response.design_tokens);

      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
        console.error('❌ Error en solicitud adaptativa:', errorMessage);
        setError(errorMessage);

        // Fallback: Usar preferencias de la persona simulada si están disponibles
        const fallbackTokens: DesignTokens = {
          css_classes: [
            persona.densidad_informacion ? `densidad-${persona.densidad_informacion}` : 'densidad-media',
            persona.estilo_tipografia ? `fuente-${persona.estilo_tipografia}` : 'fuente-sans',
            persona.nivel_animaciones ? `animacion-${persona.nivel_animaciones}` : 'animacion-media',
            persona.esquema_colores ? `modo-${persona.esquema_colores}` : 'modo-claro'
          ],
          css_variables: {
            '--font-size-base': '1rem',
            '--spacing-unit': '1rem',
            '--border-radius': '0.25rem'
          }
        };
        setDesignTokens(fallbackTokens);
        setHasFetchedDesign(true); // Marcar como ejecutado incluso en error
        injectDesignTokens(fallbackTokens);
      } finally {
        setIsLoading(false);
      }
    };

    requestAdaptiveDesign();
  }, [ephemeralContext, isMounted, persona]);

  /**
   * FASE 3: Inyección de tokens de diseño (Zero Flicker)
   */
  const injectDesignTokens = (tokens: DesignTokens) => {
    // Inyectar clases CSS en <html>
    const htmlElement = document.documentElement;
    
    // Limpiar clases previas del Frontend Efímero
    const existingClasses = htmlElement.className.split(' ').filter(cls => 
      !cls.startsWith('densidad-') && 
      !cls.startsWith('fuente-') && 
      !cls.startsWith('modo-')
    );
    
    // Aplicar nuevas clases predichas
    htmlElement.className = [...existingClasses, ...tokens.css_classes].join(' ');

    // Inyectar variables CSS en :root
    let styleElement = document.getElementById('adaptive-ui-variables');
    if (!styleElement) {
      styleElement = document.createElement('style');
      styleElement.id = 'adaptive-ui-variables';
      document.head.appendChild(styleElement);
    }

    const cssVariables = Object.entries(tokens.css_variables)
      .map(([key, value]) => `  ${key}: ${value};`)
      .join('\n');

    styleElement.textContent = `:root {\n${cssVariables}\n}`;

    console.log('🎨 Tokens de diseño inyectados:', tokens);
  };

  /**
   * Función para enviar feedback de comportamiento
   */
  const sendFeedback = (action: string, elementId?: string, elementClass?: string) => {
    if (!designTokens) return;

    const feedback = {
      action_type: action as any,
      element_id: elementId,
      element_class: elementClass,
      timestamp: new Date().toISOString(),
      session_duration: Date.now() - (ephemeralContext ? new Date(ephemeralContext.hora_local).getTime() : 0),
      page_path: window.location.pathname,
      design_tokens_used: designTokens
    };

    AdaptiveUIClient.sendFeedback(feedback);
  };
  
  /**
   * Wrapper de refreshPersona que resetea el flag de predicción
   */
  const refreshPersonaAndDesign = async () => {
    setHasFetchedDesign(false); // Resetear para permitir nueva predicción
    await refreshPersona();
  };

  const contextValue: AdaptiveUIContextType = {
    designTokens,
    isLoading: isLoading || personaLoading,
    error: error || personaError,
    persona,
    sendFeedback,
    refreshPersona: refreshPersonaAndDesign
  };

  return (
    <AdaptiveUIContext.Provider value={contextValue}>
      {children}
    </AdaptiveUIContext.Provider>
  );
}

/**
 * Hook para usar el contexto del Frontend Efímero
 */
export function useAdaptiveUI(): AdaptiveUIContextType {
  const context = React.useContext(AdaptiveUIContext);
  if (!context) {
    throw new Error('useAdaptiveUI debe usarse dentro de AdaptiveUIProvider');
  }
  return context;
}
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
  assignSpecificPersona: (personaId: string) => Promise<void>;
}

const AdaptiveUIContext = React.createContext<AdaptiveUIContextType | null>(null);

export function AdaptiveUIProvider({ children }: AdaptiveUIProviderProps) {
  const ephemeralContext = useEphemeralContext();
  const { persona, isLoading: personaLoading, error: personaError, refreshPersona, assignSpecificPersona } = usePersona(ephemeralContext);
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
   * Re-inyectar variables dinámicas cuando cambia la persona
   * (sin necesidad de nueva predicción ML)
   */
  useEffect(() => {
    if (!isMounted || !persona || !designTokens) return;
    
    console.log('🔄 Persona cambió, actualizando variables dinámicas...');
    injectDesignTokens(designTokens);
  }, [persona, isMounted, designTokens]);

  /**
   * FASE 3: Inyección de tokens de diseño (Zero Flicker)
   * Ahora con adaptaciones dinámicas basadas en la persona
   */
  const injectDesignTokens = (tokens: DesignTokens) => {
    if (!persona) return;
    
    // Inyectar clases CSS en <html>
    const htmlElement = document.documentElement;
    
    // Limpiar clases previas del Frontend Efímero
    const existingClasses = htmlElement.className.split(' ').filter(cls => 
      !cls.startsWith('densidad-') && 
      !cls.startsWith('fuente-') && 
      !cls.startsWith('modo-') &&
      !cls.startsWith('animacion-') &&
      !cls.startsWith('layout-') &&
      !cls.startsWith('edad-') &&
      !cls.startsWith('cliente-')
    );
    
    // Aplicar nuevas clases predichas
    htmlElement.className = [...existingClasses, ...tokens.css_classes].join(' ');

    // === ADAPTACIONES DINÁMICAS BASADAS EN PERSONA ===
    
    // 1. Font size basado en edad
    let fontSizeBase = '16px';
    if (persona.edad < 40) {
      fontSizeBase = '16px'; // Jóvenes: tamaño normal
    } else if (persona.edad >= 40 && persona.edad < 60) {
      fontSizeBase = '18px'; // Adultos: ligeramente más grande
    } else {
      fontSizeBase = '20px'; // Mayores: más legible
    }
    
    // 2. Theme basado en tipo_cliente
    let primaryColor = '#06B6D4'; // Cyan por defecto
    let backgroundColor = '#ffffff';
    let textColor = '#111827';
    
    if (persona.tipo_cliente === 'empresa') {
      primaryColor = '#3B82F6'; // Azul profesional para empresas
      // Theme puede ser más formal
    } else {
      primaryColor = persona.color_favorito || '#06B6D4'; // Color favorito para personas
    }
    
    // 3. Velocidad de animaciones basado en nivel_animaciones
    let animationDuration = '0.3s';
    if (persona.nivel_animaciones === 'bajo') {
      animationDuration = '0.1s'; // Rápido
    } else if (persona.nivel_animaciones === 'medio') {
      animationDuration = '0.3s'; // Normal
    } else if (persona.nivel_animaciones === 'alto') {
      animationDuration = '0.5s'; // Suave
    }
    
    // 4. Espaciado basado en densidad_informacion
    let spacingUnit = '1rem';
    if (persona.densidad_informacion === 'compacta') {
      spacingUnit = '0.75rem'; // Más apretado
    } else if (persona.densidad_informacion === 'comoda') {
      spacingUnit = '1rem'; // Normal
    } else if (persona.densidad_informacion === 'amplia') {
      spacingUnit = '1.5rem'; // Más espacioso
    }
    
    // 5. Border radius basado en preferencia_layout
    let borderRadius = '0.5rem';
    if (persona.preferencia_layout === 'minimalista') {
      borderRadius = '0.25rem'; // Más cuadrado
    } else if (persona.preferencia_layout === 'cards') {
      borderRadius = '0.75rem'; // Redondeado
    } else if (persona.preferencia_layout === 'grid') {
      borderRadius = '0.5rem'; // Intermedio
    }

    // Inyectar variables CSS en :root
    let styleElement = document.getElementById('adaptive-ui-variables');
    if (!styleElement) {
      styleElement = document.createElement('style');
      styleElement.id = 'adaptive-ui-variables';
      document.head.appendChild(styleElement);
    }

    // Combinar variables predichas del ML + variables dinámicas de persona
    const dynamicVariables = {
      // Variables dinámicas basadas en persona
      '--adaptive-font-size-base': fontSizeBase,
      '--adaptive-primary-color': primaryColor,
      '--adaptive-bg-color': backgroundColor,
      '--adaptive-text-color': textColor,
      '--adaptive-animation-duration': animationDuration,
      '--adaptive-spacing-unit': spacingUnit,
      '--adaptive-border-radius': borderRadius,
      
      // Metadatos de persona (para debugging)
      '--persona-edad': persona.edad.toString(),
      '--persona-tipo': persona.tipo_cliente,
      
      // Variables del ML (mantener las originales)
      ...tokens.css_variables
    };

    const cssVariables = Object.entries(dynamicVariables)
      .map(([key, value]) => `  ${key}: ${value};`)
      .join('\n');

    styleElement.textContent = `:root {\n${cssVariables}\n}`;

    console.log('🎨 Tokens de diseño inyectados:', tokens);
    console.log('🎭 Adaptaciones dinámicas aplicadas:', {
      edad: persona.edad,
      fontSize: fontSizeBase,
      tipo_cliente: persona.tipo_cliente,
      primaryColor,
      nivel_animaciones: persona.nivel_animaciones,
      animationDuration,
      densidad_informacion: persona.densidad_informacion,
      spacingUnit,
      preferencia_layout: persona.preferencia_layout,
      borderRadius
    });
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
  
  /**
   * Wrapper de assignSpecificPersona que resetea el flag de predicción
   */
  const handleAssignSpecificPersona = async (personaId: string) => {
    setHasFetchedDesign(false); // Resetear para permitir nueva predicción
    await assignSpecificPersona(personaId);
  };

  const contextValue: AdaptiveUIContextType = {
    designTokens,
    isLoading: isLoading || personaLoading,
    error: error || personaError,
    persona,
    sendFeedback,
    refreshPersona: refreshPersonaAndDesign,
    assignSpecificPersona: handleAssignSpecificPersona
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
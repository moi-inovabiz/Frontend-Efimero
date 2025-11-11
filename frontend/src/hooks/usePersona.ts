/**
 * Hook para gestionar Persona Simulada asignada al usuario
 * Mantiene persistencia entre recargas usando localStorage y session_id
 * Ahora con matching inteligente basado en contexto del navegador
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { PersonaSimulada, PersonaAssignmentResponse } from '@/types/persona';
import { UserContextData } from './useEphemeralContext';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const SESSION_ID_KEY = 'ephemeral_session_id';
const PERSONA_KEY = 'assigned_persona';
const PERSONA_EXPIRY_KEY = 'persona_expiry';
const PERSONA_TTL = 24 * 60 * 60 * 1000; // 24 horas

/**
 * Interfaz para el contexto que espera el backend
 */
interface ContextoAsignacion {
  hora_del_dia: number;         // 0-23
  es_fin_de_semana: boolean;
  ciudad?: string;
  region?: string;
  pais?: string;
  es_movil: boolean;
  es_tablet: boolean;
  sistema_operativo?: string;
  tipo_conexion?: string;
}

/**
 * Genera un UUID v4 simple
 */
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Transforma el contexto efímero en el formato que espera el backend
 */
function transformContextToBackend(context: UserContextData | null): ContextoAsignacion | null {
  if (!context) return null;
  
  try {
    // Extraer hora del día del ISO string
    const horaDelDia = new Date(context.hora_local).getHours();
    
    // Determinar si es fin de semana
    const diaActual = new Date().getDay(); // 0 = Domingo, 6 = Sábado
    const esFinDeSemana = diaActual === 0 || diaActual === 6;
    
    // Extraer región del timezone (ej: "America/Santiago" → "Metropolitana")
    // Mapeo de ciudades a regiones chilenas
    const timezoneParts = context.timezone.split('/');
    const ciudadTimezone = timezoneParts[1] || '';
    
    // Mapeo de ciudad/timezone a regiones de Chile
    let region = '';
    const ciudadLower = ciudadTimezone.toLowerCase();
    
    if (ciudadLower.includes('santiago')) {
      region = 'Metropolitana';
    } else if (ciudadLower.includes('valparaiso') || ciudadLower.includes('valparaíso')) {
      region = 'Valparaíso';
    } else if (ciudadLower.includes('concepcion') || ciudadLower.includes('concepción')) {
      region = 'Biobío';
    } else if (ciudadLower.includes('punta_arenas') || ciudadLower.includes('punta arenas')) {
      region = 'Magallanes';
    } else if (ciudadLower.includes('easter') || ciudadLower.includes('pascua')) {
      region = 'Valparaíso'; // Isla de Pascua
    } else {
      // Fallback: usar el país o la parte del timezone
      region = timezoneParts[0] || 'Metropolitana'; // Default a Metropolitana
    }
    
    const pais = timezoneParts[0] || '';
    
    // Ciudad desde locale (ej: "es-CL" → "CL")
    const ciudad = context.locale.split('-')[1] || '';
    
    console.log('[Persona] 🗺️ Contexto geográfico:', {
      timezone: context.timezone,
      ciudadTimezone,
      regionMapeada: region,
      locale: context.locale
    });
    
    return {
      hora_del_dia: horaDelDia,
      es_fin_de_semana: esFinDeSemana,
      ciudad,
      region,
      pais,
      es_movil: context.device_type === 'mobile',
      es_tablet: context.device_type === 'tablet',
      sistema_operativo: context.os_name,
      tipo_conexion: context.connection_effective_type || context.connection_type
    };
  } catch (error) {
    console.error('[Persona] Error transformando contexto:', error);
    return null;
  }
}

interface UsePersonaResult {
  persona: PersonaSimulada | null;
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;
  refreshPersona: () => Promise<void>;
  clearPersona: () => void;
  // Nueva función para refresh con contexto explícito
  refreshPersonaWithContext: (context: UserContextData | null) => Promise<void>;
  // Nueva función para asignar persona específica
  assignSpecificPersona: (personaId: string) => Promise<void>;
}

export function usePersona(userContext?: UserContextData | null): UsePersonaResult {
  const [persona, setPersona] = useState<PersonaSimulada | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Obtiene o genera el session_id
   */
  const getOrCreateSessionId = useCallback((): string => {
    if (typeof window === 'undefined') return '';
    
    let storedSessionId = localStorage.getItem(SESSION_ID_KEY);
    
    if (!storedSessionId) {
      storedSessionId = generateUUID();
      localStorage.setItem(SESSION_ID_KEY, storedSessionId);
      console.log('[Persona] Nuevo session_id generado:', storedSessionId);
    }
    
    return storedSessionId;
  }, []);

  /**
   * Verifica si la persona en cache es válida
   */
  const isPersonaCacheValid = useCallback((): boolean => {
    if (typeof window === 'undefined') return false;
    
    const cachedPersona = localStorage.getItem(PERSONA_KEY);
    const expiry = localStorage.getItem(PERSONA_EXPIRY_KEY);
    
    if (!cachedPersona || !expiry) return false;
    
    const expiryTime = parseInt(expiry, 10);
    const now = Date.now();
    
    if (now > expiryTime) {
      console.log('[Persona] Cache expirado');
      return false;
    }
    
    return true;
  }, []);

  /**
   * Obtiene persona desde localStorage
   */
  const getPersonaFromCache = useCallback((): PersonaSimulada | null => {
    if (typeof window === 'undefined') return null;
    
    if (!isPersonaCacheValid()) {
      return null;
    }
    
    try {
      const cachedPersona = localStorage.getItem(PERSONA_KEY);
      if (cachedPersona) {
        return JSON.parse(cachedPersona);
      }
    } catch (error) {
      console.error('[Persona] Error parseando cache:', error);
    }
    
    return null;
  }, [isPersonaCacheValid]);

  /**
   * Guarda persona en localStorage
   */
  const savePersonaToCache = useCallback((personaData: PersonaSimulada) => {
    if (typeof window === 'undefined') return;
    
    try {
      localStorage.setItem(PERSONA_KEY, JSON.stringify(personaData));
      localStorage.setItem(PERSONA_EXPIRY_KEY, (Date.now() + PERSONA_TTL).toString());
      console.log('[Persona] Guardada en cache:', personaData.nombre, personaData.apellido);
    } catch (error) {
      console.error('[Persona] Error guardando en cache:', error);
    }
  }, []);

  /**
   * Asigna una persona desde el servidor con contexto inteligente
   */
  const assignPersona = useCallback(async (
    currentSessionId: string, 
    context: UserContextData | null = null
  ): Promise<PersonaSimulada | null> => {
    try {
      console.log('[Persona] Solicitando asignación para session_id:', currentSessionId);
      
      // Transformar contexto al formato del backend
      const contextoBackend = transformContextToBackend(context);
      
      if (contextoBackend) {
        console.log('[Persona] 🧠 Usando matching inteligente con contexto:', {
          hora: contextoBackend.hora_del_dia,
          fin_semana: contextoBackend.es_fin_de_semana,
          region: contextoBackend.region,
          dispositivo: contextoBackend.es_movil ? 'móvil' : contextoBackend.es_tablet ? 'tablet' : 'desktop',
          conexion: contextoBackend.tipo_conexion
        });
      } else {
        console.log('[Persona] ⚠️ Sin contexto disponible, usando asignación aleatoria');
      }
      
      const response = await fetch(`${API_BASE_URL}/personas/assign`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': currentSessionId
        },
        body: contextoBackend ? JSON.stringify(contextoBackend) : undefined
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data: PersonaAssignmentResponse = await response.json();
      
      if (data.success && data.persona) {
        const logData: any = {
          persona: `${data.persona.nombre} ${data.persona.apellido}`,
          tipo: data.persona.tipo_cliente,
          edad: data.persona.edad,
          isNew: data.is_new_assignment
        };
        
        // Si hay score de matching, mostrarlo
        if ('matching_score' in data) {
          logData.matchingScore = data.matching_score;
        }
        
        console.log('[Persona] ✅ Asignación exitosa:', logData);
        
        savePersonaToCache(data.persona);
        return data.persona;
      }

      throw new Error('Respuesta inválida del servidor');
    } catch (error) {
      console.error('[Persona] Error asignando persona:', error);
      throw error;
    }
  }, [savePersonaToCache]);

  /**
   * Refresca la persona (fuerza nueva asignación) sin contexto
   */
  const refreshPersona = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Generar NUEVO session_id para obtener una persona diferente
      const newSessionId = generateUUID();
      
      // Limpiar cache Y session_id anterior
      if (typeof window !== 'undefined') {
        localStorage.removeItem(PERSONA_KEY);
        localStorage.removeItem(PERSONA_EXPIRY_KEY);
        localStorage.setItem(SESSION_ID_KEY, newSessionId); // Guardar nuevo session_id
      }
      
      setSessionId(newSessionId);
      console.log('[Persona] Nuevo session_id generado para refresh:', newSessionId);
      
      const newPersona = await assignPersona(newSessionId, null);
      setPersona(newPersona);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      console.error('[Persona] Error en refreshPersona:', err);
    } finally {
      setIsLoading(false);
    }
  }, [assignPersona]);

  /**
   * Refresca la persona con contexto inteligente
   */
  const refreshPersonaWithContext = useCallback(async (context: UserContextData | null) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Generar NUEVO session_id para obtener una persona diferente
      const newSessionId = generateUUID();
      
      // Limpiar cache Y session_id anterior
      if (typeof window !== 'undefined') {
        localStorage.removeItem(PERSONA_KEY);
        localStorage.removeItem(PERSONA_EXPIRY_KEY);
        localStorage.setItem(SESSION_ID_KEY, newSessionId);
      }
      
      setSessionId(newSessionId);
      console.log('[Persona] 🔄 Refresh con contexto inteligente, nuevo session_id:', newSessionId);
      
      const newPersona = await assignPersona(newSessionId, context);
      setPersona(newPersona);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      console.error('[Persona] Error en refreshPersonaWithContext:', err);
    } finally {
      setIsLoading(false);
    }
  }, [assignPersona]);

  /**
   * Limpia la persona asignada
   */
  const clearPersona = useCallback(() => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(PERSONA_KEY);
      localStorage.removeItem(PERSONA_EXPIRY_KEY);
      // NO limpiar session_id para mantener persistencia
    }
    setPersona(null);
    setError(null);
    console.log('[Persona] Persona limpiada');
  }, []);

  /**
   * Asigna una persona específica por ID (para selector manual)
   */
  const assignSpecificPersona = useCallback(async (personaId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const currentSessionId = getOrCreateSessionId();
      
      console.log('[Persona] 🎯 Asignando persona específica:', personaId);
      
      const response = await fetch(`${API_BASE_URL}/personas/assign/${personaId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': currentSessionId
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data: PersonaAssignmentResponse = await response.json();
      
      if (data.success && data.persona) {
        console.log('[Persona] ✅ Persona específica asignada:', {
          persona: `${data.persona.nombre} ${data.persona.apellido}`,
          tipo: data.persona.tipo_cliente,
          edad: data.persona.edad
        });
        
        // Limpiar cache y guardar nueva persona
        if (typeof window !== 'undefined') {
          localStorage.removeItem(PERSONA_KEY);
          localStorage.removeItem(PERSONA_EXPIRY_KEY);
        }
        
        savePersonaToCache(data.persona);
        setPersona(data.persona);
      } else {
        throw new Error('Respuesta inválida del servidor');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      console.error('[Persona] Error asignando persona específica:', err);
      throw err; // Re-throw para que el componente pueda manejarlo
    } finally {
      setIsLoading(false);
    }
  }, [getOrCreateSessionId, savePersonaToCache]);

  /**
   * Inicialización: obtener o asignar persona
   */
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const initPersona = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // 1. Obtener session_id
        const currentSessionId = getOrCreateSessionId();
        setSessionId(currentSessionId);

        // 2. Verificar cache local
        const cachedPersona = getPersonaFromCache();
        
        if (cachedPersona) {
          console.log('[Persona] Usando persona desde cache:', cachedPersona.nombre, cachedPersona.apellido);
          setPersona(cachedPersona);
          setIsLoading(false);
          return;
        }

        // 3. Si no hay cache válido, solicitar del servidor CON CONTEXTO
        console.log('[Persona] Cache no disponible, solicitando del servidor con contexto...');
        const assignedPersona = await assignPersona(currentSessionId, userContext);
        setPersona(assignedPersona);

      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
        setError(errorMessage);
        console.error('[Persona] Error en inicialización:', err);
      } finally {
        setIsLoading(false);
      }
    };

    initPersona();
  }, [getOrCreateSessionId, getPersonaFromCache, assignPersona, userContext]);

  return {
    persona,
    sessionId,
    isLoading,
    error,
    refreshPersona,
    refreshPersonaWithContext,
    assignSpecificPersona,
    clearPersona
  };
}

/**
 * Hook para gestionar Persona Simulada asignada al usuario
 * Mantiene persistencia entre recargas usando localStorage y session_id
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { PersonaSimulada, PersonaAssignmentResponse } from '@/types/persona';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const SESSION_ID_KEY = 'ephemeral_session_id';
const PERSONA_KEY = 'assigned_persona';
const PERSONA_EXPIRY_KEY = 'persona_expiry';
const PERSONA_TTL = 24 * 60 * 60 * 1000; // 24 horas

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

interface UsePersonaResult {
  persona: PersonaSimulada | null;
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;
  refreshPersona: () => Promise<void>;
  clearPersona: () => void;
}

export function usePersona(): UsePersonaResult {
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
   * Asigna una persona desde el servidor
   */
  const assignPersona = useCallback(async (currentSessionId: string): Promise<PersonaSimulada | null> => {
    try {
      console.log('[Persona] Solicitando asignación para session_id:', currentSessionId);
      
      const response = await fetch(`${API_BASE_URL}/personas/assign`, {
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
        console.log('[Persona] Asignación exitosa:', {
          persona: `${data.persona.nombre} ${data.persona.apellido}`,
          tipo: data.persona.tipo_cliente,
          edad: data.persona.edad,
          isNew: data.is_new_assignment
        });
        
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
   * Refresca la persona (fuerza nueva asignación)
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
      
      const newPersona = await assignPersona(newSessionId);
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

        // 3. Si no hay cache válido, solicitar del servidor
        console.log('[Persona] Cache no disponible, solicitando del servidor...');
        const assignedPersona = await assignPersona(currentSessionId);
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
  }, [getOrCreateSessionId, getPersonaFromCache, assignPersona]);

  return {
    persona,
    sessionId,
    isLoading,
    error,
    refreshPersona,
    clearPersona
  };
}

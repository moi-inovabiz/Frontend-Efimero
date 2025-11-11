/**
 * Componente para seleccionar manualmente una persona simulada
 * Útil para demos y testing de diferentes perfiles
 */

'use client';

import React, { useState, useEffect } from 'react';
import { PersonaSimulada } from '@/types/persona';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface PersonaSelectorProps {
  onPersonaChange: (personaId: string) => Promise<void>;
  currentPersonaId?: string;
}

export function PersonaSelector({ onPersonaChange, currentPersonaId }: PersonaSelectorProps) {
  const [personas, setPersonas] = useState<PersonaSimulada[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Cargar lista de personas
  useEffect(() => {
    const fetchPersonas = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/personas/list?limit=100`);
        if (!response.ok) throw new Error('Error cargando personas');
        
        const data = await response.json();
        setPersonas(data.personas);
      } catch (err) {
        console.error('[PersonaSelector] Error:', err);
        setError('No se pudieron cargar las personas');
      }
    };

    fetchPersonas();
  }, []);

  const handleSelectPersona = async (personaId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await onPersonaChange(personaId);
      setIsOpen(false);
    } catch (err) {
      console.error('[PersonaSelector] Error al cambiar persona:', err);
      setError('Error al cambiar persona');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 left-6 z-50 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-6 py-3 rounded-full shadow-2xl transition-all transform hover:scale-105 flex items-center gap-2 font-semibold"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        Cambiar Perfil
      </button>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden border border-gray-700">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white mb-1">
                Seleccionar Perfil
              </h2>
              <p className="text-purple-100 text-sm">
                Elige un perfil para ver cómo se adapta la interfaz
              </p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(80vh-140px)]">
          {error && (
            <div className="bg-red-900/30 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {personas.map((persona) => (
              <button
                key={persona.id}
                onClick={() => handleSelectPersona(persona.id)}
                disabled={isLoading || persona.id === currentPersonaId}
                className={`
                  text-left p-4 rounded-xl border-2 transition-all
                  ${persona.id === currentPersonaId
                    ? 'border-purple-500 bg-purple-900/30'
                    : 'border-gray-700 bg-gray-800/50 hover:border-purple-500/50 hover:bg-gray-800'
                  }
                  ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                `}
              >
                <div className="flex items-start gap-3">
                  {/* Icon */}
                  <div className="text-3xl">
                    {persona.tipo_cliente === 'empresa' ? '🏢' : '👤'}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-lg font-bold text-white truncate">
                        {persona.nombre} {persona.apellido}
                      </h3>
                      {persona.id === currentPersonaId && (
                        <span className="bg-purple-500 text-white text-xs px-2 py-0.5 rounded-full">
                          Actual
                        </span>
                      )}
                    </div>

                    {/* Metadata */}
                    <div className="grid grid-cols-2 gap-2 text-sm mb-2">
                      <div className="text-gray-400">
                        <span className="text-gray-500">Tipo:</span>{' '}
                        <span className="text-white">
                          {persona.tipo_cliente === 'empresa' ? 'Empresa' : 'Persona'}
                        </span>
                      </div>
                      <div className="text-gray-400">
                        <span className="text-gray-500">Edad:</span>{' '}
                        <span className="text-white">{persona.edad} años</span>
                      </div>
                      <div className="text-gray-400">
                        <span className="text-gray-500">Región:</span>{' '}
                        <span className="text-white">{persona.region}</span>
                      </div>
                      {persona.tipo_cliente === 'empresa' && persona.tamano_flota && (
                        <div className="text-gray-400">
                          <span className="text-gray-500">Flota:</span>{' '}
                          <span className="text-white">{persona.tamano_flota} veh.</span>
                        </div>
                      )}
                    </div>

                    {/* Visual preferences badges */}
                    <div className="flex flex-wrap gap-1">
                      {persona.densidad_informacion && (
                        <span className="bg-cyan-900/30 text-cyan-300 text-xs px-2 py-0.5 rounded border border-cyan-500/30">
                          {persona.densidad_informacion}
                        </span>
                      )}
                      {persona.nivel_animaciones && (
                        <span className="bg-purple-900/30 text-purple-300 text-xs px-2 py-0.5 rounded border border-purple-500/30">
                          {persona.nivel_animaciones}
                        </span>
                      )}
                      {persona.color_favorito && (
                        <span
                          className="text-xs px-2 py-0.5 rounded border border-white/20"
                          style={{
                            backgroundColor: persona.color_favorito + '30',
                            color: persona.color_favorito,
                          }}
                        >
                          color
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-800/50 border-t border-gray-700 p-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">
              {personas.length} perfiles disponibles
            </span>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Componente para mostrar información de la Persona Simulada asignada
 * Útil para debugging y demostración
 * Ahora con matching inteligente basado en contexto
 */

'use client';

import React from 'react';
import { usePersona } from '@/hooks/usePersona';
import { useEphemeralContext } from '@/hooks/useEphemeralContext';

interface PersonaDebugPanelProps {
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  collapsed?: boolean;
}

export function PersonaDebugPanel({ 
  position = 'bottom-right',
  collapsed = false
}: PersonaDebugPanelProps) {
  const context = useEphemeralContext();
  const { persona, isLoading, error, refreshPersonaWithContext } = usePersona(context);
  const [isOpen, setIsOpen] = React.useState(!collapsed);

  const handleRefresh = React.useCallback(async () => {
    await refreshPersonaWithContext(context);
  }, [refreshPersonaWithContext, context]);

  if (isLoading) {
    return (
      <div className={`fixed ${getPositionClasses(position)} z-50 bg-gray-800 text-white p-4 rounded-lg shadow-xl`}>
        <div className="flex items-center gap-2">
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
          <span>Cargando persona...</span>
        </div>
      </div>
    );
  }

  if (!persona) {
    return (
      <div className={`fixed ${getPositionClasses(position)} z-50 bg-red-900 text-white p-4 rounded-lg shadow-xl`}>
        <div className="font-bold">⚠️ No hay persona asignada</div>
      </div>
    );
  }

  return (
    <div className={`fixed ${getPositionClasses(position)} z-50`}>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="mb-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg shadow-lg transition-all flex items-center gap-2"
      >
        <span className="text-xl">👤</span>
        <span className="font-semibold">
          {isOpen ? 'Ocultar' : 'Ver'} Persona
        </span>
      </button>

      {/* Panel Content */}
      {isOpen && (
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 text-white p-6 rounded-lg shadow-2xl max-w-md border border-cyan-500">
          {/* Header */}
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-700">
            <h3 className="text-xl font-bold flex items-center gap-2">
              <span className="text-2xl">👤</span>
              Persona Simulada
            </h3>
            <button
              onClick={handleRefresh}
              className="text-cyan-400 hover:text-cyan-300 transition-colors"
              title="Cambiar persona con matching inteligente"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>

          {/* Basic Info */}
          <div className="space-y-3">
            <div>
              <div className="text-2xl font-bold text-cyan-400">
                {persona.nombre} {persona.apellido}
              </div>
              <div className="text-sm text-gray-400">
                {persona.descripcion}
              </div>
            </div>

            {/* Demographics */}
            <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-700">
              <InfoItem
                icon="🎂"
                label="Edad"
                value={`${persona.edad} años`}
              />
              <InfoItem
                icon="📍"
                label="Región"
                value={persona.region}
              />
              <InfoItem
                icon={persona.tipo_cliente === 'empresa' ? '🏢' : '👨‍💼'}
                label="Tipo"
                value={persona.tipo_cliente === 'empresa' ? 'Empresa' : 'Persona'}
              />
              {persona.tipo_cliente === 'empresa' && persona.tamano_flota && (
                <InfoItem
                  icon="🚗"
                  label="Flota"
                  value={`${persona.tamano_flota} veh.`}
                />
              )}
            </div>

            {/* Interests */}
            <div className="pt-3 border-t border-gray-700">
              <div className="text-xs font-semibold text-gray-400 mb-2">INTERESES</div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {persona.interes_principal && (
                  <div className="bg-gray-700 px-2 py-1 rounded">
                    <span className="text-gray-400">Interés:</span>{' '}
                    <span className="text-white">{persona.interes_principal}</span>
                  </div>
                )}
                {persona.presupuesto && (
                  <div className="bg-gray-700 px-2 py-1 rounded">
                    <span className="text-gray-400">Presupuesto:</span>{' '}
                    <span className="text-white">{persona.presupuesto}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Visual Preferences */}
            <div className="pt-3 border-t border-gray-700">
              <div className="text-xs font-semibold text-gray-400 mb-2">PREFERENCIAS VISUALES</div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {persona.densidad_informacion && (
                  <PreferenceTag
                    label="Densidad"
                    value={persona.densidad_informacion}
                  />
                )}
                {persona.estilo_tipografia && (
                  <PreferenceTag
                    label="Tipografía"
                    value={persona.estilo_tipografia}
                  />
                )}
                {persona.nivel_animaciones && (
                  <PreferenceTag
                    label="Animaciones"
                    value={persona.nivel_animaciones}
                  />
                )}
                {persona.preferencia_layout && (
                  <PreferenceTag
                    label="Layout"
                    value={persona.preferencia_layout}
                  />
                )}
              </div>
            </div>

            {/* Color Preference */}
            {persona.color_favorito && (
              <div className="pt-3 border-t border-gray-700 flex items-center justify-between">
                <span className="text-sm text-gray-400">Color favorito:</span>
                <div className="flex items-center gap-2">
                  <div 
                    className="w-8 h-8 rounded border-2 border-white/20"
                    style={{ backgroundColor: persona.color_favorito }}
                  />
                  <span className="text-xs text-gray-400 font-mono">
                    {persona.color_favorito}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="mt-4 pt-3 border-t border-gray-700 text-xs text-gray-500 text-center">
            Esta persona se mantendrá durante tu navegación
          </div>
        </div>
      )}
    </div>
  );
}

// Helper Components
function InfoItem({ icon, label, value }: { icon: string; label: string; value: string }) {
  return (
    <div className="bg-gray-700/50 px-3 py-2 rounded">
      <div className="text-xs text-gray-400 mb-1">
        <span className="mr-1">{icon}</span>
        {label}
      </div>
      <div className="text-sm font-semibold text-white">{value}</div>
    </div>
  );
}

function PreferenceTag({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-cyan-900/30 border border-cyan-500/30 px-2 py-1 rounded">
      <div className="text-gray-400">{label}</div>
      <div className="text-cyan-300 font-semibold">{value}</div>
    </div>
  );
}

function getPositionClasses(position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'): string {
  const positions = {
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4'
  };
  return positions[position];
}

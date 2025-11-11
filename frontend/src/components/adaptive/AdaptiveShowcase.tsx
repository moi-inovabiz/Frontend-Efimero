/**
 * Componente para mostrar visualmente las adaptaciones dinámicas
 * basadas en la persona asignada
 */

'use client';

import React from 'react';
import { useAdaptiveUI } from './AdaptiveUIProvider';

export function AdaptiveShowcase() {
  const { persona } = useAdaptiveUI();

  if (!persona) {
    return (
      <div className="bg-gray-100 p-6 rounded-lg">
        <p className="text-gray-500">No hay persona asignada</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white p-6 rounded-lg">
        <h2 className="text-2xl font-bold mb-2">
          🎨 Adaptaciones Dinámicas Activas
        </h2>
        <p className="text-cyan-100">
          Basadas en: {persona.nombre} {persona.apellido}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Card 1: Font Size por Edad */}
        <AdaptiveCard
          title="📝 Tamaño de Fuente"
          icon="👴"
          criterion="Edad"
          value={`${persona.edad} años`}
          adaptation={
            persona.edad < 40
              ? '16px - Tamaño estándar para jóvenes'
              : persona.edad < 60
              ? '18px - Aumentado para adultos'
              : '20px - Maximizado para mayores'
          }
          cssVar="--adaptive-font-size-base"
        >
          <p style={{ fontSize: 'var(--adaptive-font-size-base)' }}>
            Este texto se adapta automáticamente según la edad del usuario.
          </p>
        </AdaptiveCard>

        {/* Card 2: Color por Tipo Cliente */}
        <AdaptiveCard
          title="🎨 Color Primario"
          icon={persona.tipo_cliente === 'empresa' ? '🏢' : '👨‍💼'}
          criterion="Tipo de Cliente"
          value={persona.tipo_cliente === 'empresa' ? 'Empresa' : 'Persona'}
          adaptation={
            persona.tipo_cliente === 'empresa'
              ? 'Azul profesional (#3B82F6)'
              : `Color favorito: ${persona.color_favorito || '#06B6D4'}`
          }
          cssVar="--adaptive-primary-color"
        >
          <div
            className="h-16 rounded-lg flex items-center justify-center text-white font-bold"
            style={{ backgroundColor: 'var(--adaptive-primary-color)' }}
          >
            Color Adaptativo
          </div>
        </AdaptiveCard>

        {/* Card 3: Velocidad Animaciones */}
        <AdaptiveCard
          title="⚡ Velocidad de Animaciones"
          icon="🎬"
          criterion="Nivel de Animaciones"
          value={persona.nivel_animaciones || 'medio'}
          adaptation={
            persona.nivel_animaciones === 'bajo'
              ? '0.1s - Rápidas y discretas'
              : persona.nivel_animaciones === 'medio'
              ? '0.3s - Balance perfecto'
              : '0.5s - Suaves y fluidas'
          }
          cssVar="--adaptive-animation-duration"
        >
          <div className="flex gap-4">
            <div
              className="w-12 h-12 bg-cyan-500 rounded-lg animate-pulse"
              style={{
                animationDuration: 'var(--adaptive-animation-duration)',
              }}
            />
            <div
              className="w-12 h-12 bg-blue-500 rounded-lg animate-bounce"
              style={{
                animationDuration: 'calc(var(--adaptive-animation-duration) * 2)',
              }}
            />
            <div
              className="w-12 h-12 bg-purple-500 rounded-lg animate-spin"
              style={{
                animationDuration: 'calc(var(--adaptive-animation-duration) * 3)',
              }}
            />
          </div>
        </AdaptiveCard>

        {/* Card 4: Espaciado por Densidad */}
        <AdaptiveCard
          title="📏 Espaciado"
          icon="📐"
          criterion="Densidad de Información"
          value={persona.densidad_informacion || 'comoda'}
          adaptation={
            persona.densidad_informacion === 'compacta'
              ? '0.75rem - Máxima densidad'
              : persona.densidad_informacion === 'comoda'
              ? '1rem - Espaciado estándar'
              : '1.5rem - Espacioso y relajado'
          }
          cssVar="--adaptive-spacing-unit"
        >
          <div
            className="space-y-2"
            style={{
              gap: 'var(--adaptive-spacing-unit)',
            }}
          >
            <div className="bg-gray-200 h-8 rounded" />
            <div className="bg-gray-200 h-8 rounded" />
            <div className="bg-gray-200 h-8 rounded" />
          </div>
        </AdaptiveCard>

        {/* Card 5: Border Radius por Layout */}
        <AdaptiveCard
          title="🔲 Bordes Redondeados"
          icon="🎯"
          criterion="Preferencia de Layout"
          value={persona.preferencia_layout || 'cards'}
          adaptation={
            persona.preferencia_layout === 'minimalista'
              ? '0.25rem - Líneas rectas'
              : persona.preferencia_layout === 'cards'
              ? '0.75rem - Redondeado amigable'
              : '0.5rem - Balance moderno'
          }
          cssVar="--adaptive-border-radius"
        >
          <div className="grid grid-cols-3 gap-4">
            <div
              className="h-16 bg-gradient-to-br from-cyan-400 to-cyan-600"
              style={{ borderRadius: 'var(--adaptive-border-radius)' }}
            />
            <div
              className="h-16 bg-gradient-to-br from-blue-400 to-blue-600"
              style={{ borderRadius: 'var(--adaptive-border-radius)' }}
            />
            <div
              className="h-16 bg-gradient-to-br from-purple-400 to-purple-600"
              style={{ borderRadius: 'var(--adaptive-border-radius)' }}
            />
          </div>
        </AdaptiveCard>

        {/* Card 6: Resumen Completo */}
        <div className="md:col-span-2 bg-gradient-to-br from-gray-800 to-gray-900 text-white p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <span>🎯</span>
            Resumen de Adaptaciones
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            <StatItem label="Font Size" value={getCSSVar('--adaptive-font-size-base')} />
            <StatItem
              label="Color Primario"
              value={getCSSVar('--adaptive-primary-color')}
            />
            <StatItem
              label="Animación"
              value={getCSSVar('--adaptive-animation-duration')}
            />
            <StatItem
              label="Espaciado"
              value={getCSSVar('--adaptive-spacing-unit')}
            />
            <StatItem
              label="Border Radius"
              value={getCSSVar('--adaptive-border-radius')}
            />
            <StatItem label="Edad Persona" value={`${persona.edad} años`} />
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper Components
interface AdaptiveCardProps {
  title: string;
  icon: string;
  criterion: string;
  value: string;
  adaptation: string;
  cssVar: string;
  children: React.ReactNode;
}

function AdaptiveCard({
  title,
  icon,
  criterion,
  value,
  adaptation,
  cssVar,
  children,
}: AdaptiveCardProps) {
  return (
    <div className="bg-white border-2 border-gray-200 rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-3xl">{icon}</span>
        <h3 className="text-lg font-bold text-gray-800">{title}</h3>
      </div>

      <div className="space-y-3 mb-4">
        <div>
          <span className="text-xs font-semibold text-gray-500 uppercase">
            {criterion}
          </span>
          <p className="text-sm font-bold text-gray-800">{value}</p>
        </div>

        <div>
          <span className="text-xs font-semibold text-gray-500 uppercase">
            Adaptación Aplicada
          </span>
          <p className="text-sm text-gray-700">{adaptation}</p>
        </div>

        <div>
          <span className="text-xs font-semibold text-gray-500 uppercase font-mono">
            CSS Variable
          </span>
          <p className="text-xs text-cyan-600 font-mono bg-gray-100 px-2 py-1 rounded">
            {cssVar}
          </p>
        </div>
      </div>

      <div className="pt-4 border-t border-gray-200">
        <span className="text-xs font-semibold text-gray-500 uppercase mb-2 block">
          Vista Previa
        </span>
        {children}
      </div>
    </div>
  );
}

function StatItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-700 px-3 py-2 rounded">
      <div className="text-xs text-gray-400">{label}</div>
      <div className="text-sm font-bold text-cyan-400 font-mono">{value}</div>
    </div>
  );
}

function getCSSVar(varName: string): string {
  if (typeof window === 'undefined') return 'N/A';
  return getComputedStyle(document.documentElement)
    .getPropertyValue(varName)
    .trim();
}

/**
 * Demo Page - Personalización Adaptativa
 * Muestra elementos UI que se adaptan según la persona simulada
 * Ahora con adaptaciones dinámicas visuales y selector de perfiles
 */

'use client';

import { AdaptiveUIProvider, useAdaptiveUI } from '@/components/adaptive/AdaptiveUIProvider';
import { AdaptiveShowcase } from '@/components/adaptive/AdaptiveShowcase';
import { PersonaDebugPanel } from '@/components/persona/PersonaDebugPanel';
import { PersonaSelector } from '@/components/persona/PersonaSelector';
import Link from 'next/link';

function DemoContent() {
  const { designTokens, persona, isLoading, assignSpecificPersona } = useAdaptiveUI();

  if (isLoading || !persona) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-black">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-cyan-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Cargando personalización...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black p-8">
      {/* Persona Debug Panel */}
      <PersonaDebugPanel position="top-right" collapsed={false} />
      
      {/* Selector de Personas */}
      <PersonaSelector
        onPersonaChange={assignSpecificPersona}
        currentPersonaId={persona.id}
      />
      
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-12 text-center">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-4">
            Demo de Personalización Adaptativa
          </h1>
          <p className="text-xl text-gray-400 mb-4">
            Esta página se adapta automáticamente según tu Persona Simulada
          </p>
          
          {/* NUEVO: Botón Frontend Efímero */}
          <div className="my-8">
            <Link 
              href="/efimero"
              className="group relative inline-flex items-center gap-3 px-8 py-6 bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 rounded-2xl text-white font-bold text-2xl shadow-2xl hover:shadow-purple-500/50 transition-all duration-300 hover:scale-105 overflow-hidden"
            >
              {/* Efecto de brillo animado */}
              <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></span>
              
              {/* Icono */}
              <span className="text-4xl animate-pulse">🎨</span>
              
              {/* Texto */}
              <span className="relative z-10">
                Frontend Efímero Personalizado
              </span>
              
              {/* Badge "NEW" */}
              <span className="relative z-10 px-3 py-1 bg-yellow-400 text-black text-xs font-black rounded-full uppercase animate-bounce">
                AI Powered
              </span>
              
              {/* Flecha */}
              <svg className="relative z-10 w-6 h-6 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
            
            <p className="mt-4 text-sm text-gray-500 max-w-2xl mx-auto">
              Experimenta con el frontend <span className="text-purple-400 font-semibold">completamente generado por Gemini AI + Canva</span> basado en tu contexto único. Sin afectar el sistema actual.
            </p>
          </div>
          
          <Link 
            href="/" 
            className="inline-flex items-center gap-2 text-cyan-400 hover:text-cyan-300 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver al inicio
          </Link>
        </div>

        {/* Nuevo componente de Adaptaciones Dinámicas */}
        <div className="mb-12">
          <AdaptiveShowcase />
        </div>

        {/* Separador */}
        <div className="my-12 border-t border-gray-700"></div>

        {/* Tokens aplicados */}
        <div className="mb-8 bg-gray-800/50 backdrop-blur-sm border border-cyan-500/30 rounded-xl p-6">
          <h2 className="text-2xl font-bold text-cyan-400 mb-4 flex items-center gap-2">
            <span>🎨</span>
            Tokens de Diseño Aplicados
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Clases CSS:</h3>
              <div className="flex flex-wrap gap-2">
                {designTokens?.css_classes.map((cls, idx) => (
                  <span 
                    key={idx}
                    className="px-3 py-1 bg-cyan-900/30 text-cyan-300 rounded-full text-sm font-mono border border-cyan-500/30"
                  >
                    {cls}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Variables CSS:</h3>
              <div className="space-y-1 text-sm font-mono text-gray-300">
                {Object.entries(designTokens?.css_variables || {}).slice(0, 3).map(([key, value]) => (
                  <div key={key}>
                    <span className="text-cyan-400">{key}</span>: <span className="text-yellow-400">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Grid de elementos adaptativos */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card 1: Densidad de información */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-cyan-500/50 transition-all">
            <div className="text-3xl mb-3">📊</div>
            <h3 className="text-xl font-bold text-white mb-2">Densidad de Información</h3>
            <p className="text-gray-400 mb-4">
              {persona.densidad_informacion === 'compacta' && 'Mostrando información compacta para aprovechamiento máximo del espacio'}
              {persona.densidad_informacion === 'comoda' && 'Mostrando información con espaciado cómodo para fácil lectura'}
              {persona.densidad_informacion === 'amplia' && 'Mostrando información con espaciado amplio para máxima claridad'}
            </p>
            <div className="bg-cyan-900/20 border border-cyan-500/30 rounded-lg p-3">
              <div className="text-cyan-300 font-semibold">Configuración actual:</div>
              <div className="text-white text-lg">{persona.densidad_informacion}</div>
            </div>
          </div>

          {/* Card 2: Tipografía */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-cyan-500/50 transition-all">
            <div className="text-3xl mb-3">🔤</div>
            <h3 className="text-xl font-bold text-white mb-2">Estilo Tipográfico</h3>
            <p className="text-gray-400 mb-4">
              {persona.estilo_tipografia === 'moderna_geometrica' && 'Fuentes modernas y geométricas para estética contemporánea'}
              {persona.estilo_tipografia === 'clasica_serif' && 'Fuentes clásicas con serifas para elegancia tradicional'}
              {persona.estilo_tipografia === 'sans-serif' && 'Fuentes sans-serif para claridad y simplicidad'}
            </p>
            <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-3">
              <div className="text-purple-300 font-semibold">Configuración actual:</div>
              <div className="text-white text-lg">{persona.estilo_tipografia}</div>
            </div>
          </div>

          {/* Card 3: Animaciones */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-cyan-500/50 transition-all">
            <div className="text-3xl mb-3">✨</div>
            <h3 className="text-xl font-bold text-white mb-2">Nivel de Animaciones</h3>
            <p className="text-gray-400 mb-4">
              {persona.nivel_animaciones === 'bajo' && 'Animaciones mínimas para mejor rendimiento'}
              {persona.nivel_animaciones === 'medio' && 'Animaciones moderadas para equilibrio perfecto'}
              {persona.nivel_animaciones === 'alto' && 'Animaciones fluidas para experiencia rica'}
            </p>
            <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-3">
              <div className="text-green-300 font-semibold">Configuración actual:</div>
              <div className="text-white text-lg">{persona.nivel_animaciones}</div>
            </div>
          </div>

          {/* Card 4: Layout */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-cyan-500/50 transition-all">
            <div className="text-3xl mb-3">📐</div>
            <h3 className="text-xl font-bold text-white mb-2">Preferencia de Layout</h3>
            <p className="text-gray-400 mb-4">
              {persona.preferencia_layout === 'grid' && 'Diseño en cuadrícula para organización visual clara'}
              {persona.preferencia_layout === 'lista' && 'Diseño en lista para flujo de lectura lineal'}
              {persona.preferencia_layout === 'cards' && 'Diseño en tarjetas para contenido modular'}
            </p>
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3">
              <div className="text-blue-300 font-semibold">Configuración actual:</div>
              <div className="text-white text-lg">{persona.preferencia_layout}</div>
            </div>
          </div>

          {/* Card 5: Esquema de colores */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-cyan-500/50 transition-all">
            <div className="text-3xl mb-3">🎨</div>
            <h3 className="text-xl font-bold text-white mb-2">Esquema de Colores</h3>
            <p className="text-gray-400 mb-4">
              Tema aplicado según preferencias y contexto del usuario
            </p>
            <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-3">
              <div className="text-yellow-300 font-semibold">Configuración actual:</div>
              <div className="text-white text-lg">{persona.esquema_colores}</div>
              {persona.color_favorito && (
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-sm text-gray-400">Color favorito:</span>
                  <div 
                    className="w-8 h-8 rounded border-2 border-white/30"
                    style={{ backgroundColor: persona.color_favorito }}
                  />
                  <span className="text-xs font-mono text-gray-500">{persona.color_favorito}</span>
                </div>
              )}
            </div>
          </div>

          {/* Card 6: Perfil de usuario */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-cyan-500/50 transition-all">
            <div className="text-3xl mb-3">
              {persona.tipo_cliente === 'empresa' ? '🏢' : '👤'}
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Perfil del Usuario</h3>
            <p className="text-gray-400 mb-4">
              {persona.tipo_cliente === 'empresa' 
                ? `Empresa con ${persona.tamano_flota || 0} vehículos en flota`
                : `Persona individual de ${persona.edad} años`}
            </p>
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3 space-y-2">
              <div>
                <span className="text-red-300 font-semibold">Tipo:</span>
                <span className="text-white ml-2">{persona.tipo_cliente}</span>
              </div>
              <div>
                <span className="text-red-300 font-semibold">Región:</span>
                <span className="text-white ml-2">{persona.region}</span>
              </div>
              <div>
                <span className="text-red-300 font-semibold">Interés:</span>
                <span className="text-white ml-2">{persona.interes_principal}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Botón de acción adaptativo */}
        <div className="mt-12 text-center">
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-8 inline-block">
            <h2 className="text-2xl font-bold text-white mb-4">
              Botón Adaptativo de Ejemplo
            </h2>
            <p className="text-gray-400 mb-6 max-w-md">
              Este botón usa el color favorito de tu persona simulada ({persona.color_favorito})
            </p>
            <button
              className="px-8 py-4 rounded-lg font-semibold text-white shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
              style={{ 
                backgroundColor: persona.color_favorito || '#06B6D4',
                boxShadow: `0 4px 14px 0 ${persona.color_favorito || '#06B6D4'}40`
              }}
            >
              {persona.tipo_cliente === 'empresa' ? 'Ver Catálogo Empresarial' : 'Ver Vehículos Disponibles'}
            </button>
          </div>
        </div>

        {/* Footer instructivo */}
        <div className="mt-12 bg-cyan-900/20 border border-cyan-500/30 rounded-xl p-6">
          <h3 className="text-xl font-bold text-cyan-400 mb-3 flex items-center gap-2">
            <span>💡</span>
            Cómo funciona
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-300">
            <div>
              <strong className="text-white">1. Asignación automática:</strong>
              <p className="text-sm mt-1">
                Al cargar la página, se te asigna una "Persona Simulada" con características demográficas y preferencias únicas.
              </p>
            </div>
            <div>
              <strong className="text-white">2. Predicción ML:</strong>
              <p className="text-sm mt-1">
                Los modelos XGBoost analizan 53 campos de contexto para predecir el diseño óptimo.
              </p>
            </div>
            <div>
              <strong className="text-white">3. Tokens CSS:</strong>
              <p className="text-sm mt-1">
                Las predicciones se convierten en clases y variables CSS que se inyectan dinámicamente.
              </p>
            </div>
            <div>
              <strong className="text-white">4. Persistencia:</strong>
              <p className="text-sm mt-1">
                Tu persona se guarda 24h. Usa el botón 🔄 del panel para cambiar y ver diferentes estilos.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DemoPage() {
  return (
    <AdaptiveUIProvider>
      <DemoContent />
    </AdaptiveUIProvider>
  );
}

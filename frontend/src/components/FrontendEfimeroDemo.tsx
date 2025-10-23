/**
 * Demo principal del Frontend Efímero
 * Adaptado de CarShowcase para mostrar UI adaptativa en acción
 */

'use client';

import { Brain, Zap, Target, Gauge, Shield, Smartphone } from 'lucide-react';
import { AdaptiveButton, AdaptiveCard, AdaptiveText } from './adaptive/AdaptiveComponents';
import { useAdaptiveUI } from './adaptive/AdaptiveUIProvider';

export function FrontendEfimeroDemo() {
  const { designTokens, isLoading, error } = useAdaptiveUI();

  const features = [
    { 
      icon: Brain, 
      label: 'XGBoost Dual Prediction',
      description: 'Classifier + Regressor para tokens precisos'
    },
    { 
      icon: Zap, 
      label: 'Zero Flicker Technology',
      description: 'Inyección CSS antes del renderizado'
    },
    { 
      icon: Target, 
      label: 'Adaptación Profunda',
      description: 'Valores continuos, no solo binarios'
    },
    { 
      icon: Gauge, 
      label: 'Inferencia < 100ms',
      description: 'Modelos en memoria RAM'
    },
    { 
      icon: Shield, 
      label: 'Privacy First',
      description: 'JWT + cookies primera parte'
    },
    { 
      icon: Smartphone, 
      label: 'Contexto Multifuente',
      description: 'JS + HTTP + Firestore + Social'
    },
  ];

  return (
    <div
      className="min-h-screen p-8"
      style={{
        background: 'linear-gradient(to bottom, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%)',
        color: '#ffffff',
      }}
    >
      <div className="max-w-7xl mx-auto">
        
        {/* Header adaptativo */}
        <header className="text-center mb-12">
          <h1
            className="text-4xl md:text-6xl font-bold mb-4"
            style={{
              background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              letterSpacing: '0.02em',
              fontSize: 'var(--font-size-base, 1rem)',
              transform: 'scale(3.5)',
              transformOrigin: 'center',
            }}
          >
            Frontend Efímero
          </h1>
          <AdaptiveText size="lg" className="text-cyan-400 font-semibold mb-4">
            Sistema de Adaptación Predictiva Profunda de UI
          </AdaptiveText>
          <AdaptiveText className="text-gray-400 max-w-2xl mx-auto">
            Esta interfaz se adapta automáticamente usando Machine Learning. 
            Los espaciados, tipografías y colores que ves fueron predichos por XGBoost 
            basándose en tu contexto actual.
          </AdaptiveText>
        </header>

        {/* Estado del sistema */}
        <div className="mb-12">
          <AdaptiveCard title="Estado del Sistema" className="bg-gray-900/50 border-gray-700">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className={`w-4 h-4 rounded-full mx-auto mb-2 ${
                  isLoading ? 'bg-yellow-400 animate-pulse' : 
                  error ? 'bg-red-400' : 'bg-green-400'
                }`} />
                <AdaptiveText size="sm" className="font-semibold">
                  {isLoading ? 'Prediciendo...' : error ? 'Error' : 'Activo'}
                </AdaptiveText>
              </div>
              <div className="text-center">
                <AdaptiveText size="sm" className="text-cyan-400 font-mono">
                  {designTokens ? Object.keys(designTokens.css_variables).length : 0}
                </AdaptiveText>
                <AdaptiveText size="sm">Variables CSS</AdaptiveText>
              </div>
              <div className="text-center">
                <AdaptiveText size="sm" className="text-purple-400 font-mono">
                  {designTokens ? designTokens.css_classes.length : 0}
                </AdaptiveText>
                <AdaptiveText size="sm">Clases Aplicadas</AdaptiveText>
              </div>
            </div>
          </AdaptiveCard>
        </div>

        {/* Imagen hero */}
        <div
          className="w-full max-w-5xl mx-auto mb-12 rounded-3xl overflow-hidden"
          style={{
            boxShadow: '0 20px 60px rgba(6, 182, 212, 0.3)',
          }}
        >
          <img
            src="https://images.unsplash.com/photo-1555949963-aa79dcee981c?auto=format&fit=crop&w=1200&q=80"
            alt="AI-Powered UI Adaptation Visualization"
            className="w-full h-auto"
          />
        </div>

        {/* Grid de características adaptativas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {features.map((feature, index) => (
            <AdaptiveCard key={index} className="bg-gray-900/30 border-gray-700 hover:border-cyan-500 transition-all duration-300 cursor-pointer group">
              <div className="flex items-start gap-4">
                <div 
                  className="p-3 rounded-lg group-hover:scale-110 transition-transform duration-300"
                  style={{ backgroundColor: 'rgba(6, 182, 212, 0.2)' }}
                >
                  <feature.icon size={24} className="text-cyan-400" />
                </div>
                <div className="flex-1">
                  <AdaptiveText className="font-semibold text-white mb-2">
                    {feature.label}
                  </AdaptiveText>
                  <AdaptiveText size="sm" className="text-gray-400">
                    {feature.description}
                  </AdaptiveText>
                </div>
              </div>
            </AdaptiveCard>
          ))}
        </div>

        {/* Tokens debug (solo visible si hay tokens) */}
        {designTokens && (
          <div className="mb-12">
            <AdaptiveCard title="Tokens CSS Aplicados" className="bg-purple-900/20 border-purple-700">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-purple-400 font-semibold mb-3">Clases CSS (Classifier)</h4>
                  <div className="space-y-2">
                    {designTokens.css_classes.map((cls, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-purple-400 rounded-full" />
                        <AdaptiveText size="sm" className="font-mono text-purple-300">
                          {cls}
                        </AdaptiveText>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-cyan-400 font-semibold mb-3">Variables CSS (Regressor)</h4>
                  <div className="space-y-2">
                    {Object.entries(designTokens.css_variables).map(([key, value], index) => (
                      <div key={index} className="flex items-center justify-between gap-2">
                        <AdaptiveText size="sm" className="font-mono text-cyan-300">
                          {key}
                        </AdaptiveText>
                        <AdaptiveText size="sm" className="font-mono text-cyan-100">
                          {value}
                        </AdaptiveText>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </AdaptiveCard>
          </div>
        )}

        {/* Call to action */}
        <div className="text-center mb-8">
          <AdaptiveButton 
            variant="primary" 
            className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold py-4 px-8 text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300"
          >
            Generar Nuevo Diseño Adaptativo
          </AdaptiveButton>
          <AdaptiveText size="sm" className="text-gray-500 mt-4">
            Cada clic genera una nueva predicción personalizada
          </AdaptiveText>
        </div>

        {/* Footer */}
        <footer className="mt-16 pt-8 border-t border-gray-700 text-center">
          <AdaptiveText size="sm" className="text-gray-400">
            © 2025 Frontend Efímero. Powered by XGBoost + Next.js + FastAPI
          </AdaptiveText>
          <AdaptiveText size="sm" className="text-gray-600 mt-2">
            Sistema de Adaptación Predictiva Profunda de UI
          </AdaptiveText>
        </footer>
      </div>
    </div>
  );
}
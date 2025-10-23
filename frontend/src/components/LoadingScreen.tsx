/**
 * Pantalla de carga para el Frontend Efímero
 * Adaptada de la maqueta Bolt con branding del Sistema de Adaptación Predictiva
 */

'use client';

import { useEffect, useState } from 'react';

interface LoadingScreenProps {
  onLoadingComplete: () => void;
}

export function LoadingScreen({ onLoadingComplete }: LoadingScreenProps) {
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState(1);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(onLoadingComplete, 500);
          return 100;
        }
        
        // Actualizar fase según progreso
        const newProgress = prev + 1.5;
        if (newProgress >= 25 && phase === 1) setPhase(2);
        if (newProgress >= 70 && phase === 2) setPhase(3);
        
        return newProgress;
      });
    }, 40);

    return () => clearInterval(interval);
  }, [onLoadingComplete, phase]);

  const getPhaseText = () => {
    switch (phase) {
      case 1: return 'Capturando contexto del usuario...';
      case 2: return 'Ejecutando predicción XGBoost...';
      case 3: return 'Inyectando tokens de diseño...';
      default: return 'Listo para Frontend Efímero';
    }
  };

  const getPhaseColor = () => {
    switch (phase) {
      case 1: return '#3b82f6'; // blue
      case 2: return '#10b981'; // green  
      case 3: return '#8b5cf6'; // purple
      default: return '#06b6d4'; // cyan
    }
  };

  return (
    <div
      className="fixed inset-0 flex flex-col items-center justify-center"
      style={{
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%)',
        color: '#ffffff',
      }}
    >
      <div className="text-center max-w-2xl px-8">
        {/* Logo/Brand */}
        <div className="mb-8">
          <h1
            className="text-5xl md:text-6xl font-bold mb-4"
            style={{
              background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              letterSpacing: '0.02em',
            }}
          >
            Frontend Efímero
          </h1>
          <p
            className="text-xl md:text-2xl mb-2"
            style={{ color: '#a0a0a0' }}
          >
            Sistema de Adaptación Predictiva Profunda
          </p>
          <p
            className="text-sm md:text-base"
            style={{ color: '#666' }}
          >
            Powered by XGBoost • Zero Flicker Technology
          </p>
        </div>

        {/* Fase actual */}
        <div className="mb-8">
          <div 
            className="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold mb-4"
            style={{ 
              backgroundColor: `${getPhaseColor()}20`,
              color: getPhaseColor(),
              border: `1px solid ${getPhaseColor()}40`
            }}
          >
            FASE {phase}/3
          </div>
          <p
            className="text-lg"
            style={{ color: getPhaseColor() }}
          >
            {getPhaseText()}
          </p>
        </div>

        {/* Barra de progreso */}
        <div className="mb-6">
          <div
            className="w-full h-2 rounded-full overflow-hidden"
            style={{ backgroundColor: '#333' }}
          >
            <div
              className="h-full transition-all duration-300 ease-out"
              style={{
                width: `${progress}%`,
                background: `linear-gradient(90deg, ${getPhaseColor()} 0%, ${getPhaseColor()}AA 100%)`,
                boxShadow: `0 0 20px ${getPhaseColor()}40`
              }}
            />
          </div>
          <p
            className="mt-3 text-sm font-mono"
            style={{ color: '#888' }}
          >
            {Math.round(progress)}% completado
          </p>
        </div>

        {/* Características clave */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8 text-sm">
          <div 
            className="p-4 rounded-lg border"
            style={{ 
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              borderColor: 'rgba(59, 130, 246, 0.3)' 
            }}
          >
            <div className="font-semibold text-blue-400">Adaptación Profunda</div>
            <div className="text-gray-300">Valores CSS continuos</div>
          </div>
          <div 
            className="p-4 rounded-lg border"
            style={{ 
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              borderColor: 'rgba(16, 185, 129, 0.3)' 
            }}
          >
            <div className="font-semibold text-green-400">Zero Flicker</div>
            <div className="text-gray-300">SSR + Inyección CSS</div>
          </div>
          <div 
            className="p-4 rounded-lg border"
            style={{ 
              backgroundColor: 'rgba(139, 92, 246, 0.1)',
              borderColor: 'rgba(139, 92, 246, 0.3)' 
            }}
          >
            <div className="font-semibold text-purple-400">ML en Tiempo Real</div>
            <div className="text-gray-300">XGBoost Dual</div>
          </div>
        </div>
      </div>
    </div>
  );
}
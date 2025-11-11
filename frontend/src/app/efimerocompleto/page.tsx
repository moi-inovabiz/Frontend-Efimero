'use client';

import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import { useGeminiUI } from '@/hooks/useGeminiUI';
import { useEffect } from 'react';

export default function EfimeroCompletoPage() {
  const { user, isAuthenticated } = useAuth();
  const { generatedUI } = useGeminiUI();

  useEffect(() => {
    console.log('[EfimeroCompleto] Page mounted. Generated UI available?', !!generatedUI);
  }, [generatedUI]);

  if (!generatedUI) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-black to-indigo-900 p-8">
        <div className="max-w-xl text-center bg-white/10 backdrop-blur-lg rounded-3xl p-12 border border-indigo-500/40">
          <span className="text-6xl mb-6 block">🌀</span>
          <h1 className="text-3xl font-bold text-white mb-4">Aún no hay un frontend efímero generado</h1>
          <p className="text-indigo-200 mb-8">
            Primero visita <code className="px-2 py-1 bg-black/40 rounded">/efimero</code> para que Gemini AI cree tu experiencia personalizada.
          </p>
          <Link
            href="/efimero"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg transition-colors"
          >
            Ir a /efimero
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-pink-900 to-red-900">
      {/* Header */}
      <div className="bg-black/30 backdrop-blur-sm border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-3xl">🤖</span>
            <div>
              <h1 className="text-xl font-bold text-white">Frontend Efímero</h1>
              <p className="text-xs text-purple-300">Generado por Gemini 2.0 Flash</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {isAuthenticated && user && (
              <div className="text-right">
                <p className="text-sm text-white font-semibold">{user.email}</p>
                <p className="text-xs text-purple-300">{user.tipo_cliente}</p>
              </div>
            )}

            <Link
              href="/demo"
              className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors text-sm"
            >
              ← Volver
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-12">
        {/* Status Banner */}
        <div className="mb-12 bg-gradient-to-r from-green-500/20 to-emerald-500/20 backdrop-blur-sm border border-green-500/50 rounded-2xl p-6">
          <div className="flex items-start gap-4">
            <span className="text-4xl">✅</span>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white mb-2">
                UI Generada: <span className="text-green-300">{generatedUI.metadata.layout_type}</span>
              </h2>
              <p className="text-green-200 mb-4">
                Esta experiencia fue creada en tiempo real para ti por Gemini AI.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="bg-black/30 rounded-lg p-3">
                  <div className="text-green-400 font-semibold mb-1">Modelo</div>
                  <div className="text-white">{generatedUI.metadata.model}</div>
                </div>
                <div className="bg-black/30 rounded-lg p-3">
                  <div className="text-emerald-400 font-semibold mb-1">Generado</div>
                  <div className="text-white">
                    {new Date(generatedUI.metadata.generated_at).toLocaleString()}
                  </div>
                </div>
                <div className="bg-black/30 rounded-lg p-3">
                  <div className="text-teal-400 font-semibold mb-1">Contexto</div>
                  <div className="text-white">{user?.tipo_cliente || 'Visitante'}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* UI Generada */}
        <div
          className="rounded-2xl overflow-hidden border-4 border-purple-500/50 shadow-2xl"
          dangerouslySetInnerHTML={{ __html: generatedUI.html }}
        />

        {/* Información adicional */}
        <div className="mt-12 bg-black/50 backdrop-blur-sm rounded-2xl border border-purple-500/30 p-8">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>⚙️</span>
            <span>Detalles Técnicos</span>
          </h3>
          <ul className="space-y-2 text-purple-200 text-sm">
            <li>✅ HTML + Tailwind generado automáticamente</li>
            <li>✅ Personalizado con tu contexto y preferencias</li>
            <li>✅ Renderizado en cliente sin tocar el backend</li>
            <li>✅ Cacheado en sessionStorage para evitar segunda llamada</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

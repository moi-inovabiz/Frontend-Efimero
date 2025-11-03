'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-black p-4">
      <div className="text-center">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-4">
            Frontend Efímero
          </h1>
          <p className="text-xl text-gray-400 mb-2">
            Sistema de Adaptación Predictiva Profunda de UI
          </p>
          <p className="text-sm text-gray-500">
            Kaufmann Mercedes-Benz Chile
          </p>
        </div>

        {/* Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          {/* Register Button */}
          <Link
            href="/register"
            className="group relative w-64 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-xl font-semibold text-white shadow-lg hover:shadow-cyan-500/50 transition-all duration-300 hover:scale-105"
          >
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
              Crear Cuenta
            </span>
            <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 opacity-0 group-hover:opacity-20 transition-opacity" />
          </Link>

          {/* Login Button */}
          <Link
            href="/login"
            className="group relative w-64 px-8 py-4 bg-gray-700/50 border-2 border-gray-600 rounded-xl font-semibold text-white hover:border-cyan-500 hover:bg-gray-700 transition-all duration-300 hover:scale-105"
          >
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              Iniciar Sesión
            </span>
            <div className="absolute inset-0 rounded-xl bg-cyan-500 opacity-0 group-hover:opacity-10 transition-opacity" />
          </Link>
        </div>

        {/* Info Cards */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <div className="bg-gray-800/30 backdrop-blur-sm border border-gray-700 rounded-lg p-6">
            <div className="text-cyan-400 text-3xl mb-2">🧠</div>
            <h3 className="text-lg font-semibold text-white mb-2">ML Adaptativo</h3>
            <p className="text-sm text-gray-400">
              XGBoost con 45 features automáticas para personalización profunda
            </p>
          </div>

          <div className="bg-gray-800/30 backdrop-blur-sm border border-gray-700 rounded-lg p-6">
            <div className="text-cyan-400 text-3xl mb-2">🎨</div>
            <h3 className="text-lg font-semibold text-white mb-2">UI Dinámica</h3>
            <p className="text-sm text-gray-400">
              Interfaz que se adapta en tiempo real a tu comportamiento
            </p>
          </div>

          <div className="bg-gray-800/30 backdrop-blur-sm border border-gray-700 rounded-lg p-6">
            <div className="text-cyan-400 text-3xl mb-2">🚗</div>
            <h3 className="text-lg font-semibold text-white mb-2">Mercedes-Benz</h3>
            <p className="text-sm text-gray-400">
              Experiencia premium para clientes persona y empresa en Chile
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-gray-500 text-sm">
          <p>Sistema de autenticación con RUT chileno y preferencias visuales</p>
          <p className="mt-2">Backend: FastAPI + SQLAlchemy | Frontend: Next.js 15 + React 19</p>
        </div>
      </div>
    </div>
  );
}

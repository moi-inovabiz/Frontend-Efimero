/**
 * Dashboard Page - Protected Route
 * Displays personalized content based on tipo_cliente (persona vs empresa)
 * Requires authentication
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

export default function DashboardPage() {
  const router = useRouter();
  const { user, loading, isAuthenticated, logout } = useAuth();
  const [loadingLogout, setLoadingLogout] = useState(false);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [loading, isAuthenticated, router]);

  const handleLogout = async () => {
    setLoadingLogout(true);
    await logout();
    router.push('/');
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-black">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-cyan-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Cargando...</p>
        </div>
      </div>
    );
  }

  // Not authenticated (should redirect, but show fallback)
  if (!user) {
    return null;
  }

  const isEmpresa = user.tipo_cliente === 'empresa';

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--color-background, #0f172a)' }}>
      {/* Header */}
      <header style={{ 
        backgroundColor: 'var(--color-surface, #1e293b)', 
        borderBottomColor: 'var(--color-border, #334155)',
        borderBottomWidth: '1px'
      }}>
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold" style={{ color: 'var(--color-primary, #06b6d4)' }}>
                Frontend Efímero
              </h1>
              <p className="text-sm" style={{ color: 'var(--color-text-secondary, #94a3b8)' }}>
                Sistema Adaptativo
              </p>
            </div>
            
            {/* User Menu */}
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="font-semibold" style={{ color: 'var(--color-text, #f1f5f9)' }}>
                  {user.nombre} {user.apellido}
                </p>
                <p className="text-sm flex items-center justify-end gap-1" style={{ color: 'var(--color-text-secondary, #94a3b8)' }}>
                  {isEmpresa ? '🏢' : '👤'} {isEmpresa ? 'Empresa' : 'Persona Natural'}
                </p>
              </div>
              <Link
                href="/dashboard/preferences"
                className="px-4 py-2 rounded-lg text-sm font-medium"
                style={{
                  backgroundColor: 'var(--color-secondary, #3b82f6)',
                  color: '#ffffff',
                  transition: 'all var(--animation-duration, 300ms) var(--animation-easing, ease)',
                }}
              >
                🎨 Preferencias
              </Link>
              <button
                onClick={handleLogout}
                disabled={loadingLogout}
                className="px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  backgroundColor: 'rgba(239, 68, 68, 0.1)',
                  color: '#f87171',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  transition: `all var(--animation-duration, 300ms) var(--animation-easing, ease)`,
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.2)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.1)'}
              >
                {loadingLogout ? 'Cerrando...' : 'Cerrar Sesión'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8" style={{ padding: 'var(--spacing-base, 2rem)' }}>
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2" style={{ 
            color: 'var(--color-text, #f1f5f9)',
            fontSize: 'var(--font-size-heading, 1.875rem)'
          }}>
            ¡Bienvenido{isEmpresa ? 'a' : ''}, {user.nombre}!
          </h2>
          <p style={{ color: 'var(--color-text-secondary, #94a3b8)' }}>
            {isEmpresa 
              ? 'Gestiona tu flota y encuentra los mejores vehículos comerciales para tu empresa.'
              : 'Descubre el vehículo perfecto para ti con nuestra tecnología adaptativa.'}
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8" style={{ gap: 'var(--spacing-base, 1.5rem)' }}>
          {/* Profile Completion */}
          <div className="rounded-xl p-6" style={{ 
            backgroundColor: 'var(--color-surface, #1e293b)',
            border: '1px solid var(--color-border, #334155)',
            borderRadius: 'var(--border-radius, 0.75rem)',
            transition: `all var(--animation-duration, 300ms) var(--animation-easing, ease)`,
          }}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold" style={{ color: 'var(--color-text, #f1f5f9)' }}>Perfil Completo</h3>
              <span className="text-2xl">✓</span>
            </div>
            <p className="text-3xl font-bold" style={{ color: 'var(--color-primary, #06b6d4)' }}>100%</p>
            <p className="text-sm mt-2" style={{ color: 'var(--color-text-secondary, #94a3b8)' }}>Toda tu información está actualizada</p>
          </div>

          {/* Recommendations */}
          <div className="rounded-xl p-6" style={{ 
            backgroundColor: 'var(--color-surface, #1e293b)',
            border: '1px solid var(--color-border, #334155)',
            borderRadius: 'var(--border-radius, 0.75rem)',
            transition: `all var(--animation-duration, 300ms) var(--animation-easing, ease)`,
          }}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold" style={{ color: 'var(--color-text, #f1f5f9)' }}>Recomendaciones</h3>
              <span className="text-2xl">🚗</span>
            </div>
            <p className="text-3xl font-bold" style={{ color: 'var(--color-secondary, #3b82f6)' }}>
              {isEmpresa ? '12' : '8'}
            </p>
            <p className="text-sm mt-2" style={{ color: 'var(--color-text-secondary, #94a3b8)' }}>
              Vehículos que coinciden con tu perfil
            </p>
          </div>

          {/* Region */}
          <div className="rounded-xl p-6" style={{ 
            backgroundColor: 'var(--color-surface, #1e293b)',
            border: '1px solid var(--color-border, #334155)',
            borderRadius: 'var(--border-radius, 0.75rem)',
            transition: `all var(--animation-duration, 300ms) var(--animation-easing, ease)`,
          }}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold" style={{ color: 'var(--color-text, #f1f5f9)' }}>Ubicación</h3>
              <span className="text-2xl">📍</span>
            </div>
            <p className="text-lg font-bold" style={{ color: 'var(--color-accent, #8b5cf6)' }}>{user.region}</p>
            <p className="text-sm mt-2" style={{ color: 'var(--color-text-secondary, #94a3b8)' }}>Tu región actual</p>
          </div>
        </div>

        {/* User Profile Summary */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 p-6 mb-8">
          <h3 className="text-xl font-bold text-white mb-4">Tu Perfil</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column */}
            <div className="space-y-4">
              <div>
                <p className="text-gray-400 text-sm">Email</p>
                <p className="text-white font-medium">{user.email}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">RUT</p>
                <p className="text-white font-medium">{user.rut}</p>
              </div>
              {user.telefono && (
                <div>
                  <p className="text-gray-400 text-sm">Teléfono</p>
                  <p className="text-white font-medium">{user.telefono}</p>
                </div>
              )}
              {!isEmpresa && user.fecha_nacimiento && (
                <div>
                  <p className="text-gray-400 text-sm">Fecha de Nacimiento</p>
                  <p className="text-white font-medium">{user.fecha_nacimiento}</p>
                </div>
              )}
              {isEmpresa && user.tamano_flota && (
                <div>
                  <p className="text-gray-400 text-sm">Tamaño de Flota</p>
                  <p className="text-white font-medium">{user.tamano_flota} vehículos</p>
                </div>
              )}
            </div>

            {/* Right Column */}
            <div className="space-y-4">
              <div>
                <p className="text-gray-400 text-sm">Intereses Principales</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {user.interes_principal?.map((interes) => (
                    <span
                      key={interes}
                      className="bg-cyan-500/10 text-cyan-400 px-3 py-1 rounded-full text-sm border border-cyan-500/30"
                    >
                      {interes.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Uso Previsto</p>
                <p className="text-white font-medium capitalize">
                  {user.uso_previsto?.replace(/_/g, ' ')}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Presupuesto</p>
                <p className="text-white font-medium capitalize">
                  {user.presupuesto?.replace(/_/g, ' ').replace('m', 'M')}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Vehículo Actual</p>
                <p className="text-white font-medium">
                  {user.tiene_vehiculo_actual ? 'Sí' : 'No'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Visual Preferences */}
        {user.esquema_colores && (
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 p-6 mb-8">
            <h3 className="text-xl font-bold text-white mb-4">Preferencias Visuales</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-gray-400 text-sm">Esquema</p>
                <p className="text-white font-medium capitalize">{user.esquema_colores?.replace(/_/g, ' ')}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Color Favorito</p>
                <p className="text-white font-medium capitalize">{user.color_favorito}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Densidad</p>
                <p className="text-white font-medium capitalize">{user.densidad_informacion}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Animaciones</p>
                <p className="text-white font-medium capitalize">{user.nivel_animaciones}</p>
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link
            href="/"
            className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white p-6 rounded-xl hover:from-cyan-600 hover:to-blue-700 transition-all transform hover:scale-[1.02] flex items-center justify-between"
          >
            <div>
              <h4 className="font-bold text-lg mb-1">Explorar Vehículos</h4>
              <p className="text-cyan-100 text-sm">
                Descubre nuestra interfaz adaptativa en acción
              </p>
            </div>
            <span className="text-3xl">→</span>
          </Link>

          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 p-6 flex items-center justify-between opacity-50 cursor-not-allowed">
            <div>
              <h4 className="font-bold text-lg mb-1 text-gray-400">Configuración Avanzada</h4>
              <p className="text-gray-600 text-sm">Próximamente disponible</p>
            </div>
            <span className="text-3xl">⚙️</span>
          </div>
        </div>
      </main>
    </div>
  );
}

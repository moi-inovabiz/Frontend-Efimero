/**
 * Visual Preferences Edit Page
 * Permite al usuario cambiar sus preferencias visuales y ver cambios en tiempo real
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { updateVisualPreferences } from '@/lib/auth-client';

const ESQUEMAS_COLORES = [
  { value: 'automatico', label: 'Automático', desc: 'Se adapta al sistema' },
  { value: 'claro', label: 'Claro', desc: 'Fondo blanco, texto oscuro' },
  { value: 'oscuro', label: 'Oscuro', desc: 'Fondo negro, texto claro' },
  { value: 'alto_contraste', label: 'Alto Contraste', desc: 'Máxima legibilidad' },
  { value: 'lujo', label: 'Lujo', desc: 'Dorado y elegante' },
  { value: 'corporativo', label: 'Corporativo', desc: 'Azul profesional' },
  { value: 'moderno', label: 'Moderno', desc: 'Morado vibrante' },
];

const COLORES_FAVORITOS = [
  { value: 'azul', label: 'Azul', color: '#3b82f6' },
  { value: 'verde', label: 'Verde', color: '#10b981' },
  { value: 'rojo', label: 'Rojo', color: '#ef4444' },
  { value: 'amarillo', label: 'Amarillo', color: '#f59e0b' },
  { value: 'morado', label: 'Morado', color: '#8b5cf6' },
  { value: 'rosa', label: 'Rosa', color: '#ec4899' },
  { value: 'cyan', label: 'Cyan', color: '#06b6d4' },
  { value: 'naranja', label: 'Naranja', color: '#f97316' },
];

const ESTILOS_TIPOGRAFIA = [
  { value: 'moderna_geometrica', label: 'Moderna Geométrica' },
  { value: 'elegante_serif', label: 'Elegante Serif' },
  { value: 'technica_monospace', label: 'Técnica Monospace' },
  { value: 'humanista_sans', label: 'Humanista Sans' },
  { value: 'clasica_tradicional', label: 'Clásica Tradicional' },
];

const DENSIDADES = [
  { value: 'minimalista', label: 'Minimalista', desc: 'Espacioso y amplio' },
  { value: 'comoda', label: 'Cómoda', desc: 'Balance perfecto' },
  { value: 'compacta', label: 'Compacta', desc: 'Más información' },
  { value: 'maxima', label: 'Máxima', desc: 'Densidad total' },
];

const NIVELES_ANIMACIONES = [
  { value: 'ninguna', label: 'Ninguna', desc: 'Sin animaciones' },
  { value: 'sutiles', label: 'Sutiles', desc: 'Mínimas y rápidas' },
  { value: 'moderadas', label: 'Moderadas', desc: 'Balance perfecto' },
  { value: 'dinamicas', label: 'Dinámicas', desc: 'Expresivas' },
];

export default function VisualPreferencesPage() {
  const router = useRouter();
  const { user, refreshUser, loading: authLoading } = useAuth();

  const [esquemaColores, setEsquemaColores] = useState('automatico');
  const [colorFavorito, setColorFavorito] = useState('azul');
  const [estiloTipografia, setEstiloTipografia] = useState('moderna_geometrica');
  const [densidadInformacion, setDensidadInformacion] = useState('comoda');
  const [nivelAnimaciones, setNivelAnimaciones] = useState('moderadas');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Cargar preferencias actuales
  useEffect(() => {
    if (user) {
      setEsquemaColores(user.esquema_colores || 'automatico');
      setColorFavorito(user.color_favorito || 'azul');
      setEstiloTipografia(user.estilo_tipografia || 'moderna_geometrica');
      setDensidadInformacion(user.densidad_informacion || 'comoda');
      setNivelAnimaciones(user.nivel_animaciones || 'moderadas');
    }
  }, [user]);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [authLoading, user, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await updateVisualPreferences({
        esquema_colores: esquemaColores,
        color_favorito: colorFavorito,
        estilo_tipografia: estiloTipografia,
        densidad_informacion: densidadInformacion,
        nivel_animaciones: nivelAnimaciones,
      });

      // Refrescar datos del usuario para aplicar cambios inmediatamente
      await refreshUser();
      
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al actualizar preferencias');
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--color-background, #0f172a)' }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 mx-auto mb-4" style={{ borderColor: 'var(--color-primary, #06b6d4)' }}></div>
          <p style={{ color: 'var(--color-text-secondary, #94a3b8)' }}>Cargando...</p>
        </div>
      </div>
    );
  }

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
            <h1 className="text-2xl font-bold" style={{ color: 'var(--color-primary, #06b6d4)' }}>
              Preferencias Visuales
            </h1>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 rounded-lg text-sm font-medium"
              style={{
                backgroundColor: 'var(--color-surface, #1e293b)',
                color: 'var(--color-text, #f1f5f9)',
                border: '1px solid var(--color-border, #334155)',
              }}
            >
              ← Volver al Dashboard
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h2 className="text-3xl font-bold mb-2" style={{ color: 'var(--color-text, #f1f5f9)' }}>
            Personaliza tu Experiencia
          </h2>
          <p style={{ color: 'var(--color-text-secondary, #94a3b8)' }}>
            Los cambios se aplicarán inmediatamente en toda la interfaz
          </p>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="mb-6 p-4 rounded-lg" style={{ 
            backgroundColor: 'rgba(16, 185, 129, 0.1)', 
            border: '1px solid rgba(16, 185, 129, 0.3)',
            color: '#10b981'
          }}>
            ✓ Preferencias actualizadas correctamente
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 rounded-lg" style={{ 
            backgroundColor: 'rgba(239, 68, 68, 0.1)', 
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: '#f87171'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Esquema de Colores */}
          <div>
            <div className="block text-lg font-semibold mb-4" style={{ color: 'var(--color-text, #f1f5f9)' }}>
              Esquema de Colores
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {ESQUEMAS_COLORES.map((esquema) => (
                <button
                  key={esquema.value}
                  type="button"
                  onClick={() => setEsquemaColores(esquema.value)}
                  className="p-4 rounded-lg text-left"
                  style={{
                    backgroundColor: esquemaColores === esquema.value ? 'var(--color-primary, #06b6d4)' : 'var(--color-surface, #1e293b)',
                    border: `2px solid ${esquemaColores === esquema.value ? 'var(--color-primary, #06b6d4)' : 'var(--color-border, #334155)'}`,
                    color: esquemaColores === esquema.value ? '#ffffff' : 'var(--color-text, #f1f5f9)',
                    transition: 'all var(--animation-duration, 300ms) var(--animation-easing, ease)',
                  }}
                >
                  <div className="font-semibold">{esquema.label}</div>
                  <div className="text-sm opacity-80">{esquema.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Color Favorito */}
          <div>
            <div className="block text-lg font-semibold mb-4" style={{ color: 'var(--color-text, #f1f5f9)' }}>
              Color de Acento
            </div>
            <div className="grid grid-cols-4 gap-4">
              {COLORES_FAVORITOS.map((color) => (
                <button
                  key={color.value}
                  type="button"
                  onClick={() => setColorFavorito(color.value)}
                  className="p-4 rounded-lg text-center"
                  style={{
                    backgroundColor: color.color,
                    border: `3px solid ${colorFavorito === color.value ? '#ffffff' : 'transparent'}`,
                    color: '#ffffff',
                    fontWeight: '600',
                    transition: 'all var(--animation-duration, 300ms) var(--animation-easing, ease)',
                  }}
                >
                  {color.label}
                </button>
              ))}
            </div>
          </div>

          {/* Estilo Tipografía */}
          <div>
            <div className="block text-lg font-semibold mb-4" style={{ color: 'var(--color-text, #f1f5f9)' }}>
              Estilo de Tipografía
            </div>
            <div className="space-y-2">
              {ESTILOS_TIPOGRAFIA.map((estilo) => (
                <button
                  key={estilo.value}
                  type="button"
                  onClick={() => setEstiloTipografia(estilo.value)}
                  className="w-full p-4 rounded-lg text-left"
                  style={{
                    backgroundColor: estiloTipografia === estilo.value ? 'var(--color-primary, #06b6d4)' : 'var(--color-surface, #1e293b)',
                    border: `2px solid ${estiloTipografia === estilo.value ? 'var(--color-primary, #06b6d4)' : 'var(--color-border, #334155)'}`,
                    color: estiloTipografia === estilo.value ? '#ffffff' : 'var(--color-text, #f1f5f9)',
                    transition: 'all var(--animation-duration, 300ms) var(--animation-easing, ease)',
                  }}
                >
                  {estilo.label}
                </button>
              ))}
            </div>
          </div>

          {/* Densidad */}
          <div>
            <div className="block text-lg font-semibold mb-4" style={{ color: 'var(--color-text, #f1f5f9)' }}>
              Densidad de Información
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {DENSIDADES.map((densidad) => (
                <button
                  key={densidad.value}
                  type="button"
                  onClick={() => setDensidadInformacion(densidad.value)}
                  className="p-4 rounded-lg text-center"
                  style={{
                    backgroundColor: densidadInformacion === densidad.value ? 'var(--color-primary, #06b6d4)' : 'var(--color-surface, #1e293b)',
                    border: `2px solid ${densidadInformacion === densidad.value ? 'var(--color-primary, #06b6d4)' : 'var(--color-border, #334155)'}`,
                    color: densidadInformacion === densidad.value ? '#ffffff' : 'var(--color-text, #f1f5f9)',
                    transition: 'all var(--animation-duration, 300ms) var(--animation-easing, ease)',
                  }}
                >
                  <div className="font-semibold">{densidad.label}</div>
                  <div className="text-xs opacity-80">{densidad.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Nivel Animaciones */}
          <div>
            <div className="block text-lg font-semibold mb-4" style={{ color: 'var(--color-text, #f1f5f9)' }}>
              Nivel de Animaciones
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {NIVELES_ANIMACIONES.map((nivel) => (
                <button
                  key={nivel.value}
                  type="button"
                  onClick={() => setNivelAnimaciones(nivel.value)}
                  className="p-4 rounded-lg text-center"
                  style={{
                    backgroundColor: nivelAnimaciones === nivel.value ? 'var(--color-primary, #06b6d4)' : 'var(--color-surface, #1e293b)',
                    border: `2px solid ${nivelAnimaciones === nivel.value ? 'var(--color-primary, #06b6d4)' : 'var(--color-border, #334155)'}`,
                    color: nivelAnimaciones === nivel.value ? '#ffffff' : 'var(--color-text, #f1f5f9)',
                    transition: 'all var(--animation-duration, 300ms) var(--animation-easing, ease)',
                  }}
                >
                  <div className="font-semibold">{nivel.label}</div>
                  <div className="text-xs opacity-80">{nivel.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-4 rounded-lg font-semibold disabled:opacity-50"
              style={{
                backgroundColor: 'var(--color-primary, #06b6d4)',
                color: '#ffffff',
                transition: 'all var(--animation-duration, 300ms) var(--animation-easing, ease)',
              }}
            >
              {loading ? 'Guardando...' : 'Guardar Cambios'}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}

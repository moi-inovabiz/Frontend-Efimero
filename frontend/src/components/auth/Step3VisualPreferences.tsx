/**
 * Step 3: Visual Preferences (OPTIONAL)
 * - esquema_colores (palette selector)
 * - color_favorito (color picker)
 * - densidad_informacion (slider)
 * - estilo_tipografia (radio)
 * - prioridades_info (drag-and-drop ranking) - SIMPLIFIED to checkboxes for MVP
 * - nivel_animaciones (radio)
 * - User can skip this step
 * 
 * FEATURE: Aplica el tema en tiempo real mientras el usuario selecciona
 */

'use client';

import { useState, useEffect } from 'react';
import { RegistrationData } from '@/lib/auth-client';
import { generateTheme, themeToCSS } from '@/lib/theme-generator';

interface Step3Props {
  data: Partial<RegistrationData>;
  onUpdate: (data: Partial<RegistrationData>) => void;
  onSubmit: () => void;
  onSkip: () => void;
  onBack: () => void;
  loading: boolean;
}

const ESQUEMAS_COLORES = [
  { value: 'automatico', label: 'Automático', colors: ['#3b82f6', '#ef4444', '#10b981'] },
  { value: 'claro', label: 'Claro', colors: ['#ffffff', '#f3f4f6', '#e5e7eb'] },
  { value: 'oscuro', label: 'Oscuro', colors: ['#111827', '#1f2937', '#374151'] },
  { value: 'alto_contraste', label: 'Alto Contraste', colors: ['#000000', '#ffffff', '#ffff00'] },
  { value: 'lujo', label: 'Lujo', colors: ['#000000', '#fbbf24', '#d1d5db'] },
  { value: 'corporativo', label: 'Corporativo', colors: ['#1e3a8a', '#374151', '#6b7280'] },
  { value: 'moderno', label: 'Moderno', colors: ['#06b6d4', '#8b5cf6', '#ec4899'] },
];

const COLORES_FAVORITOS = [
  { value: 'azul', label: 'Azul', hex: '#3b82f6' },
  { value: 'rojo', label: 'Rojo', hex: '#ef4444' },
  { value: 'verde', label: 'Verde', hex: '#10b981' },
  { value: 'amarillo', label: 'Amarillo', hex: '#fbbf24' },
  { value: 'morado', label: 'Morado', hex: '#8b5cf6' },
  { value: 'negro', label: 'Negro', hex: '#000000' },
  { value: 'blanco', label: 'Blanco', hex: '#ffffff' },
  { value: 'gris', label: 'Gris', hex: '#6b7280' },
  { value: 'naranja', label: 'Naranja', hex: '#f97316' },
];

const DENSIDADES = [
  { value: 'minimalista', label: 'Minimalista', description: 'Solo lo esencial' },
  { value: 'comoda', label: 'Cómoda', description: 'Balance ideal' },
  { value: 'detallada', label: 'Detallada', description: 'Mucha información' },
  { value: 'maxima', label: 'Máxima', description: 'Todo visible' },
];

const TIPOGRAFIAS = [
  { value: 'clasica_serif', label: 'Clásica Serif', preview: 'Times New Roman' },
  { value: 'moderna_geometrica', label: 'Moderna Geométrica', preview: 'Futura' },
  { value: 'humanista', label: 'Humanista', preview: 'Gill Sans' },
  { value: 'industrial', label: 'Industrial', preview: 'DIN' },
  { value: 'lujo', label: 'Lujo', preview: 'Didot' },
];

const NIVELES_ANIMACION = [
  { value: 'ninguna', label: 'Sin Animaciones', icon: '🚫' },
  { value: 'minimas', label: 'Mínimas', icon: '⚡' },
  { value: 'moderadas', label: 'Moderadas', icon: '✨' },
  { value: 'completas', label: 'Completas', icon: '🎨' },
];

export default function Step3VisualPreferences({ data, onUpdate, onSubmit, onSkip, onBack, loading }: Step3Props) {
  const visualPrefs = data.visual_preferences || {};
  
  const [esquema, setEsquema] = useState(visualPrefs.esquema_colores || 'automatico');
  const [colorFav, setColorFav] = useState(visualPrefs.color_favorito || 'azul');
  const [densidad, setDensidad] = useState(visualPrefs.densidad_informacion || 'comoda');
  const [tipografia, setTipografia] = useState(visualPrefs.estilo_tipografia || 'moderna_geometrica');
  const [animaciones, setAnimaciones] = useState(visualPrefs.nivel_animaciones || 'moderadas');

  // Aplicar tema en tiempo real mientras el usuario selecciona opciones
  useEffect(() => {
    console.log('[Step3] Aplicando tema preview:', { esquema, colorFav, densidad, tipografia, animaciones });
    
    // Crear un usuario temporal con las preferencias seleccionadas
    const tempUser = {
      id: 'preview',
      email: 'preview@example.com',
      nombre: 'Preview',
      apellido: 'User',
      rut: '11111111-1',
      tipo_cliente: 'persona' as const,
      region: 'Metropolitana',
      tiene_vehiculo_actual: false,
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      
      // Preferencias visuales seleccionadas
      esquema_colores: esquema,
      color_favorito: colorFav,
      estilo_tipografia: tipografia,
      densidad_informacion: densidad,
      nivel_animaciones: animaciones,
      estilo_imagenes: 'fotografico',
      preferencia_layout: 'cuadricula',
      estilo_navegacion: 'hamburguesa',
      preferencia_visual: 'imagenes',
      modo_comparacion: 'lado_a_lado',
      idioma_specs: 'espanol',
    };

    // Generar y aplicar el tema
    const theme = generateTheme(tempUser);
    const css = themeToCSS(theme);

    let style = document.getElementById('user-theme-preview');
    if (!style) {
      style = document.createElement('style');
      style.id = 'user-theme-preview';
      document.head.appendChild(style);
    }
    style.textContent = css;
    document.body.style.fontFamily = theme.fontFamily;

    console.log('[Step3] Tema preview aplicado');

    // Cleanup: No remover el style al desmontar para que persista al siguiente paso
    return () => {
      console.log('[Step3] Componente desmontado, manteniendo tema preview');
    };
  }, [esquema, colorFav, densidad, tipografia, animaciones]);

  // Handle submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    console.log('[Step3] Guardando preferencias:', { esquema, colorFav, densidad, tipografia, animaciones });

    onUpdate({
      visual_preferences: {
        esquema_colores: esquema,
        color_favorito: colorFav,
        densidad_informacion: densidad,
        estilo_tipografia: tipografia,
        nivel_animaciones: animaciones,
      },
    });

    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Header */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-white mb-2">Personaliza tu Experiencia</h2>
        <p className="text-gray-400 text-sm">
          Estas preferencias son opcionales. Puedes omitir este paso y configurarlo más tarde.
        </p>
      </div>

      {/* Esquema de Colores */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-3">
          Esquema de Colores
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {ESQUEMAS_COLORES.map((esquemaItem) => (
            <button
              key={esquemaItem.value}
              type="button"
              onClick={() => setEsquema(esquemaItem.value)}
              className={`p-4 rounded-lg border-2 transition-all ${
                esquema === esquemaItem.value
                  ? 'border-cyan-500 bg-cyan-500/10'
                  : 'border-gray-600 bg-gray-700/30 hover:border-gray-500'
              }`}
            >
              <div className="flex gap-1 mb-2 justify-center">
                {esquemaItem.colors.map((color, i) => (
                  <div
                    key={i}
                    className="w-6 h-6 rounded"
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
              <p className={`text-sm font-medium ${esquema === esquemaItem.value ? 'text-cyan-300' : 'text-gray-400'}`}>
                {esquemaItem.label}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Color Favorito */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-3">
          Color Favorito
        </label>
        <div className="grid grid-cols-3 md:grid-cols-5 gap-3">
          {COLORES_FAVORITOS.map((color) => (
            <button
              key={color.value}
              type="button"
              onClick={() => setColorFav(color.value)}
              className={`p-3 rounded-lg border-2 transition-all ${
                colorFav === color.value
                  ? 'border-cyan-500 bg-cyan-500/10'
                  : 'border-gray-600 bg-gray-700/30 hover:border-gray-500'
              }`}
            >
              <div
                className="w-full h-8 rounded mb-2"
                style={{ backgroundColor: color.hex }}
              />
              <p className={`text-xs font-medium ${colorFav === color.value ? 'text-cyan-300' : 'text-gray-400'}`}>
                {color.label}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Densidad de Información */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-3">
          Densidad de Información
        </label>
        <div className="space-y-2">
          {DENSIDADES.map((dens) => (
            <label
              key={dens.value}
              className={`flex items-center justify-between p-4 rounded-lg border-2 cursor-pointer transition-all ${
                densidad === dens.value
                  ? 'border-cyan-500 bg-cyan-500/10'
                  : 'border-gray-600 bg-gray-700/30 hover:border-gray-500'
              }`}
            >
              <div className="flex items-center">
                <input
                  type="radio"
                  name="densidad"
                  value={dens.value}
                  checked={densidad === dens.value}
                  onChange={(e) => setDensidad(e.target.value)}
                  className="w-4 h-4 text-cyan-500 border-gray-600 focus:ring-cyan-500 focus:ring-offset-gray-800"
                />
                <div className="ml-3">
                  <span className={`font-medium ${densidad === dens.value ? 'text-cyan-300' : 'text-gray-400'}`}>
                    {dens.label}
                  </span>
                  <p className="text-xs text-gray-500">{dens.description}</p>
                </div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Estilo de Tipografía */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-3">
          Estilo de Tipografía
        </label>
        <div className="space-y-2">
          {TIPOGRAFIAS.map((tipo) => (
            <label
              key={tipo.value}
              className={`flex items-center justify-between p-4 rounded-lg border-2 cursor-pointer transition-all ${
                tipografia === tipo.value
                  ? 'border-cyan-500 bg-cyan-500/10'
                  : 'border-gray-600 bg-gray-700/30 hover:border-gray-500'
              }`}
            >
              <div className="flex items-center">
                <input
                  type="radio"
                  name="tipografia"
                  value={tipo.value}
                  checked={tipografia === tipo.value}
                  onChange={(e) => setTipografia(e.target.value)}
                  className="w-4 h-4 text-cyan-500 border-gray-600 focus:ring-cyan-500 focus:ring-offset-gray-800"
                />
                <span className={`ml-3 font-medium ${tipografia === tipo.value ? 'text-cyan-300' : 'text-gray-400'}`}>
                  {tipo.label}
                </span>
              </div>
              <span className="text-gray-500 text-sm italic">{tipo.preview}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Nivel de Animaciones */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-3">
          Nivel de Animaciones
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {NIVELES_ANIMACION.map((nivel) => (
            <button
              key={nivel.value}
              type="button"
              onClick={() => setAnimaciones(nivel.value)}
              className={`p-4 rounded-lg border-2 transition-all ${
                animaciones === nivel.value
                  ? 'border-cyan-500 bg-cyan-500/10'
                  : 'border-gray-600 bg-gray-700/30 hover:border-gray-500'
              }`}
            >
              <div className="text-2xl mb-1">{nivel.icon}</div>
              <p className={`text-sm font-medium ${animaciones === nivel.value ? 'text-cyan-300' : 'text-gray-400'}`}>
                {nivel.label}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Navigation Buttons */}
      <div className="flex gap-4">
        <button
          type="button"
          onClick={onBack}
          disabled={loading}
          className="flex-1 bg-gray-700 text-gray-300 py-3 rounded-lg font-semibold hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:ring-offset-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ← Atrás
        </button>
        <button
          type="button"
          onClick={onSkip}
          disabled={loading}
          className="flex-1 bg-gray-700 text-gray-300 py-3 rounded-lg font-semibold hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:ring-offset-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Omitir
        </button>
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-3 rounded-lg font-semibold hover:from-cyan-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-gray-800 transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Creando cuenta...
            </>
          ) : (
            'Completar Registro ✓'
          )}
        </button>
      </div>
    </form>
  );
}

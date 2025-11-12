/**
 * Frontend Efímero - Generado por Gemini AI + Canva MCP
 * 
 * Esta página es completamente generada dinámicamente usando:
 * - Gemini AI: Decisiones de diseño y composición
 * - Canva Dev MCP: Generación de assets visuales
 * - Contexto del usuario: 64+ campos para personalización extrema
 * 
 * NO afecta el sistema actual - es un experimento paralelo
 */

'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useEphemeralContext } from '@/hooks/useEphemeralContext';
import { usePersona } from '@/hooks/usePersona';
import { useGeminiUI } from '@/hooks/useGeminiUI';
import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function EfimeroPage() {
  const { user, isAuthenticated } = useAuth();
  const contextData = useEphemeralContext();
  const personaData = usePersona();
  const { generateUI, loading, error: geminiError, generatedUI, apiKeyError } = useGeminiUI();
  
  const [renderError, setRenderError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  
  const router = useRouter();

  // USAR useRef PARA EVITAR RE-RENDERS INFINITOS
  const isGeneratingRef = useRef(false);
  const hasGeneratedRef = useRef(false);
  const hasNavigatedRef = useRef(false);
  const hasErroredRef = useRef(false); // Nueva ref para evitar loops en errores
  const lastPersonaIdRef = useRef<string | null>(null); // Tracking de cambios de persona

  const handleRetry = () => {
    console.log('[Efimero] Manual retry triggered');
    hasGeneratedRef.current = false; // Reset la bandera
    isGeneratingRef.current = false;
    hasNavigatedRef.current = false;
    hasErroredRef.current = false; // Reset error flag
    setRenderError(null);
    setRetryCount(prev => prev + 1);
  };

  // Efecto para detectar cambios de persona y resetear generación
  useEffect(() => {
    const currentPersonaId = personaData?.persona?.id || null;
    
    if (currentPersonaId !== lastPersonaIdRef.current) {
      console.log('[Efimero] 👤 Persona changed!');
      console.log('[Efimero] Previous:', lastPersonaIdRef.current);
      console.log('[Efimero] Current:', currentPersonaId);
      console.log('[Efimero] 🔄 Resetting generation flags to regenerate UI...');
      
      // Resetear todas las flags para forzar nueva generación
      hasGeneratedRef.current = false;
      isGeneratingRef.current = false;
      hasErroredRef.current = false;
      
      // Actualizar la referencia
      lastPersonaIdRef.current = currentPersonaId;
    }
  }, [personaData?.persona?.id]);

  useEffect(() => {
    // Si hay error de API key, no intentar de nuevo (evitar loop)
    if (apiKeyError || hasErroredRef.current) {
      console.log('[Efimero] ⛔ API Key error detected - stopping retry loop');
      hasErroredRef.current = true;
      return;
    }

    // Si hay cualquier error de Gemini, no reintentar automáticamente
    if (geminiError && !hasErroredRef.current) {
      console.log('[Efimero] ⚠️ Gemini error detected:', geminiError);
      hasErroredRef.current = true;
      setRenderError(geminiError);
      return;
    }
    
    // Si ya tenemos UI generada (por cache) no volver a disparar generación
    if (generatedUI) {
      if (!hasGeneratedRef.current) {
        console.log('[Efimero] ✅ Generated UI already available (likely from cache). Skipping generation.');
      }
      hasGeneratedRef.current = true;
      return;
    }

    if (hasGeneratedRef.current) {
      console.log('[Efimero] ⛔ Already generated - EARLY EXIT');
      return;
    }

    if (isGeneratingRef.current) {
      console.log('[Efimero] ⏳ Generation already in progress');
      return;
    }

    if (!user && !contextData && !personaData) {
      console.log('[Efimero] No hay datos suficientes, esperando...');
      return;
    }

    const generateEfimeroLayout = async () => {
      console.log('[Efimero] useEffect triggered');
      console.log('[Efimero] User:', !!user, 'Context:', !!contextData, 'Persona:', !!personaData);
      console.log('[Efimero] Has generated:', hasGeneratedRef.current, 'Is generating:', isGeneratingRef.current, 'Loading:', loading, 'Generated UI:', !!generatedUI);

      isGeneratingRef.current = true;

      try {
        setRenderError(null);
        console.log('[Efimero] 🔄 Starting generation...');
        console.log('[Efimero] Building params for Gemini...');

        /**
         * FLUJO DE DATOS: Demo Adaptativa → Frontend Efímero
         * 
         * 1. El usuario selecciona un perfil en /demo usando <PersonaSelector>
         * 2. PersonaSelector llama assignSpecificPersona(personaId) del hook usePersona
         * 3. usePersona obtiene la Persona completa del backend (/personas/assign/:id)
         * 4. La Persona incluye TODOS los campos de preferencias visuales:
         *    - esquema_colores, color_favorito, densidad_informacion
         *    - estilo_tipografia, estilo_imagenes, nivel_animaciones
         *    - preferencia_layout, estilo_navegacion, preferencia_visual
         *    - modo_comparacion, idioma_specs
         * 5. Cuando se navega a /efimero, este componente:
         *    - Lee la Persona activa via usePersona (personaData)
         *    - Extrae TODAS las preferencias visuales de la Persona
         *    - Las envía a Gemini via buildPrompt()
         * 6. Gemini genera HTML personalizado respetando estas preferencias
         * 7. El usuario puede volver a /demo, cambiar de perfil, y ver diferencias
         * 
         * PRIORIDAD: Persona > User autenticado > Defaults
         * Si hay Persona seleccionada, usar sus preferencias (más específicas)
         * Si no, usar preferencias del User autenticado (perfil general)
         * Si no, usar defaults
         */

        // Priorizar datos de Persona sobre User (Persona es más específica y actualizada)
        const sourcePersona = personaData?.persona;
        const sourceUser = user;

        const params = {
          // Datos demográficos: priorizar Persona > User
          user: {
            tipo_cliente: sourcePersona?.tipo_cliente || sourceUser?.tipo_cliente || 'general',
            edad: sourcePersona?.edad || undefined,
            region: sourcePersona?.region || sourceUser?.region || 'Metropolitana',
            interes_principal: (() => {
              const personaIntereses = sourcePersona?.interes_principal;
              const userIntereses = sourceUser?.interes_principal;
              
              if (personaIntereses) {
                return typeof personaIntereses === 'string' ? [personaIntereses] : personaIntereses;
              }
              return userIntereses || [];
            })(),
            presupuesto: sourcePersona?.presupuesto || sourceUser?.presupuesto || 'medio'
          },
          
          // Preferencias visuales: usar TODOS los campos de la Persona (11 campos completos)
          preferences: {
            esquema_colores: sourcePersona?.esquema_colores || sourceUser?.esquema_colores || 'moderno',
            color_favorito: sourcePersona?.color_favorito || sourceUser?.color_favorito || '#0EA5E9',
            densidad_informacion: sourcePersona?.densidad_informacion || sourceUser?.densidad_informacion || 'comoda',
            estilo_tipografia: sourcePersona?.estilo_tipografia || sourceUser?.estilo_tipografia || 'moderna_geometrica',
            estilo_imagenes: sourcePersona?.estilo_imagenes || sourceUser?.estilo_imagenes || 'fotograficas',
            nivel_animaciones: sourcePersona?.nivel_animaciones || sourceUser?.nivel_animaciones || 'medio',
            preferencia_layout: sourcePersona?.preferencia_layout || sourceUser?.preferencia_layout || 'cards',
            estilo_navegacion: sourcePersona?.estilo_navegacion || sourceUser?.estilo_navegacion || 'horizontal',
            preferencia_visual: sourcePersona?.preferencia_visual || sourceUser?.preferencia_visual || 'equilibrada',
            modo_comparacion: sourcePersona?.modo_comparacion || sourceUser?.modo_comparacion || 'lado_a_lado',
            idioma_specs: sourcePersona?.idioma_specs || sourceUser?.idioma_specs || 'tecnico',
            
            // Prioridades (booleanos) - Solo PersonaSimulada tiene estos campos
            prioriza_precio: sourcePersona?.prioriza_precio || false,
            prioriza_tecnologia: sourcePersona?.prioriza_tecnologia || false,
            prioriza_consumo: sourcePersona?.prioriza_consumo || false
          },
          
          // Contexto del dispositivo (datos efímeros del navegador)
          context: contextData ? {
            tipo_dispositivo: contextData.device_type || 'desktop',
            navegador: contextData.browser_name || 'unknown',
            sistema_operativo: contextData.os_name || 'unknown'
          } : {
            tipo_dispositivo: 'desktop',
            navegador: 'unknown',
            sistema_operativo: 'unknown'
          },
          
          // Info de la Persona para contexto adicional
          persona: sourcePersona ? {
            nombre: sourcePersona.nombre,
            tipo_cliente: sourcePersona.tipo_cliente,
            edad: sourcePersona.edad,
            region: sourcePersona.region
          } : undefined
        };

        console.log('[Efimero] 📊 Params construidos:', {
          source: sourcePersona ? 'Persona seleccionada' : sourceUser ? 'User autenticado' : 'Defaults',
          personaName: sourcePersona ? `${sourcePersona.nombre} ${sourcePersona.apellido}` : 'N/A',
          tipoCliente: params.user.tipo_cliente,
          edad: params.user.edad,
          preferencias: {
            color: params.preferences.color_favorito,
            densidad: params.preferences.densidad_informacion,
            animaciones: params.preferences.nivel_animaciones,
            layout: params.preferences.preferencia_layout
          }
        });

        console.log('[Efimero] Params ready, calling generateUI...');
        const result = await generateUI(params);

        if (result) {
          console.log('[Efimero] ✅ Generation completed successfully');
          hasGeneratedRef.current = true;
          hasErroredRef.current = false; // Reset error si funciona
        } else {
          console.log('[Efimero] ⚠️ generateUI returned null');
          hasErroredRef.current = true; // Evitar loop si retorna null
        }
      } catch (err) {
        console.error('[Efimero] ❌ Error generating efimero layout:', err);
        setRenderError('No se pudo generar el layout personalizado');
        hasErroredRef.current = true; // Evitar loop en catch
      } finally {
        isGeneratingRef.current = false;
      }
    };

    generateEfimeroLayout();
  }, [user, contextData, personaData, retryCount, generatedUI, generateUI, geminiError, apiKeyError]);

  // NO navegar a otra página - renderizar aquí mismo
  // useEffect(() => {
  //   if (!generatedUI) {
  //     return;
  //   }

  //   if (hasNavigatedRef.current) {
  //     return;
  //   }

  //   console.log('[Efimero] 🚀 Navigating to /efimerocompleto (UI ready)');
  //   hasNavigatedRef.current = true;
  //   hasGeneratedRef.current = true;
  //   router.prefetch('/efimerocompleto');
  //   router.push('/efimerocompleto');
  // }, [generatedUI, router]);

  // Timeout de seguridad - si loading dura más de 30 segundos, mostrar error
  useEffect(() => {
    if (!loading) return;
    
    const timeout = setTimeout(() => {
      if (loading) {
        console.error('[Efimero] Timeout: Gemini tardó más de 30s');
        setRenderError('La generación está tardando demasiado. Intenta recargar la página.');
      }
    }, 30000);
    
    return () => clearTimeout(timeout);
  }, [loading]);

  // Si ya tenemos UI generada, renderizarla directamente
  if (generatedUI && !loading) {
    console.log('[Efimero] ✅ Rendering generated UI');
    
    // Extraer el color favorito de la persona para usarlo en el botón
    const personaColor = personaData?.persona?.color_favorito || '#06B6D4';
    
    return (
      <>
        {/* Botón de volver - FUERA del contenedor para evitar conflictos */}
        <div className="fixed top-4 left-4 z-50">
          <Link
            href="/demo"
            className="inline-flex items-center gap-2 px-4 py-2 backdrop-blur-sm text-white rounded-lg transition-all shadow-lg"
            style={{ 
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              border: `2px solid ${personaColor}`
            }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver a Demo
          </Link>
        </div>

        {/* HTML generado por Gemini - Con Tailwind CSS aplicado */}
        <div className="w-full" dangerouslySetInnerHTML={{ __html: generatedUI.html }} />
      </>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-pink-900 to-red-900">
        <div className="text-center">
          <div className="relative">
            {/* Loader animado */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-24 h-24 border-8 border-purple-300/30 rounded-full"></div>
            </div>
            <div className="animate-spin rounded-full h-24 w-24 border-t-8 border-b-8 border-purple-400 mx-auto"></div>
          </div>
          
          <h2 className="text-2xl font-bold text-white mt-8 mb-2">
            🤖 Gemini AI está trabajando...
          </h2>
          <p className="text-purple-300 animate-pulse">
            Generando tu frontend personalizado
          </p>
          
          <div className="mt-6 flex flex-col gap-2 text-sm text-purple-400">
            <div className="flex items-center gap-2 justify-center">
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
              <span>Analizando tu contexto único</span>
            </div>
            <div className="flex items-center gap-2 justify-center">
              <div className="w-2 h-2 bg-pink-400 rounded-full animate-pulse delay-100"></div>
              <span>Decidiendo layout óptimo</span>
            </div>
            <div className="flex items-center gap-2 justify-center">
              <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse delay-200"></div>
              <span>Generando HTML con Tailwind</span>
            </div>
          </div>
          
          {/* Botón de cancelar después de 10 segundos */}
          <div className="mt-8">
            <Link 
              href="/demo"
              className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors text-sm inline-block"
            >
              ← Volver al Demo
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const error = geminiError || renderError;

  if (error || apiKeyError) {
    const isApiKeyIssue = apiKeyError || (error && (error.includes('API key') || error.includes('leaked')));
    
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-900 via-orange-900 to-yellow-900 p-8">
        <div className="max-w-3xl bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-red-500/50">
          <div className="text-center">
            <span className="text-6xl mb-4 block">{isApiKeyIssue ? '🔑' : '⚠️'}</span>
            <h2 className="text-3xl font-bold text-white mb-4">
              {isApiKeyIssue ? 'API Key Comprometida' : 'Error al generar frontend'}
            </h2>
            <p className="text-red-300 mb-6">{error}</p>
            
            {isApiKeyIssue && (
              <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-6 mb-6 text-left">
                <h3 className="text-lg font-bold text-yellow-300 mb-3">🔒 Solución:</h3>
                <ol className="space-y-2 text-sm text-white/90">
                  <li className="flex gap-2">
                    <span className="font-bold">1.</span>
                    <span>Ve a <a href="https://aistudio.google.com/app/apikey" target="_blank" className="text-blue-300 underline hover:text-blue-200">Google AI Studio</a></span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-bold">2.</span>
                    <span>Crea una nueva API key de Gemini</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-bold">3.</span>
                    <span>Edita el archivo <code className="px-2 py-1 bg-black/40 rounded text-yellow-300">frontend/.env.local</code></span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-bold">4.</span>
                    <span>Reemplaza <code className="px-2 py-1 bg-black/40 rounded text-yellow-300">NEXT_PUBLIC_GEMINI_API_KEY=TU_NUEVA_KEY</code></span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-bold">5.</span>
                    <span>Reinicia el servidor con <code className="px-2 py-1 bg-black/40 rounded text-yellow-300">npm run dev</code></span>
                  </li>
                </ol>
                <div className="mt-4 p-3 bg-yellow-500/20 border border-yellow-500/50 rounded">
                  <p className="text-xs text-yellow-200">
                    ⚠️ <strong>Importante:</strong> Nunca compartas tu API key en repositorios públicos. 
                    La actual fue deshabilitada por Google por estar expuesta en Git.
                  </p>
                </div>
              </div>
            )}
            
            <div className="bg-black/30 rounded-lg p-4 mb-6 text-left">
              <p className="text-sm text-yellow-300 font-mono break-all">
                {geminiError || renderError || 'Error desconocido'}
              </p>
            </div>
            
            <div className="flex gap-4 justify-center">
              <Link 
                href="/demo"
                className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
              >
                ← Volver al Demo
              </Link>
              {!isApiKeyIssue && (
                <button
                  onClick={handleRetry}
                  className="px-6 py-3 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors"
                >
                  🔄 Reintentar
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!generatedUI) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-black p-8">
        <div className="text-center">
          <p className="text-white text-xl">Esperando generación...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-pink-900 to-red-900">
      {/* Header con info del sistema */}
      <div className="bg-black/30 backdrop-blur-sm border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-3xl">🤖</span>
            <div>
              <h1 className="text-xl font-bold text-white">Frontend Efímero</h1>
              <p className="text-xs text-purple-300">Powered by Gemini 2.0 Flash</p>
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
                Este diseño fue creado específicamente para ti por Gemini AI en tiempo real
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="bg-black/30 rounded-lg p-3">
                  <div className="text-green-400 font-semibold mb-1">Modelo</div>
                  <div className="text-white">
                    {generatedUI.metadata.model}
                  </div>
                </div>
                
                <div className="bg-black/30 rounded-lg p-3">
                  <div className="text-emerald-400 font-semibold mb-1">Generado</div>
                  <div className="text-white">
                    {new Date(generatedUI.metadata.generated_at).toLocaleTimeString()}
                  </div>
                </div>
                
                <div className="bg-black/30 rounded-lg p-3">
                  <div className="text-teal-400 font-semibold mb-1">Contexto</div>
                  <div className="text-white">
                    {user?.tipo_cliente || 'Visitante'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* UI Generada por Gemini */}
        <div 
          className="rounded-2xl overflow-hidden border-4 border-purple-500/50 shadow-2xl"
          dangerouslySetInnerHTML={{ __html: generatedUI.html }}
        />

        {/* Info técnica */}
        <div className="mt-12 bg-black/50 backdrop-blur-sm rounded-2xl border border-purple-500/30 p-8">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>⚙️</span>
            {' '}
            Información Técnica
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div>
              <h4 className="text-purple-400 font-semibold mb-2">Tecnología</h4>
              <ul className="space-y-1 text-purple-200">
                <li>✅ Gemini 1.5 Flash API integrada</li>
                <li>✅ Generación en tiempo real (~3-5s)</li>
                <li>✅ HTML + Tailwind CSS</li>
                <li>✅ Personalización basada en 64+ campos</li>
                <li>✅ Sin backend intermediario</li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-pink-400 font-semibold mb-2">Datos Utilizados</h4>
              <ul className="space-y-1 text-pink-200">
                {user && <li>• Usuario: {user.tipo_cliente}</li>}
                {user && (
                  <>
                    <li>• Esquema: {user.esquema_colores}</li>
                    <li>• Densidad: {user.densidad_informacion}</li>
                  </>
                )}
                {personaData?.persona && <li>• Persona: {personaData.persona.nombre}</li>}
                <li>• Contexto efímero detectado</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

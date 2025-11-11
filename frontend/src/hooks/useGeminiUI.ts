/**
 * useGeminiUI Hook
 * 
 * Hook para interactuar con Gemini API y generar UIs personalizadas
 * Consume directamente la API de Google Generative AI (Gemini)
 */

import { useState, useCallback } from 'react';

const GEMINI_API_KEY = process.env.NEXT_PUBLIC_GEMINI_API_KEY;
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';

interface UserContext {
  tipo_cliente?: string;
  edad?: number;
  region?: string;
  interes_principal?: string[];
  presupuesto?: string;
}

interface VisualPreferences {
  esquema_colores?: string;
  color_favorito?: string;
  densidad_informacion?: string;
  estilo_tipografia?: string;
  nivel_animaciones?: string;
  prioriza_precio?: boolean;
  prioriza_tecnologia?: boolean;
  prioriza_consumo?: boolean;
}

interface EphemeralContext {
  tipo_dispositivo?: string;
  navegador?: string;
  sistema_operativo?: string;
}

interface PersonaData {
  nombre?: string;
  tipo_cliente?: string;
  edad?: number;
  region?: string;
}

interface GenerateUIParams {
  user?: UserContext;
  preferences?: VisualPreferences;
  context?: EphemeralContext;
  persona?: PersonaData;
}

interface GeneratedUI {
  html: string;
  metadata: {
    model: string;
    generated_at: string;
    layout_type: string;
  };
}

const SESSION_STORAGE_KEY = 'efimero_ui_cache_v1';

export function useGeminiUI() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedUI, setGeneratedUI] = useState<GeneratedUI | null>(() => {
    if (typeof window === 'undefined') {
      return null;
    }

    try {
      const cached = window.sessionStorage.getItem(SESSION_STORAGE_KEY);
      if (!cached) {
        return null;
      }

      const parsed = JSON.parse(cached) as GeneratedUI;
      // Validar que sea un objeto con HTML antes de usarlo
      if (parsed && typeof parsed.html === 'string') {
        console.log('[useGeminiUI] Loaded cached UI from sessionStorage');
        return parsed;
      }
    } catch (cacheError) {
      console.warn('[useGeminiUI] Failed to parse cached UI:', cacheError);
    }

    return null;
  });

  const buildPrompt = useCallback((params: GenerateUIParams): string => {
    const { user, preferences, context, persona } = params;

    return `
Eres un diseñador UI/UX experto especializado en e-commerce automotriz Mercedes-Benz.

Tu tarea es generar un diseño HTML completo usando Tailwind CSS para una landing page personalizada.

**INFORMACIÓN DEL USUARIO:**
- Tipo de cliente: ${user?.tipo_cliente || 'general'}
- Edad: ${user?.edad || 'no especificada'}
- Región: ${user?.region || 'Chile'}
- Intereses: ${user?.interes_principal?.join(', ') || 'vehículos de lujo'}
- Presupuesto: ${user?.presupuesto || 'medio'}

**PREFERENCIAS VISUALES:**
- Esquema de colores: ${preferences?.esquema_colores || 'automatico'}
- Color favorito: ${preferences?.color_favorito || 'azul'}
- Densidad de información: ${preferences?.densidad_informacion || 'comoda'}
- Estilo tipográfico: ${preferences?.estilo_tipografia || 'moderna_geometrica'}
- Nivel de animaciones: ${preferences?.nivel_animaciones || 'moderadas'}
- Prioriza precio: ${preferences?.prioriza_precio ? 'SÍ' : 'NO'}
- Prioriza tecnología: ${preferences?.prioriza_tecnologia ? 'SÍ' : 'NO'}
- Prioriza consumo: ${preferences?.prioriza_consumo ? 'SÍ' : 'NO'}

**CONTEXTO DEL DISPOSITIVO:**
- Dispositivo: ${context?.tipo_dispositivo || 'desktop'}
- Navegador: ${context?.navegador || 'moderno'}
- Sistema operativo: ${context?.sistema_operativo || 'unknown'}

${persona ? `**PERSONA SIMULADA:**
- Nombre: ${persona.nombre}
- Perfil: ${persona.tipo_cliente}, ${persona.edad} años, ${persona.region}` : ''}

**INSTRUCCIONES ESPECÍFICAS:**

1. **Estructura HTML:**
   - Genera HTML semántico válido
   - Usa SOLO clases de Tailwind CSS (no CSS custom)
   - Incluye estas secciones:
     * Hero section con título personalizado
     * Grid de 3 vehículos Mercedes-Benz relevantes
     * Call-to-action footer

2. **Personalización según perfil:**
   - Si tipo_cliente es "empresa": enfoca en flotas, TCO, vehículos comerciales (Sprinter, Vito)
   - Si tipo_cliente es "persona": enfoca en lujo, tecnología, vehículos premium (EQS, S-Class, GLE)

3. **Adaptación visual:**
   - Si densidad es "minimalista": usa spacing amplio (p-12, gap-8), texto grande
   - Si densidad es "compacta": usa spacing reducido (p-6, gap-4), texto normal
   - Si densidad es "maxima": usa spacing mínimo (p-4, gap-2), texto pequeño

4. **Color scheme:**
   - Si esquema es "oscuro": bg-gradient-to-br from-gray-900 via-black
   - Si esquema es "claro": bg-gradient-to-br from-gray-50 via-white
   - Si esquema es "lujo": bg-gradient-to-br from-purple-900 via-gray-900 to-black
   - Si esquema es "corporativo": bg-gradient-to-br from-blue-900 via-blue-800 to-black

5. **Destacar según prioridades:**
   - Si prioriza_tecnologia: destacar specs técnicas, MBUX, autonomía eléctrica
   - Si prioriza_precio: destacar precio, financiamiento, ofertas
   - Si prioriza_consumo: destacar eficiencia, consumo, TCO

6. **Responsive design:**
   - Usa clases responsive de Tailwind (md:, lg:)
   - Grid debe ser: grid-cols-1 md:grid-cols-3

7. **NO incluyas:**
   - Etiquetas <html>, <head>, <body>
   - Scripts de JavaScript
   - **Imágenes externas** (usa emojis, gradients de Tailwind o data URIs)
   - Enlaces a servicios de placeholder (via.placeholder.com, lorempixel, etc.)
   - Explicaciones o comentarios fuera del HTML

8. **Para imágenes de vehículos:**
   - Usa emojis de vehículos: 🚗 🚙 🚐 ⚡ 🏎️
   - O usa gradients de Tailwind con texto: bg-gradient-to-br from-blue-600 to-purple-600
   - O usa íconos SVG inline simples
   - NUNCA uses URLs externas de imágenes

**FORMATO DE RESPUESTA:**
Retorna ÚNICAMENTE el HTML del contenido (div principal con todo el diseño).
No uses markdown code blocks.
No incluyas explicaciones.
Solo el HTML puro con clases Tailwind.

Genera el HTML ahora:
`;
  }, []);

  // Función helper para generar UI de fallback cuando hay rate limit
  const generateFallbackUI = useCallback((params: GenerateUIParams): GeneratedUI => {
    const tipoCliente = params.user?.tipo_cliente || 'general';
    const colorScheme = params.preferences?.esquema_colores || 'moderno';
    
    const fallbackHTML = `
<div class="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
  <!-- Hero Section -->
  <div class="relative h-screen flex items-center justify-center overflow-hidden">
    <div class="absolute inset-0 bg-black/40"></div>
    <div class="relative z-10 text-center px-8">
      <h1 class="text-6xl md:text-8xl font-bold text-white mb-6 animate-fade-in">
        🚗 Mercedes-Benz
      </h1>
      <p class="text-2xl md:text-4xl text-blue-300 mb-8">
        ${tipoCliente === 'empresa' ? 'Soluciones Corporativas' : 'El Mejor o Nada'}
      </p>
      <div class="flex gap-4 justify-center">
        <button class="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xl font-semibold transition-all transform hover:scale-105">
          Explorar Vehículos
        </button>
        <button class="px-8 py-4 bg-white/10 hover:bg-white/20 text-white rounded-lg text-xl font-semibold backdrop-blur-sm transition-all">
          Contactar
        </button>
      </div>
    </div>
  </div>

  <!-- Vehículos Destacados -->
  <div class="max-w-7xl mx-auto px-8 py-20">
    <h2 class="text-4xl font-bold text-white mb-12 text-center">Vehículos Destacados</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Card 1 -->
      <div class="bg-white/10 backdrop-blur-lg rounded-2xl overflow-hidden hover:transform hover:scale-105 transition-all">
        <div class="h-48 bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center">
          <span class="text-6xl">🏎️</span>
        </div>
        <div class="p-6">
          <h3 class="text-2xl font-bold text-white mb-2">Mercedes-AMG GT</h3>
          <p class="text-blue-300 mb-4">Deportivo de alto rendimiento</p>
          <div class="flex justify-between items-center">
            <span class="text-white font-semibold">Desde $180,000</span>
            <button class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">Ver más</button>
          </div>
        </div>
      </div>

      <!-- Card 2 -->
      <div class="bg-white/10 backdrop-blur-lg rounded-2xl overflow-hidden hover:transform hover:scale-105 transition-all">
        <div class="h-48 bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center">
          <span class="text-6xl">⚡</span>
        </div>
        <div class="p-6">
          <h3 class="text-2xl font-bold text-white mb-2">Mercedes-Benz EQS</h3>
          <p class="text-purple-300 mb-4">Eléctrico de lujo</p>
          <div class="flex justify-between items-center">
            <span class="text-white font-semibold">Desde $105,000</span>
            <button class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg">Ver más</button>
          </div>
        </div>
      </div>

      <!-- Card 3 -->
      <div class="bg-white/10 backdrop-blur-lg rounded-2xl overflow-hidden hover:transform hover:scale-105 transition-all">
        <div class="h-48 bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center">
          <span class="text-6xl">🚙</span>
        </div>
        <div class="p-6">
          <h3 class="text-2xl font-bold text-white mb-2">Mercedes-Benz GLE</h3>
          <p class="text-green-300 mb-4">SUV premium</p>
          <div class="flex justify-between items-center">
            <span class="text-white font-semibold">Desde $75,000</span>
            <button class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg">Ver más</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Call to Action -->
  <div class="bg-gradient-to-r from-blue-600 to-purple-600 py-20">
    <div class="max-w-4xl mx-auto text-center px-8">
      <h2 class="text-4xl font-bold text-white mb-6">¿Listo para tu próximo Mercedes-Benz?</h2>
      <p class="text-xl text-white/90 mb-8">Agenda una prueba de manejo y descubre la excelencia alemana</p>
      <button class="px-12 py-4 bg-white text-blue-600 hover:bg-gray-100 rounded-lg text-xl font-semibold transition-all transform hover:scale-105">
        Agendar Prueba de Manejo
      </button>
    </div>
  </div>

  <!-- Footer Info -->
  <div class="bg-black/50 backdrop-blur-sm py-8 text-center">
    <p class="text-white/60 text-sm">
      ⚠️ UI de demostración - Gemini API temporalmente no disponible (rate limit)
    </p>
    <p class="text-white/40 text-xs mt-2">
      Este diseño se generará dinámicamente con IA cuando la cuota se restablezca
    </p>
  </div>
</div>
    `.trim();

    return {
      html: fallbackHTML,
      metadata: {
        model: 'fallback-mock',
        generated_at: new Date().toISOString(),
        layout_type: tipoCliente === 'empresa' ? 'executive' : 'standard'
      }
    };
  }, []);

  const generateUI = useCallback(async (params: GenerateUIParams): Promise<GeneratedUI | null> => {
    console.log('[useGeminiUI] Starting generation...');
    console.log('[useGeminiUI] API Key available:', !!GEMINI_API_KEY);
    console.log('[useGeminiUI] API URL:', GEMINI_API_URL);
    
    if (!GEMINI_API_KEY) {
      const errorMsg = 'Gemini API key no configurada';
      console.error('[useGeminiUI]', errorMsg);
      setError(errorMsg);
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const prompt = buildPrompt(params);
      console.log('[useGeminiUI] Prompt length:', prompt.length, 'chars');
      console.log('[useGeminiUI] Calling Gemini API...');

      const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                {
                  text: prompt
                }
              ]
            }
          ],
          generationConfig: {
            temperature: 0.9,
            topK: 40,
            topP: 0.95,
            maxOutputTokens: 8192,
          }
        })
      });

      console.log('[useGeminiUI] Response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('[useGeminiUI] API Error:', errorData);
        
        // Si es error 429 (rate limit), usar fallback
        if (response.status === 429) {
          console.warn('[useGeminiUI] Rate limit reached, using fallback UI');
          const fallback = generateFallbackUI(params);
          setGeneratedUI(fallback);
          if (typeof window !== 'undefined') {
            window.sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(fallback));
          }
          return fallback;
        }
        
        throw new Error(`Gemini API error: ${errorData.error?.message || response.statusText}`);
      }

      const data = await response.json();
      console.log('[useGeminiUI] Response received, candidates:', data.candidates?.length);
      
      // Extraer el texto generado
      const generatedText = data.candidates?.[0]?.content?.parts?.[0]?.text;
      
      if (!generatedText) {
        console.error('[useGeminiUI] No text in response:', data);
        throw new Error('No se recibió respuesta de Gemini');
      }

      console.log('[useGeminiUI] Generated HTML length:', generatedText.length, 'chars');

      // Limpiar el HTML (remover markdown code blocks si existen)
      let cleanedHTML = generatedText.trim();
      if (cleanedHTML.startsWith('```html')) {
        cleanedHTML = cleanedHTML.replaceAll(/```html\n?/g, '').replaceAll(/```\n?$/g, '').trim();
      } else if (cleanedHTML.startsWith('```')) {
        cleanedHTML = cleanedHTML.replaceAll(/```\n?/g, '').trim();
      }

      // 🔧 LIMPIAR URLs DE PLACEHOLDER QUE CAUSAN ERRORES DNS
      // Reemplazar via.placeholder.com con emojis o gradients
      const placeholderImgPattern = /<img[^>]+src=("|')https?:\/\/[^"']*(via\.placeholder\.com|placehold\.[a-z]+|lorempixel\.com)[^"']*("|')[^>]*>/gi;
      const placeholderSrcsetPattern = /<img[^>]+srcset=("|')[^"']*(via\.placeholder\.com|placehold\.[a-z]+|lorempixel\.com)[^"']*("|')[^>]*>/gi;
      const placeholderBgPattern = /url\(("|')?https?:\/\/[^\)"']*(via\.placeholder\.com|placehold\.[a-z]+|lorempixel\.com)[^\)"']*("|')?\)/gi;
      const placeholderAnyUrlPattern = /https?:\/\/[^\s"'>]*(via\.placeholder\.com|placehold\.[a-z]+|lorempixel\.com)[^\s"'>]*/gi;

      cleanedHTML = cleanedHTML.replace(
        placeholderImgPattern,
        '<div class="bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-6xl">🚗</div>'
      );

      cleanedHTML = cleanedHTML.replace(
        placeholderSrcsetPattern,
        ''
      );

      cleanedHTML = cleanedHTML.replace(
        placeholderBgPattern,
        'linear-gradient(135deg, #2563eb, #9333ea)'
      );

      cleanedHTML = cleanedHTML.replace(
        placeholderAnyUrlPattern,
        ''
      );

      if (/placeholder\.com|placehold\.|lorempixel\.com/i.test(cleanedHTML)) {
        console.warn('[useGeminiUI] Placeholder references remained after cleaning. Applying fallback replacements.');
        cleanedHTML = cleanedHTML.replace(/<img[^>]*>/gi, '<div class="bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-6xl">🚗</div>');
        cleanedHTML = cleanedHTML.replace(/placeholder/gi, 'mercedes-benz');
      }
      
      console.log('[useGeminiUI] HTML cleaned (removed placeholder images)');

      // Determinar layout type
      let layoutType = 'standard';
      if (params.user?.tipo_cliente === 'empresa') {
        layoutType = 'executive';
      } else if (params.preferences?.densidad_informacion === 'minimalista') {
        layoutType = 'luxury_minimal';
      }

      const result: GeneratedUI = {
        html: cleanedHTML,
        metadata: {
          model: 'gemini-1.5-flash',
          generated_at: new Date().toISOString(),
          layout_type: layoutType
        }
      };

      console.log('[useGeminiUI] ✅ UI generated successfully, layout:', layoutType);
      setGeneratedUI(result);
      if (typeof window !== 'undefined') {
        window.sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(result));
      }
      return result;

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido al generar UI';
      console.error('[useGeminiUI] ❌ Error:', errorMessage, err);
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
      console.log('[useGeminiUI] Generation finished');
    }
  }, [buildPrompt, generateFallbackUI]);

  return {
    generateUI,
    loading,
    error,
    generatedUI
  };
}

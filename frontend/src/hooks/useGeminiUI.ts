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
  estilo_imagenes?: string;
  nivel_animaciones?: string;
  preferencia_layout?: string;
  estilo_navegacion?: string;
  preferencia_visual?: string;
  modo_comparacion?: string;
  idioma_specs?: string;
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
    persona_id?: string; // ID de la persona para la que se generó
  };
}

const SESSION_STORAGE_KEY_PREFIX = 'efimero_ui_cache_v2_'; // v2 para invalidar cache antiguo

/**
 * Genera la clave de cache específica para una persona
 */
function getCacheKey(personaId?: string): string {
  return `${SESSION_STORAGE_KEY_PREFIX}${personaId || 'default'}`;
}

export function useGeminiUI() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiKeyError, setApiKeyError] = useState(false); // Nueva bandera para API key inválida
  const [generatedUI, setGeneratedUI] = useState<GeneratedUI | null>(null);
  const [currentPersonaId, setCurrentPersonaId] = useState<string | null>(null);

  /**
   * Carga el cache SOLO si es para la misma persona
   */
  const loadCachedUI = useCallback((personaId?: string): GeneratedUI | null => {
    if (typeof window === 'undefined') {
      return null;
    }

    try {
      const cacheKey = getCacheKey(personaId);
      const cached = window.sessionStorage.getItem(cacheKey);
      
      if (!cached) {
        console.log('[useGeminiUI] No cache found for persona:', personaId || 'default');
        return null;
      }

      const parsed = JSON.parse(cached) as GeneratedUI;
      
      // Validar que sea un objeto con HTML antes de usarlo
      if (parsed && typeof parsed.html === 'string') {
        console.log('[useGeminiUI] ✅ Loaded cached UI for persona:', personaId || 'default');
        return parsed;
      }
    } catch (cacheError) {
      console.warn('[useGeminiUI] Failed to parse cached UI:', cacheError);
    }

    return null;
  }, []);

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

**PREFERENCIAS VISUALES (11 campos - RESPETAR TODOS):**
1. Esquema de colores: ${preferences?.esquema_colores || 'moderno'}
2. Color favorito: ${preferences?.color_favorito || '#0EA5E9'}
3. Densidad de información: ${preferences?.densidad_informacion || 'comoda'}
4. Estilo tipográfico: ${preferences?.estilo_tipografia || 'moderna_geometrica'}
5. Estilo de imágenes: ${preferences?.estilo_imagenes || 'fotograficas'}
6. Nivel de animaciones: ${preferences?.nivel_animaciones || 'medio'}
7. Preferencia de layout: ${preferences?.preferencia_layout || 'cards'}
8. Estilo de navegación: ${preferences?.estilo_navegacion || 'horizontal'}
9. Preferencia visual: ${preferences?.preferencia_visual || 'equilibrada'}
10. Modo comparación: ${preferences?.modo_comparacion || 'lado_a_lado'}
11. Idioma de specs: ${preferences?.idioma_specs || 'tecnico'}

**PRIORIDADES:**
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
   - Si tipo_cliente es "empresa": enfoca en flotas, TCO, vehículos comerciales (Sprinter, Vito, eVito)
   - Si tipo_cliente es "persona": enfoca en lujo, tecnología, vehículos premium (EQS, S-Class, GLE, AMG)

3. **Adaptación de DENSIDAD DE INFORMACIÓN:**
   - Si densidad es "minimalista": espaciado amplio (p-12, gap-8, my-8), texto muy grande (text-xl, text-2xl), máximo 1 vehículo, mucho espacio en blanco
   - Si densidad es "comoda": espaciado moderado (p-6, gap-6, my-6), texto mediano (text-base, text-lg), 2-3 vehículos
   - Si densidad es "compacta": espaciado reducido (p-4, gap-4, my-4), texto normal (text-sm, text-base), 3-4 vehículos, cards más pequeñas
   - Si densidad es "amplia": espaciado generoso (p-8, gap-8, my-8), texto grande (text-lg, text-xl), 2 vehículos máximo

4. **Color scheme (esquema_colores) - CRÍTICO PARA ESTILOS:**
   **IMPORTANTE:** Para colores de fondo principales, USA ESTILOS INLINE para garantizar que se vean:
   
   - Si esquema es "oscuro": 
     * Container principal: style="background: linear-gradient(to bottom right, #111827, #000000, #111827);"
     * Texto: class="text-white"
   
   - Si esquema es "claro": 
     * Container principal: style="background: linear-gradient(to bottom right, #f9fafb, #ffffff, #f3f4f6);"
     * Texto: class="text-gray-900"
   
   - Si esquema es "lujo": 
     * Container principal: style="background: linear-gradient(to bottom right, #581c87, #1f2937, #000000);"
     * Acentos: style="color: #fbbf24;" (dorado)
   
   - Si esquema es "corporativo": 
     * Container principal: style="background: linear-gradient(to bottom right, #1e3a8a, #1e40af, #000000);"
     * Acentos: class="text-blue-400"
   
   - Si esquema es "moderno": 
     * Container principal: style="background: linear-gradient(to bottom right, #1f2937, #111827, #000000);"
     * Acentos: class="text-cyan-400"
   
   **Color favorito (${preferences?.color_favorito}):**
   - Usa SIEMPRE este color para botones principales con style="background-color: ${preferences?.color_favorito};"
   - Usa este color para borders importantes: style="border-color: ${preferences?.color_favorito};"
   - Usa este color para títulos destacados: style="color: ${preferences?.color_favorito};"

5. **Estilo TIPOGRÁFICO (estilo_tipografia):**
   - Si es "moderna_geometrica": usa font-sans, font-bold, tracking-tight, letras limpias
   - Si es "clasica_serif": usa font-serif, font-normal, tracking-normal, elegancia tradicional
   - Si es "sans-serif": usa font-sans, font-medium, tracking-normal, claridad

6. **Nivel de ANIMACIONES (nivel_animaciones) - MUY IMPORTANTE:**
   - Si nivel es "bajo" o "minimo": NO uses transition, NO uses animate-*, elementos estáticos
   - Si nivel es "medio" o "moderado": usa transition-all duration-300, hover:scale-105 moderado
   - Si nivel es "alto" o "maximo": usa transition-all duration-150, animate-pulse, animate-bounce, hover:scale-110, efectos fluidos

7. **Preferencia de LAYOUT (preferencia_layout):**
   - Si es "grid": usa grid grid-cols-1 md:grid-cols-3, distribución cuadrícula
   - Si es "lista": usa flex flex-col gap-4, diseño vertical lineal
   - Si es "cards": usa grid con cards elevadas (shadow-xl, rounded-xl, border)
   - Si es "minimalista": usa flex con mucho espacio, borders sutiles

8. **Estilo de NAVEGACIÓN (estilo_navegacion):**
   - Si es "horizontal": barra nav en top con flex flex-row
   - Si es "vertical": sidebar con flex flex-col
   - Si es "hamburger": menú oculto para móvil
   - Si es "tabs": pestañas horizontales con border-b

9. **Preferencia VISUAL (preferencia_visual):**
   - Si es "minimalista": máximo espacio en blanco, colores neutros, sin bordes
   - Si es "maximalista": colores vibrantes, muchos elementos, borders gruesos
   - Si es "equilibrada": balance entre elementos y espacio

10. **Modo COMPARACIÓN (modo_comparacion):**
    - Si es "lado_a_lado": grid de vehículos con md:grid-cols-2 o md:grid-cols-3
    - Si es "tabla": estructura de tabla con borders
    - Si es "lista": stack vertical con separadores

11. **Idioma de SPECS (idioma_specs):**
    - Si es "tecnico": usa términos como "kW", "Nm", "0-100 km/h", "WLTP"
    - Si es "simple": usa "Potencia", "Velocidad", "Consumo" sin tecnicismos
    - Si es "casual": usa lenguaje natural "Rápido", "Eficiente", "Potente"

12. **Destacar según prioridades:**
    - Si prioriza_tecnologia: destacar specs técnicas, MBUX, autonomía eléctrica, sistemas de asistencia
    - Si prioriza_precio: destacar precio grande, financiamiento, ofertas, descuentos
    - Si prioriza_consumo: destacar eficiencia, consumo, TCO, eléctricos (EQS, EQE, eVito)

13. **Responsive design:**
    - Usa clases responsive de Tailwind (md:, lg:)
    - Grid debe adaptarse: grid-cols-1 md:grid-cols-2 lg:grid-cols-3

14. **NO incluyas:**
    - Etiquetas <html>, <head>, <body>
    - Scripts de JavaScript
    - **Imágenes externas** (usa emojis, gradients de Tailwind o data URIs)
    - Enlaces a servicios de placeholder (via.placeholder.com, lorempixel, etc.)
    - Explicaciones o comentarios fuera del HTML

15. **Para imágenes de vehículos:**
    - Usa emojis relevantes: 🚗 🚙 🚐 ⚡ 🏎️ 🔋 (eléctricos con ⚡)
    - O usa gradients con style inline: style="background: linear-gradient(to bottom right, #2563eb, #7c3aed);"
    - O usa SVG inline simples
    - NUNCA uses URLs externas de imágenes

**REGLAS CRÍTICAS PARA COLORES:**
1. El div contenedor principal DEBE tener style inline para el fondo basado en esquema_colores
2. Los botones principales DEBEN usar style="background-color: ${preferences?.color_favorito};"
3. Los títulos importantes DEBEN usar style="color: ${preferences?.color_favorito};"
4. Combina clases Tailwind (para spacing, typography) CON estilos inline (para colores)

**EJEMPLO DE ESTRUCTURA CORRECTA:**
\`\`\`html
<div style="background: linear-gradient(to bottom right, #1e3a8a, #1e40af, #000000); min-height: 100vh;" class="p-8">
  <h1 style="color: ${preferences?.color_favorito};" class="text-5xl font-bold mb-6">
    Título personalizado
  </h1>
  <button style="background-color: ${preferences?.color_favorito};" class="px-6 py-3 text-white rounded-lg">
    Acción principal
  </button>
</div>
\`\`\`

**FORMATO DE RESPUESTA:**
Retorna ÚNICAMENTE el HTML del contenido (div principal con todo el diseño).
No uses markdown code blocks.
No incluyas explicaciones.
Solo el HTML puro que combine clases Tailwind Y estilos inline para colores.

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
    
    // Generar ID único para cache basado en persona o usuario
    const personaId = params.persona?.nombre 
      ? `${params.persona.nombre}_${params.persona.edad}`
      : params.user?.tipo_cliente 
        ? `${params.user.tipo_cliente}_${params.user.edad || 'unknown'}`
        : 'default';
    
    console.log('[useGeminiUI] 👤 Persona ID for cache:', personaId);
    console.log('[useGeminiUI] 📋 Params received:', {
      hasPersona: !!params.persona,
      personaName: params.persona?.nombre,
      hasUser: !!params.user,
      userType: params.user?.tipo_cliente
    });
    
    // Detectar si cambió la persona
    const personaChanged = personaId !== currentPersonaId;
    
    if (personaChanged) {
      console.log('[useGeminiUI] 🔄 Persona changed from', currentPersonaId, 'to', personaId);
      setCurrentPersonaId(personaId || null);
      setGeneratedUI(null); // Limpiar UI anterior
      
      // NO buscar cache si cambió la persona - forzar nueva generación
      console.log('[useGeminiUI] 🚫 Skipping cache lookup - persona changed');
    } else {
      // Solo buscar cache si NO cambió la persona
      const cachedUI = loadCachedUI(personaId);
      if (cachedUI) {
        console.log('[useGeminiUI] ✅ Using cached UI for same persona:', personaId);
        setGeneratedUI(cachedUI);
        return cachedUI;
      } else {
        console.log('[useGeminiUI] 📭 No cache found for persona:', personaId);
      }
    }
    
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
        
        // Detectar API key inválida o leaked
        const errorMessage = errorData.error?.message || '';
        if (errorMessage.includes('API key') && (errorMessage.includes('leaked') || errorMessage.includes('invalid'))) {
          console.error('[useGeminiUI] ❌ API Key inválida o comprometida');
          setApiKeyError(true);
          setError('API key inválida o comprometida. Por favor, configura una nueva API key en las variables de entorno.');
          
          // NO usar fallback - mostrar error crítico
          setLoading(false);
          return null;
        }
        
        // Si es error 429 (rate limit), usar fallback
        if (response.status === 429) {
          console.warn('[useGeminiUI] Rate limit reached, using fallback UI');
          const fallback = generateFallbackUI(params);
          fallback.metadata.persona_id = personaId;
          setGeneratedUI(fallback);
          if (typeof window !== 'undefined') {
            const cacheKey = getCacheKey(personaId);
            window.sessionStorage.setItem(cacheKey, JSON.stringify(fallback));
          }
          return fallback;
        }
        
        throw new Error(`Gemini API error: ${errorMessage || response.statusText}`);
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
          model: 'gemini-2.0-flash',
          generated_at: new Date().toISOString(),
          layout_type: layoutType,
          persona_id: personaId
        }
      };

      console.log('[useGeminiUI] ✅ UI generated successfully, layout:', layoutType, 'persona:', personaId);
      setGeneratedUI(result);
      if (typeof window !== 'undefined') {
        const cacheKey = getCacheKey(personaId);
        window.sessionStorage.setItem(cacheKey, JSON.stringify(result));
        console.log('[useGeminiUI] 💾 Cached UI with key:', cacheKey);
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
  }, [buildPrompt, generateFallbackUI, loadCachedUI, currentPersonaId]);

  return {
    generateUI,
    loading,
    error,
    generatedUI,
    apiKeyError
  };
}

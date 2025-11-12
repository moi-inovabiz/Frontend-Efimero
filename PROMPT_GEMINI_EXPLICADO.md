# 📄 Prompt enviado a Gemini AI - Frontend Efímero

## 🎯 Resumen Ejecutivo

Cuando presionas el botón **"Frontend Efímero Personalizado"**, se envía un prompt de ~200 líneas a **Gemini 2.0 Flash** que incluye:

1. **Rol del asistente**: Diseñador UI/UX experto en e-commerce automotriz Mercedes-Benz
2. **Datos del usuario**: Tipo de cliente, edad, región, intereses, presupuesto
3. **Preferencias visuales**: 11 campos (color, densidad, tipografía, animaciones, etc.)
4. **Contexto del dispositivo**: Tipo de dispositivo, navegador, SO
5. **Persona simulada**: Datos del perfil genérico asignado
6. **Instrucciones detalladas**: 8 reglas específicas para generar el HTML

---

## 📊 Fuentes de Datos

### **1. Datos del Usuario (si está autenticado)**
Viene de la tabla `usuarios` en la base de datos:
- `tipo_cliente`: "persona" | "empresa"
- `edad`: Número (opcional)
- `region`: "Metropolitana", "Valparaíso", etc.
- `interes_principal`: ["lujo", "tecnologia", "deportivo"]
- `presupuesto`: "bajo" | "medio" | "alto" | "premium"

### **2. Preferencias Visuales (del usuario autenticado)**
11 campos configurables:
- `esquema_colores`: "automatico" | "claro" | "oscuro" | "alto_contraste" | "lujo" | "corporativo" | "moderno"
- `color_favorito`: "azul" | "verde" | "rojo" | "amarillo" | "morado" | "rosa" | "cyan" | "naranja"
- `densidad_informacion`: "minimalista" | "comoda" | "compacta" | "maxima"
- `estilo_tipografia`: "moderna_geometrica" | "elegante_serif" | "technica_monospace" | "humanista_sans" | "clasica_tradicional"
- `nivel_animaciones`: "ninguna" | "sutiles" | "moderadas" | "dinamicas"
- `prioriza_precio`: boolean
- `prioriza_tecnologia`: boolean
- `prioriza_consumo`: boolean
- Y más...

### **3. Contexto Efímero (del navegador)**
Detectado automáticamente:
- `tipo_dispositivo`: "mobile" | "tablet" | "desktop"
- `navegador`: "Chrome", "Firefox", "Safari", etc.
- `sistema_operativo`: "Windows", "macOS", "Linux", "iOS", "Android"

### **4. Persona Simulada**
Del sistema de matching inteligente (26 perfiles):
- `nombre`: "Carmen Rivera", "Transportes Del Sur", etc.
- `tipo_cliente`: "persona" | "empresa"
- `edad`: 25-65 años
- `region`: Región de Chile

---

## 📝 Ejemplo de Prompt Real

Aquí está el prompt EXACTO que se envía a Gemini cuando un usuario empresa de 42 años hace click:

\`\`\`
Eres un diseñador UI/UX experto especializado en e-commerce automotriz Mercedes-Benz.

Tu tarea es generar un diseño HTML completo usando Tailwind CSS para una landing page personalizada.

**INFORMACIÓN DEL USUARIO:**
- Tipo de cliente: empresa
- Edad: 42
- Región: Metropolitana
- Intereses: flotas, tco, logistica
- Presupuesto: alto

**PREFERENCIAS VISUALES:**
- Esquema de colores: corporativo
- Color favorito: azul
- Densidad de información: compacta
- Estilo tipográfico: moderna_geometrica
- Nivel de animaciones: sutiles
- Prioriza precio: NO
- Prioriza tecnología: SÍ
- Prioriza consumo: SÍ

**CONTEXTO DEL DISPOSITIVO:**
- Dispositivo: desktop
- Navegador: Chrome
- Sistema operativo: Windows

**PERSONA SIMULADA:**
- Nombre: Transportes Del Sur
- Perfil: empresa, 45 años, Valparaíso

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
\`\`\`

---

## 🎨 Resultado Esperado

Gemini genera un HTML personalizado como este (ejemplo simplificado):

\`\`\`html
<div class="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-black">
  <!-- Hero Section -->
  <div class="relative h-screen flex items-center justify-center">
    <div class="relative z-10 text-center px-6">
      <h1 class="text-7xl font-bold text-white mb-4">
        Soluciones Corporativas Mercedes-Benz
      </h1>
      <p class="text-2xl text-blue-300 mb-8">
        Optimiza tu flota con eficiencia alemana
      </p>
      <button class="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
        Calcular TCO
      </button>
    </div>
  </div>

  <!-- Grid de Vehículos -->
  <div class="max-w-7xl mx-auto px-6 py-16">
    <h2 class="text-4xl font-bold text-white mb-10">Vehículos Comerciales</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Card 1: Sprinter -->
      <div class="bg-white/10 backdrop-blur-lg rounded-xl p-6">
        <div class="h-40 bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center rounded-lg mb-4">
          <span class="text-6xl">🚐</span>
        </div>
        <h3 class="text-2xl font-bold text-white mb-2">Mercedes-Benz Sprinter</h3>
        <p class="text-blue-300 mb-4">Capacidad de carga excepcional</p>
        <div class="space-y-2 text-sm text-white/80">
          <div>✓ Consumo: 8.5L/100km</div>
          <div>✓ Carga útil: 3,500kg</div>
          <div>✓ TCO optimizado 5 años</div>
        </div>
        <button class="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded">
          Cotizar
        </button>
      </div>

      <!-- Cards 2 y 3 similares... -->
    </div>
  </div>

  <!-- Call to Action -->
  <div class="bg-gradient-to-r from-blue-600 to-blue-800 py-16">
    <div class="max-w-4xl mx-auto text-center px-6">
      <h2 class="text-4xl font-bold text-white mb-4">¿Listo para optimizar tu flota?</h2>
      <p class="text-xl text-white/90 mb-8">Calculemos el TCO de tu flota ideal</p>
      <button class="px-12 py-4 bg-white text-blue-600 rounded-lg font-bold">
        Solicitar Análisis de Flota
      </button>
    </div>
  </div>
</div>
\`\`\`

---

## 🔍 Características Clave del Prompt

### **1. Personalización Extrema**
- **64+ campos** combinados influyen en el diseño
- Cada usuario ve un frontend **único**

### **2. Instrucciones Muy Específicas**
- 8 reglas detalladas para evitar errores
- Prohibiciones explícitas (imágenes externas, scripts JS)
- Formato de respuesta estricto (solo HTML, sin explicaciones)

### **3. Adaptación Contextual**
- **Empresa**: Enfoque en TCO, eficiencia, flotas
- **Persona**: Enfoque en lujo, tecnología, experiencia

### **4. Tailwind CSS Puro**
- NO se permite CSS custom
- Diseño responsive con breakpoints (md:, lg:)
- Componentes modernos (backdrop-blur, gradients)

### **5. Sin Dependencias Externas**
- Usa emojis en lugar de imágenes (🚗🚙⚡)
- Gradientes de Tailwind para fondos
- SVG inline para iconos simples

---

## 📈 Flujo Completo

\`\`\`
1. Usuario → Click "Frontend Efímero Personalizado"
   ↓
2. Frontend → Recolecta datos:
   - AuthContext → user (si autenticado)
   - useEphemeralContext → contextData (navegador)
   - usePersona → personaData (perfil simulado)
   ↓
3. buildPrompt() → Construye prompt de ~3000 chars
   ↓
4. fetch() → Gemini 2.0 Flash API
   - URL: generativelanguage.googleapis.com
   - Body: { contents: [{ parts: [{ text: prompt }] }] }
   - Config: { temperature: 0.9, topK: 40, topP: 0.95, maxOutputTokens: 8192 }
   ↓
5. Gemini → Genera HTML (2000-5000 chars)
   ↓
6. cleanHTML() → Limpia respuesta:
   - Remueve markdown code blocks
   - Elimina URLs de placeholder
   - Reemplaza imágenes externas con emojis
   ↓
7. dangerouslySetInnerHTML → Renderiza HTML generado
   ↓
8. Usuario → Ve frontend personalizado único
\`\`\`

---

## ⚙️ Configuración Técnica

### **Modelo usado:**
- **Gemini 2.0 Flash** (gemini-2.0-flash)
- Rápido (~3-5 segundos de generación)
- 1M tokens de contexto (input)
- 8,192 tokens de salida (output)

### **Parámetros de generación:**
\`\`\`javascript
{
  temperature: 0.9,    // Alta creatividad
  topK: 40,           // Diversidad de tokens
  topP: 0.95,         // Núcleo de probabilidad
  maxOutputTokens: 8192  // ~2000 palabras de HTML
}
\`\`\`

### **Costo estimado:**
- **Input**: ~3000 tokens × $0.075 / 1M = $0.000225
- **Output**: ~2000 tokens × $0.30 / 1M = $0.0006
- **Total por request**: ~$0.001 (un décimo de centavo)

---

## 🎯 Casos de Uso

### **Caso 1: Usuario Joven (Persona)**
\`\`\`
- Tipo: persona, 28 años
- Preferencias: lujo, color morado, animaciones dinámicas
- Resultado: UI con gradientes purple/pink, animaciones fluidas, enfoque en EQS eléctrico
\`\`\`

### **Caso 2: Empresa de Logística**
\`\`\`
- Tipo: empresa, 45 años
- Preferencias: corporativo, color azul, densidad compacta
- Resultado: UI azul oscuro, enfoque en Sprinter/Vito, calculadora TCO destacada
\`\`\`

### **Caso 3: Usuario Premium**
\`\`\`
- Tipo: persona, 55 años
- Preferencias: lujo, minimalista, animaciones sutiles
- Resultado: UI elegante con mucho espacio en blanco, enfoque en S-Class/AMG
\`\`\`

---

## 🔧 Archivo de Código

El prompt está en: `frontend/src/hooks/useGeminiUI.ts`

Función: `buildPrompt()` (líneas 92-205)

---

## 📚 Documentación Adicional

- Propuesta completa: `openspec/changes/implement-gemini-canva-efimero/proposal.md`
- Análisis del estado: `ANALISIS_ESTADO_COMPLETO.md`
- Código del hook: `frontend/src/hooks/useGeminiUI.ts`
- Página de generación: `frontend/src/app/efimero/page.tsx`
- Página de visualización: `frontend/src/app/efimerocompleto/page.tsx`

---

**Última actualización**: 12 de Noviembre, 2025

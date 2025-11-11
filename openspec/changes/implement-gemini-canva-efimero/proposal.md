# Change Proposal: Frontend Efímero con Gemini AI

**Status**: 🟡 Propuesta  
**Fecha**: 2025-11-11  
**Autor**: Sistema  
**Prioridad**: Media  
**Complejidad**: Media  

---

## 📋 Resumen Ejecutivo

Implementar un **frontend completamente generado por Gemini AI** usando llamadas directas a la API desde el cliente. El objetivo es crear una experiencia de UI única por usuario basándose en su contexto completo (64+ campos), sin afectar el sistema actual.

**Enfoque**: Gemini API directa desde frontend (sin backend intermediario)

**Concepto clave**: Dos frontends paralelos
- **`/`** → Sistema actual (intacto) ✅
- **`/efimero`** → Frontend generado por Gemini AI (nuevo) 🤖

---

## 🎯 Objetivos

### Objetivos Principales
1. **Personalización extrema**: UI generada dinámicamente por IA según contexto del usuario
2. **Experimentación segura**: Probar generación de UI sin romper sistema actual
3. **Gemini API directa**: Llamadas desde frontend sin backend intermediario
4. **HTML/CSS generado**: Gemini crea código Tailwind personalizado
5. **A/B Testing**: Comparar engagement entre frontend estático vs generado por IA

### Objetivos Secundarios
- Reducir tiempo de diseño manual
- Aumentar conversión con UI optimizada por IA
- Experimentar con LLM-generated UI
- Escalar personalización sin multiplicar código

---

## 🏗️ Arquitectura Propuesta

### Stack Técnico Simplificado

```yaml
Frontend:
  /efimero:
    ruta: src/app/efimero/page.tsx ✅ (ya creada)
    hooks: useGeminiUI.ts (a crear)
    rendering: dangerouslySetInnerHTML o react-jsx-parser
    
  API Integration:
    gemini_api: Directa desde cliente
    endpoint: https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent
    auth: API key en NEXT_PUBLIC_GEMINI_API_KEY

Backend:
  Sin cambios: ✅ Reutiliza auth, ML, personas existentes
  No servicio adicional necesario
```

### Flujo de Datos

```
Usuario → /efimero
  ↓
1. Frontend recolecta contexto completo:
   - useAuth() → user profile
   - useEphemeralContext() → 45+ campos automáticos
   - usePersona() → persona simulada
   - (Opcional) XGBoost predictions
  ↓
2. useGeminiUI hook construye prompt:
   - Incluye todas las preferencias visuales
   - Incluye datos demográficos
   - Incluye intereses y prioridades
  ↓
3. Fetch directo a Gemini API:
   POST https://generativelanguage.googleapis.com/.../generateContent
   Headers: { 'x-goog-api-key': API_KEY }
   Body: { prompt con contexto completo }
  ↓
4. Gemini retorna HTML+Tailwind generado
  ↓
5. Frontend renderiza con seguridad:
   - Sanitiza HTML
   - Valida estructura
   - Renderiza con dangerouslySetInnerHTML
  ↓
6. Usuario ve UI única generada para él
```

---

## 🎨 Casos de Uso

### Caso 1: Layout Personalizado por Tipo de Usuario

**Input a Gemini**:
```json
{
  "user": {
    "tipo_cliente": "empresa",
    "edad": 42,
    "region": "Metropolitana",
    "intereses": ["flotas", "tco"]
  },
  "preferences": {
    "esquema_colores": "corporativo",
    "densidad_informacion": "compacta"
  },
  "ml_prediction": {
    "interes": "alto",
    "score": 0.85
  }
}
```

**Output de Gemini**:
```json
{
  "layout_type": "executive_dashboard",
  "hero": {
    "title": "Optimiza tu flota con Mercedes-Benz",
    "subtitle": "Soluciones comerciales para Santiago",
    "gradient": ["#1e40af", "#1e3a8a"],
    "cta_text": "Calcular TCO"
  },
  "sections": [
    {
      "type": "vehicle-comparison",
      "vehicles": ["Sprinter", "Vito", "eSprinter"],
      "highlight_metric": "tco"
    },
    {
      "type": "roi-calculator",
      "preset": "fleet_25_vehicles"
    },
    {
      "type": "financing",
      "product": "leasing_empresarial"
    }
  ]
}
```

### Caso 2: Contenido Adaptado a Prioridades

**Usuario que prioriza tecnología**:
```typescript
// Gemini genera enfoque tech
{
  hero_title: "EQS: Tecnología eléctrica de vanguardia",
  product_cards: [
    {
      vehicle: "EQS",
      highlighted_features: [
        "MBUX Hyperscreen",
        "678 km autonomía",
        "Carga rápida 200kW"
      ],
      layout: "tech_specs_prominent"
    }
  ]
}
```

**Usuario que prioriza precio**:
```typescript
// Gemini genera enfoque económico
{
  hero_title: "Mercedes-Benz accesible para ti",
  product_cards: [
    {
      vehicle: "Clase A",
      highlighted_features: [
        "Desde $32.990.000",
        "Financiamiento 0%",
        "Bajo costo mantención"
      ],
      layout: "price_prominent"
    }
  ]
}
```

### Caso 3: HTML Generado Dinámicamente

**Gemini genera HTML completo con Tailwind**:
```html
<div class="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-black">
  <header class="p-12">
    <h1 class="text-7xl font-black text-white mb-4">
      Hola Juan, tu Mercedes-Benz ideal te espera
    </h1>
    <p class="text-2xl text-blue-300">
      Basado en tus preferencias: tecnología y sostenibilidad
    </p>
  </header>
  
  <main class="container mx-auto px-12 py-8">
    <div class="grid grid-cols-2 gap-8">
      <!-- EQS Card - destacando tech -->
      <div class="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-blue-500/50">
        <h2 class="text-4xl font-bold text-white mb-4">Mercedes-Benz EQS</h2>
        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <span class="text-3xl">⚡</span>
            <span class="text-xl text-blue-200">678 km autonomía</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-3xl">🖥️</span>
            <span class="text-xl text-blue-200">MBUX Hyperscreen 56"</span>
          </div>
        </div>
        <button class="mt-6 w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl">
          Explorar EQS
        </button>
      </div>
      
      <!-- Más cards... -->
    </div>
  </main>
</div>
```

---

## 📊 Integración con Sistema Actual

### ✅ NO Rompe Nada

| Componente Actual | Cambio | Riesgo |
|-------------------|--------|--------|
| `server-theme.ts` | ❌ No tocar | 0% |
| `AuthContext` | ❌ No tocar | 0% |
| `useEphemeralContext` | ❌ No tocar | 0% |
| `usePersona` | ❌ No tocar | 0% |
| XGBoost ML | ✅ Reutilizar predictions | 0% |
| `/dashboard` | ❌ No tocar | 0% |
| `/demo` | ✅ Agregar botón | 1% |

### ➕ Solo Agrega

- **2 servicios nuevos** (puertos separados 8001, 8002)
- **3 endpoints nuevos** (`/visual-assets/*`)
- **1 ruta nueva** (`/efimero`)
- **2 archivos nuevos** (server-assets.ts, useVisualAssets.ts)

### 🛡️ Protecciones

```typescript
// Feature flags
ENABLE_VISUAL_ASSETS=false (default)
ENABLE_GEMINI_ORCHESTRATOR=false

// Fallbacks siempre
try {
  const asset = await canvaService.generate();
} catch {
  return '/static/default-hero.jpg'; // Sistema actual
}

// Timeouts
await fetch(geminiService, { timeout: 2000 });

// A/B Testing gradual
if (user.id % 10 === 0) {
  // Solo 10% ve nuevo sistema
}
```

---

## 💰 Costos Estimados

### Gemini API (ÚNICO costo)
- **Gemini 1.5 Flash** (recomendado):
  - Input: $0.075 / 1M tokens
  - Output: $0.30 / 1M tokens
  - Prompt por request: ~3000 tokens
  - HTML generado: ~2000 tokens
  - **Costo por request: ~$0.001**
  
- **10,000 usuarios/día**:
  - Sin cache: 10,000 × $0.001 = **$10/día** = **$300/mes**
  - Con cache localStorage: ~$100/mes (33% rehits)
  - **Muy económico** para experimentar

### Infraestructura
- **Frontend**: Ya existente (Next.js)
- **Backend**: Ya existente (no cambios)
- **Cache**: localStorage (gratis) o sessionStorage
- **CDN**: Vercel/Netlify (gratis en tier free)

### **Total Estimado**: $100-300/mes
- Ideal para experimentación
- Escala bien con cache
- Sin costos de infraestructura adicional

---

## 📅 Plan de Implementación

### Fase 0: Preparación (2 días)
```
✅ Crear /efimero route (HECHO)
✅ Agregar botón en /demo (HECHO)
⏳ Configurar Canva Developer account
⏳ Configurar Google AI Studio (Gemini)
⏳ Crear servicios/gemini/ folder
⏳ Crear servicios/canva/ folder
⏳ Actualizar docker-compose.yml
```

### Fase 1: Hero Banner SSR (1 semana)
```
⏳ Crear server-assets.ts
⏳ Crear endpoint /visual-assets/generate-hero
⏳ Implementar Gemini service (8001)
⏳ Implementar Canva service (8002)
⏳ Crear templates en Canva
⏳ Integrar en /efimero
⏳ Testing con feature flag off
```

### Fase 2: Product Cards (1 semana)
```
⏳ Crear useVisualAssets hook
⏳ Endpoint /visual-assets/generate-product-cards
⏳ Templates Canva para cards
⏳ Batch generation (5-10 cards paralelo)
⏳ Lazy loading optimizado
⏳ A/B testing 10% usuarios
```

### Fase 3: Optimización (3 días)
```
⏳ Redis cache layer
⏳ CDN para assets Canva
⏳ Preload assets críticos
⏳ Monitoreo performance
⏳ Alertas si > 500ms
```

### Fase 4: Analytics (2 días)
```
⏳ Trackear engagement
⏳ Comparar conversión vs sistema actual
⏳ A/B testing automático
⏳ Dashboard de métricas
```

---

## 🎯 Métricas de Éxito

### KPIs Principales
- **Time to First Contentful Paint**: < 1s (con cache)
- **Engagement rate**: +20% vs sistema actual
- **Conversion rate**: +15% vs sistema actual
- **Cache hit rate**: > 80%

### KPIs Secundarios
- **Asset generation time**: < 500ms (P95)
- **Gemini decision time**: < 200ms
- **Error rate**: < 1%
- **Cost per user**: < $0.02

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Canva API lenta | Media | Alto | Cache 24h, fallback estático |
| Gemini hallucinations | Baja | Medio | Validación decisiones, templates fijos |
| Costos altos | Media | Medio | Cache agresivo, rate limiting |
| Calidad inconsistente | Media | Alto | A/B testing, human review templates |
| Dependencia externa | Alta | Alto | Fallback siempre, monitoreo 24/7 |

---

## 🚀 Próximos Pasos

1. **Aprobar propuesta** → Crear tasks.md
2. **Setup cuentas** → Canva + Gemini API keys
3. **Implementar Fase 1** → Hero banner funcional
4. **Testing interno** → Team review con feature flag
5. **A/B testing 10%** → Medir engagement
6. **Rollout gradual** → 10% → 50% → 100%
7. **Iterar** → Mejorar basado en datos

---

## 📚 Referencias

- [Canva Dev MCP Documentation](https://canva.dev/mcp)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Model Context Protocol Spec](https://modelcontextprotocol.io/)
- Sistema actual: `openspec/changes/add-login-visual-preferences/`

---

## ✅ Checklist de Implementación

### Preparación
- [x] Crear `/efimero` route
- [x] Agregar botón en `/demo`
- [x] Documentar propuesta
- [ ] Obtener API keys (Canva + Gemini)
- [ ] Setup servicios Docker

### Desarrollo
- [ ] Gemini service (Python/FastAPI)
- [ ] Canva service (Node.js/Express)
- [ ] server-assets.ts (SSR extension)
- [ ] useVisualAssets hook
- [ ] Templates Canva (5+ variantes)

### Testing
- [ ] Unit tests (servicios)
- [ ] Integration tests (flujo completo)
- [ ] Performance tests (< 1s load)
- [ ] A/B testing framework

### Deployment
- [ ] Feature flags configurados
- [ ] Monitoreo setup
- [ ] Alertas configuradas
- [ ] Rollback plan documentado

---

**Estado Actual**: Fase 0 parcialmente completa (ruta + botón creados). Pendiente configuración de APIs y servicios backend.

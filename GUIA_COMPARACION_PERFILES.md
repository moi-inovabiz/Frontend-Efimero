# 📊 Guía: Comparación de Perfiles en Frontend Efímero

## 🎯 Funcionalidad Implementada

Ahora es posible **seleccionar diferentes perfiles de usuario en la Demo Adaptativa y ver cómo cambia el Frontend Efímero** generado por Gemini AI según las preferencias visuales de cada perfil.

## 🔄 Flujo Completo de Datos

```
┌─────────────────────────────────────────────────────────────────────────┐
│  1. DEMO ADAPTATIVA (/demo)                                             │
│     - Usuario ve perfiles genéricos                                     │
│     - Usa <PersonaSelector> para elegir un perfil                       │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  2. HOOK usePersona                                                      │
│     - assignSpecificPersona(personaId) se ejecuta                       │
│     - Backend retorna Persona completa con 11 campos de preferencias    │
│     - Se guarda en localStorage (persiste 24h)                          │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  3. NAVEGACIÓN A FRONTEND EFÍMERO (/efimero)                            │
│     - Usuario hace clic en "Frontend Efímero Personalizado"            │
│     - La página carga con la Persona activa                             │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  4. CONSTRUCCIÓN DE PARÁMETROS (efimero/page.tsx)                       │
│     - Lee Persona via usePersona()                                      │
│     - Extrae TODOS los campos de preferencias:                          │
│       * esquema_colores, color_favorito, densidad_informacion           │
│       * estilo_tipografia, estilo_imagenes, nivel_animaciones           │
│       * preferencia_layout, estilo_navegacion, preferencia_visual       │
│       * modo_comparacion, idioma_specs                                  │
│     - Prioridad: Persona > User autenticado > Defaults                  │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  5. GENERACIÓN DEL PROMPT (useGeminiUI.ts)                              │
│     - buildPrompt() crea prompt de 200+ líneas                          │
│     - Incluye las 11 preferencias visuales con instrucciones específicas│
│     - Envía a Gemini 2.0 Flash                                          │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  6. GEMINI AI GENERA HTML                                               │
│     - Analiza todas las preferencias                                    │
│     - Genera HTML con Tailwind CSS personalizado                        │
│     - Respeta densidad, colores, animaciones, layout, etc.              │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  7. RENDERIZADO Y COMPARACIÓN                                           │
│     - Usuario ve landing page Mercedes-Benz personalizada              │
│     - Puede volver a /demo, cambiar de perfil                           │
│     - Ver claramente las diferencias entre perfiles                     │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📝 Ejemplo de Uso

### Paso 1: Abrir Demo Adaptativa
```
http://localhost:3000/demo
```

### Paso 2: Seleccionar un Perfil
- Usar el selector de personas (botón "👤 Personas" en la esquina)
- Elegir, por ejemplo: **"Carlos Empresario"** (empresa, 42 años)
  - Preferencias: Corporativo, densidad compacta, sin animaciones

### Paso 3: Generar Frontend Efímero
- Hacer clic en **"Frontend Efímero Personalizado"**
- Esperar 3-5 segundos mientras Gemini genera
- Ver landing page adaptada a Carlos:
  - ✅ Esquema corporativo (azul oscuro)
  - ✅ Densidad compacta (más información en menos espacio)
  - ✅ Sin animaciones (nivel bajo)
  - ✅ Enfoque en flotas y vehículos comerciales (Sprinter, Vito)

### Paso 4: Comparar con Otro Perfil
- Hacer clic en **"← Volver a Demo"** (botón en la esquina)
- En /demo, cambiar a **"Sofía Joven"** (persona, 28 años)
  - Preferencias: Lujo, densidad amplia, animaciones altas
- Volver a hacer clic en **"Frontend Efímero Personalizado"**
- Ver landing page adaptada a Sofía:
  - ✅ Esquema de lujo (púrpura/dorado)
  - ✅ Densidad amplia (mucho espacio en blanco)
  - ✅ Animaciones fluidas (alto nivel)
  - ✅ Enfoque en vehículos premium (EQS, S-Class, AMG)

## 🎨 Campos de Preferencias Respetados

### 1. **esquema_colores**
| Valor | Efecto en Gemini |
|-------|------------------|
| `oscuro` | Fondo negro/gris 900, texto blanco |
| `claro` | Fondo blanco/gris 50, texto oscuro |
| `lujo` | Púrpura 900 + negro, acentos dorados |
| `corporativo` | Azul 900 + azul 800, acentos azules |
| `moderno` | Gris 800/900, acentos cyan |

### 2. **color_favorito**
- Se usa para:
  - Botones principales
  - Acentos importantes
  - Borders de elementos destacados

### 3. **densidad_informacion**
| Valor | Spacing | Tamaño Texto | # Vehículos |
|-------|---------|--------------|-------------|
| `minimalista` | p-12, gap-8 | text-xl/2xl | 1 vehículo |
| `comoda` | p-6, gap-6 | text-base/lg | 2-3 vehículos |
| `compacta` | p-4, gap-4 | text-sm/base | 3-4 vehículos |
| `amplia` | p-8, gap-8 | text-lg/xl | 2 vehículos |

### 4. **estilo_tipografia**
| Valor | Clases Tailwind |
|-------|-----------------|
| `moderna_geometrica` | font-sans, font-bold, tracking-tight |
| `clasica_serif` | font-serif, font-normal, tracking-normal |
| `sans-serif` | font-sans, font-medium, tracking-normal |

### 5. **estilo_imagenes**
| Valor | Implementación |
|-------|----------------|
| `fotograficas` | Emojis + gradients realistas |
| `ilustraciones` | SVG inline + colores planos |
| `minimalistas` | Solo gradients + tipografía |

### 6. **nivel_animaciones** ⚡
| Valor | Transiciones | Efectos |
|-------|--------------|---------|
| `bajo/minimo` | Sin transitions | Elementos estáticos |
| `medio/moderado` | duration-300 | hover:scale-105 moderado |
| `alto/maximo` | duration-150 | animate-pulse, bounce, scale-110 |

### 7. **preferencia_layout**
| Valor | Estructura |
|-------|------------|
| `grid` | grid grid-cols-3, distribución cuadrícula |
| `lista` | flex flex-col, diseño vertical |
| `cards` | grid con cards elevadas (shadow-xl, rounded-xl) |
| `minimalista` | flex con spacing amplio, borders sutiles |

### 8. **estilo_navegacion**
| Valor | Nav |
|-------|-----|
| `horizontal` | Barra top, flex flex-row |
| `vertical` | Sidebar, flex flex-col |
| `hamburger` | Menú oculto móvil |
| `tabs` | Pestañas horizontales con border-b |

### 9. **preferencia_visual**
| Valor | Estética |
|-------|----------|
| `minimalista` | Máximo espacio blanco, colores neutros |
| `maximalista` | Colores vibrantes, muchos elementos |
| `equilibrada` | Balance entre elementos y espacio |

### 10. **modo_comparacion**
| Valor | Layout de Vehículos |
|-------|---------------------|
| `lado_a_lado` | grid md:grid-cols-2/3 |
| `tabla` | Estructura tabla con borders |
| `lista` | Stack vertical con separadores |

### 11. **idioma_specs**
| Valor | Lenguaje Técnico |
|-------|------------------|
| `tecnico` | "kW", "Nm", "0-100 km/h", "WLTP" |
| `simple` | "Potencia", "Velocidad", "Consumo" |
| `casual` | "Rápido", "Eficiente", "Potente" |

## 🔥 Ejemplos de Comparación

### Caso 1: Empresario vs Joven Persona

#### **Carlos Empresario** (42 años, empresa, Metropolitana)
```json
{
  "esquema_colores": "corporativo",
  "color_favorito": "#1E40AF",
  "densidad_informacion": "compacta",
  "nivel_animaciones": "bajo",
  "preferencia_layout": "tabla",
  "idioma_specs": "tecnico"
}
```
**Resultado:**
- Fondo azul corporativo
- 4 vehículos comerciales (Sprinter, Vito, eVito)
- Sin animaciones
- Especificaciones técnicas detalladas
- Layout tipo tabla para comparación

#### **Sofía Joven** (28 años, persona, Valparaíso)
```json
{
  "esquema_colores": "lujo",
  "color_favorito": "#A855F7",
  "densidad_informacion": "amplia",
  "nivel_animaciones": "alto",
  "preferencia_layout": "cards",
  "idioma_specs": "casual"
}
```
**Resultado:**
- Fondo púrpura con dorados
- 2 vehículos premium (EQS, S-Class)
- Animaciones fluidas (pulse, bounce)
- Lenguaje casual ("Elegante", "Potente")
- Cards grandes con mucho espacio

### Caso 2: Minimalista vs Maximalista

#### **Ana Minimalista**
```json
{
  "preferencia_visual": "minimalista",
  "densidad_informacion": "minimalista",
  "esquema_colores": "claro",
  "nivel_animaciones": "bajo"
}
```
**Resultado:**
- Mucho espacio en blanco
- Colores neutros (grises, blancos)
- 1 solo vehículo destacado
- Sin animaciones ni efectos
- Tipografía muy grande

#### **Roberto Maximalista**
```json
{
  "preferencia_visual": "maximalista",
  "densidad_informacion": "compacta",
  "esquema_colores": "oscuro",
  "nivel_animaciones": "alto"
}
```
**Resultado:**
- Muchos elementos visuales
- Colores vibrantes (cyan, purple, pink)
- 4 vehículos con specs completas
- Animaciones constantes
- Borders, sombras, gradients

## 🚀 Ventajas del Sistema

### 1. **Persistencia de Perfil**
- El perfil seleccionado se guarda 24 horas
- Al recargar /efimero, usa el mismo perfil
- Cambiar perfil actualiza automáticamente

### 2. **Prioridad Inteligente**
```typescript
// Orden de prioridad de datos:
1. Persona seleccionada (más específica)
2. User autenticado (perfil general)
3. Defaults (fallback)
```

### 3. **Regeneración Rápida**
- Cada cambio de perfil genera nuevo HTML
- No hay cache entre perfiles
- Diferencias son inmediatamente visibles

### 4. **Botón de Retorno**
- En /efimero hay botón "← Volver a Demo"
- Facilita cambiar de perfil
- Workflow fluido: Demo → Efímero → Demo → Efímero

## 📋 Checklist de Prueba

- [ ] Seleccionar perfil "Empresario" en /demo
- [ ] Generar Frontend Efímero, verificar enfoque corporativo
- [ ] Volver a /demo
- [ ] Seleccionar perfil "Joven Persona"
- [ ] Generar Frontend Efímero, verificar enfoque premium/lujo
- [ ] Comparar diferencias:
  - [ ] Colores (corporativo vs lujo)
  - [ ] Densidad (compacta vs amplia)
  - [ ] Animaciones (sin vs fluidas)
  - [ ] Vehículos mostrados (comerciales vs premium)
  - [ ] Lenguaje (técnico vs casual)

## 🛠️ Archivos Modificados

1. **frontend/src/app/efimero/page.tsx**
   - Lógica de construcción de params
   - Priorización Persona > User > Defaults
   - Documentación del flujo de datos

2. **frontend/src/hooks/useGeminiUI.ts**
   - Interfaz `VisualPreferences` ampliada (11 campos)
   - Prompt `buildPrompt()` mejorado (200+ líneas)
   - Instrucciones específicas para cada campo

3. **frontend/src/types/persona.ts**
   - `PersonaSimulada` con 11 campos de preferencias
   - 3 campos de prioridades (booleanos)

## 💡 Tips de Uso

1. **Para ver diferencias dramáticas**, selecciona perfiles opuestos:
   - Minimalista vs Maximalista
   - Empresa vs Persona
   - Bajo presupuesto vs Alto presupuesto

2. **Para testing**, usa el selector de personas en /demo:
   - Clic en "👤 Personas" (esquina superior derecha)
   - Aparecen ~10 perfiles genéricos
   - Clic en cualquiera para asignar

3. **Para debugging**, revisa la consola del navegador:
   - `[Efimero] 📊 Params construidos` muestra qué datos se envían
   - `[Gemini] ✅ Generation completed` confirma generación exitosa

## 🎯 Próximas Mejoras Posibles

- [ ] Comparación lado a lado (2 perfiles simultáneos)
- [ ] Guardado de favoritos (screenshots de diferentes perfiles)
- [ ] Exportar HTML generado para análisis
- [ ] Métricas de tiempo de generación por perfil
- [ ] A/B testing automático (mostrar 2 versiones, elegir la mejor)

---

**Última actualización:** 12 de noviembre de 2025  
**Versión:** 1.0  
**Estado:** ✅ Implementado y funcional

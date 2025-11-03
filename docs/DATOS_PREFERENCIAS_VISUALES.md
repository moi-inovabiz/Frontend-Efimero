# 🎨 Datos de Preferencias Visuales y Diseño - Kaufmann Mercedes-Benz

**Fecha**: Noviembre 3, 2025  
**Objetivo**: Capturar gustos visuales para personalizar colores, tipografía, diseño

---

## 🎯 DATOS DE PREFERENCIAS VISUALES (Nuevos)

### **PASO 4: Preferencias de Diseño** (1-2 min)

Estas preguntas se hacen **después del registro básico**, de forma opcional o en un wizard de personalización.

---

## 1️⃣ **ESQUEMA DE COLORES PREFERIDO** ⭐⭐⭐

### **Pregunta:**
> "¿Qué paleta de colores prefieres para tu experiencia?"

```typescript
esquema_colores: 
  | "automatico"           // Sigue tema del sistema
  | "claro_elegante"       // Blancos, grises claros, acentos dorados
  | "oscuro_premium"       // Negros, grises oscuros, acentos plateados
  | "alto_contraste"       // Negro/blanco puro (accesibilidad)
  | "calido"               // Beiges, marrones, acentos cobre
  | "frio"                 // Azules, grises azulados, acentos azul eléctrico
  | "vibrante"             // Colores saturados, energéticos
```

**Mapeo a Productos Kaufmann**:
```typescript
// Mercedes-Benz Clase S, AMG → "oscuro_premium", "claro_elegante"
// Smart eléctrico → "vibrante", "frio"
// Camiones comerciales → "automatico", "alto_contraste"
// Vans ejecutivas → "claro_elegante", "calido"
```

**Features ML generadas**:
- `prefiere_colores_frios: bool`
- `prefiere_colores_calidos: bool`
- `necesita_alto_contraste: bool`
- `es_usuario_vibrante: bool`

**CSS Variables aplicadas**:
```css
/* Ejemplo: oscuro_premium */
--color-background: #0a0a0a;
--color-surface: #1a1a1a;
--color-primary: #c4c4c4;    /* Plateado */
--color-accent: #ffd700;     /* Dorado */
--color-text: #ffffff;

/* Ejemplo: vibrante */
--color-background: #ffffff;
--color-surface: #f5f5f5;
--color-primary: #0066ff;    /* Azul eléctrico */
--color-accent: #ff3366;     /* Rosa vibrante */
--color-text: #1a1a1a;
```

---

## 2️⃣ **COLOR PRINCIPAL FAVORITO** ⭐⭐⭐

### **Pregunta:**
> "¿Cuál es tu color favorito? (Esto personalizará los acentos de la interfaz)"

```typescript
color_favorito:
  | "azul"        // #0066ff - Profesional, confiable
  | "rojo"        // #e60000 - Energético, Mercedes AMG
  | "verde"       // #00cc66 - Sostenible, Smart eléctrico
  | "dorado"      // #ffd700 - Premium, lujo
  | "plateado"    // #c0c0c0 - Elegante, Mercedes signature
  | "naranja"     // #ff6600 - Dinámico, deportivo
  | "purpura"     // #9933ff - Exclusivo, único
  | "negro"       // #000000 - Clásico, atemporal
  | "blanco"      // #ffffff - Minimalista, limpio
```

**Mapeo Psicológico**:
- **Azul** → Profesional, confiable → Empresas transporte
- **Rojo** → Energía, pasión → AMG, deportivos
- **Verde** → Sostenibilidad → Smart eléctrico
- **Dorado/Plateado** → Lujo → Clase S, ejecutivos
- **Negro** → Elegancia → Autos premium
- **Naranja** → Dinamismo → Jóvenes, SUVs

**Features ML**:
- `color_favorito_encoded: int` (0-8)
- `prefiere_colores_neutros: bool` (negro, blanco, gris)
- `prefiere_colores_premium: bool` (dorado, plateado)
- `prefiere_colores_energeticos: bool` (rojo, naranja)

**Aplicación en UI**:
```css
/* Si elige "dorado" */
--color-accent: #ffd700;
--color-accent-hover: #ffed4e;
--color-button-primary: linear-gradient(135deg, #ffd700, #ffb700);

/* Botones, links, iconos destacados usan este color */
.btn-primary { background: var(--color-accent); }
.link-primary { color: var(--color-accent); }
```

---

## 3️⃣ **ESTILO DE TIPOGRAFÍA** ⭐⭐

### **Pregunta:**
> "¿Qué estilo de letra prefieres?"

```typescript
estilo_tipografia:
  | "moderna_geometrica"   // Sans-serif geométrica (Mercedes oficial)
  | "clasica_serif"        // Serif tradicional (lujo clásico)
  | "tecnologica"          // Monospace/futurista (tech, Smart)
  | "elegante_script"      // Script sutil (ultra premium)
  | "bold_impactante"      // Sans bold (deportivo, AMG)
```

**Mapeo a Fuentes**:
```css
/* moderna_geometrica - DEFAULT Mercedes */
font-family: 'Corporate S', 'Helvetica Neue', sans-serif;

/* clasica_serif - Lujo clásico */
font-family: 'Playfair Display', 'Georgia', serif;

/* tecnologica - Smart eléctrico */
font-family: 'Space Grotesk', 'Roboto Mono', monospace;

/* elegante_script - Ultra premium */
font-family: 'Cormorant', 'Crimson Text', serif;

/* bold_impactante - AMG deportivo */
font-family: 'Montserrat', 'Oswald', sans-serif;
font-weight: 700;
```

**Features ML**:
- `prefiere_serif: bool`
- `prefiere_sans_serif: bool`
- `prefiere_fuentes_bold: bool`
- `estilo_tipografia_encoded: int` (0-4)

---

## 4️⃣ **DENSIDAD DE INFORMACIÓN** ⭐⭐⭐

### **Pregunta:**
> "¿Cuánta información quieres ver en pantalla?"

```typescript
densidad_informacion:
  | "minimalista"    // Mucha whitespace, pocas opciones visibles
  | "comoda"         // Balance, información esencial
  | "compacta"       // Más información, menos espacios
  | "maxima"         // Dashboard denso, para expertos
```

**Visualización**:
```
┌─────────────────────────────────────────┐
│ MINIMALISTA (Simple, espacioso)        │
├─────────────────────────────────────────┤
│                                         │
│     Mercedes-Benz GLE 450               │
│                                         │
│     [Imagen grande]                     │
│                                         │
│     $89.990.000                         │
│                                         │
│     [Ver detalles →]                    │
│                                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ COMPACTA (Más info, menos espacio)     │
├─────────────────────────────────────────┤
│ Mercedes-Benz GLE 450  $89.990.000     │
│ [Img] 367 HP | 0-100: 5.7s | 9.1L/100km│
│ ⭐⭐⭐⭐⭐ (124 reseñas)                  │
│ 📍 Stock: 3 unidades en Las Condes     │
│ [Cotizar] [Test Drive] [Comparar]      │
├─────────────────────────────────────────┤
│ Mercedes-Benz GLC 300  $64.990.000     │
│ [Img] 258 HP | 0-100: 6.3s | 8.5L/100km│
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ MÁXIMA (Dashboard técnico)              │
├─────────────────────────────────────────┤
│ GLE 450 | GLC 300 | Clase E | Actros   │
│ [4 imágenes pequeñas lado a lado]      │
│ Precio | HP | Cons. | Stock | TCO      │
│ Tabla comparativa con 20+ specs        │
│ Gráfico de consumo, gráfico de costos  │
│ [10 botones de acción]                  │
└─────────────────────────────────────────┘
```

**Features ML**:
- `densidad_ui_normalizada: float` (0-1, 0=minimalista, 1=máxima)
- `prefiere_minimalismo: bool`
- `es_usuario_experto: bool` (correlaciona con "máxima")

**CSS Variables**:
```css
/* minimalista */
--spacing-unit: 2rem;      /* Espacios grandes */
--card-padding: 3rem;
--line-height: 1.8;

/* compacta */
--spacing-unit: 0.75rem;   /* Espacios pequeños */
--card-padding: 1rem;
--line-height: 1.4;

/* máxima */
--spacing-unit: 0.5rem;    /* Espacios mínimos */
--card-padding: 0.5rem;
--line-height: 1.2;
--font-size-base: 0.875rem; /* Texto más pequeño */
```

---

## 5️⃣ **ESTILO DE IMÁGENES** ⭐⭐

### **Pregunta:**
> "¿Qué estilo de imágenes de productos prefieres?"

```typescript
estilo_imagenes:
  | "fotograficas_realistas"   // Fotos reales de showroom
  | "renders_limpios"          // Renders 3D sobre fondo blanco
  | "lifestyle_contexto"       // Autos en uso real (carretera, ciudad)
  | "tecnicas_specs"           // Vistas técnicas, cortes, detalles
```

**Aplicación**:
```typescript
// fotograficas_realistas
const imagenProducto = "gle450_showroom_01.jpg";

// renders_limpios
const imagenProducto = "gle450_render_white_bg.png";

// lifestyle_contexto
const imagenProducto = "gle450_mountain_road.jpg";

// tecnicas_specs
const imagenProducto = "gle450_cutaway_engine.jpg";
```

**Por Segmento**:
- **Autos de lujo** → fotograficas_realistas, lifestyle_contexto
- **Camiones comerciales** → tecnicas_specs, renders_limpios
- **Smart eléctrico** → lifestyle_contexto (urbano)

---

## 6️⃣ **NIVEL DE ANIMACIONES** ⭐⭐

### **Pregunta:**
> "¿Cuántas animaciones quieres en la interfaz?"

```typescript
nivel_animaciones:
  | "ninguna"        // Sin animaciones (accesibilidad o rendimiento)
  | "sutiles"        // Transiciones suaves básicas
  | "moderadas"      // Animaciones estándar
  | "dinamicas"      // Animaciones llamativas, interactivas
```

**Combina con datos automáticos**:
```typescript
// Si usuario tiene prefers_reduced_motion: true
// → Forzar "ninguna" o "sutiles" independiente de preferencia
if (prefers_reduced_motion || connection_effective_type === "2g") {
  nivel_animaciones = "ninguna";
}
```

**CSS aplicado**:
```css
/* ninguna */
* {
  transition: none !important;
  animation: none !important;
}

/* sutiles */
.card {
  transition: transform 0.2s ease;
}

/* moderadas */
.card {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.3s ease;
}
.card:hover {
  transform: translateY(-4px);
}

/* dinamicas */
.card {
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  animation: slideIn 0.6s ease-out;
}
```

---

## 7️⃣ **PREFERENCIA DE LAYOUT** ⭐⭐

### **Pregunta:**
> "¿Cómo prefieres ver los vehículos?"

```typescript
preferencia_layout:
  | "lista_detallada"     // Lista vertical con mucha info
  | "grilla_cards"        // Cards en grilla (2-3 columnas)
  | "carrusel_grande"     // Carousel con imágenes grandes
  | "tabla_comparativa"   // Tabla con specs técnicas
```

**Visualización**:

**Lista Detallada**:
```
┌────────────────────────────────────────┐
│ [Imagen] Mercedes-Benz GLE 450        │
│          ⭐⭐⭐⭐⭐ $89.990.000          │
│          367 HP | 3.0L V6 Turbo        │
│          Consumo: 9.1 L/100km          │
│          [Cotizar] [Test Drive]        │
├────────────────────────────────────────┤
│ [Imagen] Mercedes-Benz GLC 300        │
│          ⭐⭐⭐⭐⭐ $64.990.000          │
└────────────────────────────────────────┘
```

**Grilla Cards**:
```
┌──────────┐ ┌──────────┐ ┌──────────┐
│ [Imagen] │ │ [Imagen] │ │ [Imagen] │
│ GLE 450  │ │ GLC 300  │ │ Clase E  │
│ $89.990M │ │ $64.990M │ │ $79.990M │
│ [Ver +]  │ │ [Ver +]  │ │ [Ver +]  │
└──────────┘ └──────────┘ └──────────┘
```

---

## 8️⃣ **PREFERENCIA DE NAVEGACIÓN** ⭐⭐

### **Pregunta:**
> "¿Cómo prefieres navegar el sitio?"

```typescript
estilo_navegacion:
  | "menu_tradicional"      // Menú top horizontal clásico
  | "sidebar_persistente"   // Sidebar lateral siempre visible
  | "hamburger_minimalista" // Menú hamburguesa oculto
  | "tabs_categorias"       // Pestañas por tipo de vehículo
```

**Por Tipo de Usuario**:
- **Persona natural (lujo)** → hamburger_minimalista (limpio)
- **Empresa (flotas)** → sidebar_persistente (acceso rápido)
- **Usuario experto** → tabs_categorias (navegación rápida)

---

## 9️⃣ **ICONOS vs TEXTO** ⭐

### **Pregunta:**
> "¿Prefieres ver?"

```typescript
preferencia_visual:
  | "iconos_solo"          // Solo iconos (minimalista)
  | "iconos_con_labels"    // Iconos + texto (recomendado)
  | "texto_solo"           // Solo texto (accesibilidad)
```

**Ejemplo**:
```html
<!-- iconos_solo -->
<button><Icon name="cart" /></button>

<!-- iconos_con_labels -->
<button><Icon name="cart" /> Cotizar</button>

<!-- texto_solo -->
<button>Solicitar Cotización</button>
```

---

## 🔟 **PRIORIDAD DE INFORMACIÓN** ⭐⭐⭐

### **Pregunta:**
> "¿Qué es lo más importante para ti al ver un vehículo?"
> (Ordenar por prioridad: 1, 2, 3, 4, 5)

```typescript
prioridades_info: {
  precio: number,           // 1-5
  especificaciones: number, // HP, torque, cilindrada
  consumo: number,          // L/100km, rendimiento
  seguridad: number,        // Airbags, asistencias
  tecnologia: number        // Pantalla, conectividad
}

// Ejemplo usuario ejecutivo:
{ precio: 3, especificaciones: 4, consumo: 5, seguridad: 2, tecnologia: 1 }

// Ejemplo empresa transporte:
{ precio: 2, especificaciones: 3, consumo: 1, seguridad: 4, tecnologia: 5 }
```

**Features ML**:
- `prioriza_precio: bool` (precio en top 2)
- `prioriza_consumo: bool` (consumo #1)
- `prioriza_tecnologia: bool` (tech en top 2)

**Aplicación en UI**:
```typescript
// Si prioriza_consumo === true
// Mostrar consumo destacado en card principal
<div className="card">
  <h3>Mercedes-Benz GLE 450</h3>
  <div className="highlight">⛽ 9.1 L/100km</div> {/* DESTACADO */}
  <p>$89.990.000</p>
  <p>367 HP</p>
</div>
```

---

## 1️⃣1️⃣ **MODO DE COMPARACIÓN** ⭐

### **Pregunta:**
> "¿Cómo prefieres comparar vehículos?"

```typescript
modo_comparacion:
  | "lado_a_lado"       // Tabla comparativa 2-3 vehículos
  | "overlay_specs"     // Overlay sobre imagen con specs
  | "checklist_features" // Lista de features con checks
  | "no_comparar"       // Prefiero ver uno a la vez
```

---

## 1️⃣2️⃣ **PREFERENCIA DE IDIOMA DE SPECS** ⭐

### **Pregunta:**
> "¿Prefieres ver las especificaciones técnicas en?"

```typescript
idioma_specs:
  | "espanol_simple"     // "367 caballos de fuerza"
  | "espanol_tecnico"    // "367 HP @ 5500 RPM"
  | "unidades_metricas"  // "274 kW @ 5500 RPM"
  | "ambos"              // "367 HP (274 kW)"
```

---

## 📊 RESUMEN: FORMULARIO DE PREFERENCIAS VISUALES

### **Wizard de Personalización (Paso Opcional - 2 min)**

```
┌─────────────────────────────────────────────┐
│  🎨 Personaliza tu experiencia visual      │
│  (Puedes cambiar esto en cualquier momento)│
├─────────────────────────────────────────────┤
│                                             │
│  1. ¿Qué paleta de colores prefieres?      │
│  ○ Claro elegante                           │
│  ● Oscuro premium                           │
│  ○ Alto contraste                           │
│  ○ Automático (sigue tu sistema)            │
│                                             │
│  2. Tu color favorito:                      │
│  [Selector de color visual]                 │
│  ● Plateado  ○ Dorado  ○ Azul  ○ Rojo      │
│                                             │
│  3. Densidad de información:                │
│  ├────●──────────┤                          │
│  Minimalista    Máxima                      │
│                                             │
│  4. Estilo de tipografía:                   │
│  ○ Moderna (Mercedes oficial)               │
│  ● Elegante (Serif)                         │
│  ○ Tecnológica (Futurista)                  │
│                                             │
│  5. ¿Qué es más importante para ti?         │
│  Arrastra para ordenar:                     │
│  [1] Tecnología y conectividad              │
│  [2] Seguridad                              │
│  [3] Precio                                 │
│  [4] Especificaciones (HP, torque)          │
│  [5] Consumo de combustible                 │
│                                             │
│  [Omitir] [Guardar preferencias →]         │
└─────────────────────────────────────────────┘
```

---

## 🤖 FEATURES MACHINE LEARNING GENERADAS

Con estas preferencias visuales, generas **20+ features ML**:

### **Colores (6 features)**
```python
1. esquema_colores_encoded: int (0-6)
2. color_favorito_encoded: int (0-8)
3. prefiere_colores_oscuros: bool
4. prefiere_colores_premium: bool (dorado, plateado)
5. prefiere_colores_neutros: bool
6. prefiere_colores_energeticos: bool
```

### **Tipografía y Layout (5 features)**
```python
7. prefiere_serif: bool
8. prefiere_sans_serif: bool
9. densidad_ui_normalizada: float (0-1)
10. prefiere_minimalismo: bool
11. es_usuario_experto_ui: bool
```

### **Interacción (5 features)**
```python
12. nivel_animaciones_encoded: int (0-3)
13. sin_animaciones: bool
14. prefiere_iconos_solo: bool
15. prefiere_sidebar: bool
16. usa_comparacion: bool
```

### **Prioridades (4 features)**
```python
17. prioriza_precio: bool
18. prioriza_consumo: bool
19. prioriza_tecnologia: bool
20. prioriza_seguridad: bool
```

---

## 🎨 APLICACIÓN EN UI - EJEMPLOS REALES

### **Ejemplo 1: Usuario Premium Minimalista**

```typescript
{
  esquema_colores: "claro_elegante",
  color_favorito: "dorado",
  estilo_tipografia: "elegante_script",
  densidad_informacion: "minimalista",
  nivel_animaciones: "sutiles"
}
```

**Resultado UI**:
```css
/* Tema */
--color-background: #fafafa;
--color-surface: #ffffff;
--color-accent: #ffd700;
--font-primary: 'Cormorant', serif;

/* Layout */
--spacing-unit: 2rem;
--card-padding: 3rem;

/* Animaciones */
transition: transform 0.2s ease;
```

### **Ejemplo 2: Empresa Transporte (Técnico)**

```typescript
{
  esquema_colores: "alto_contraste",
  color_favorito: "azul",
  estilo_tipografia: "moderna_geometrica",
  densidad_informacion: "maxima",
  preferencia_layout: "tabla_comparativa",
  prioridades_info: { consumo: 1, precio: 2, especificaciones: 3 }
}
```

**Resultado UI**:
```css
/* Tema */
--color-background: #ffffff;
--color-text: #000000;
--color-accent: #0066ff;
--font-primary: 'Corporate S', sans-serif;

/* Layout */
--spacing-unit: 0.5rem;
--card-padding: 0.75rem;
--font-size-base: 0.875rem;

/* Sin animaciones */
* { transition: none !important; }
```

**Vista**:
```
┌──────────────────────────────────────────┐
│ Actros 2651  | Atego 1730 | Axor 2544   │
├──────────────────────────────────────────┤
│ Consumo      | 28L/100km  | 24L/100km   │
│ Precio       | $180M      | $120M       │
│ HP           | 510        | 300         │
│ Carga Útil   | 15 ton     | 12 ton      │
│ TCO 5 años   | $380M      | $280M       │
└──────────────────────────────────────────┘
```

---

## ✅ RECOMENDACIÓN FINAL

### **Formulario Login Completo (3 Pasos)**

**PASO 1: Datos Básicos** (30 seg)
- Email, Nombre, RUT, Teléfono

**PASO 2: Perfil de Cliente** (45 seg)
- Tipo cliente, Región, Interés, Uso, Presupuesto

**PASO 3: Preferencias Visuales** (1-2 min) - **OPCIONAL/OMITIR**
- Esquema colores
- Color favorito
- Densidad información
- Prioridades (precio, consumo, tech)

### **Features Totales Generadas**

```
Datos automáticos (45 campos)
+ Datos de perfil (10 campos)
+ Preferencias visuales (12 campos)
─────────────────────────────
= 67 CAMPOS TOTALES

Features ML derivadas:
- Contexto automático: 35 features
- Perfil usuario: 15 features
- Preferencias visuales: 20 features
─────────────────────────────
= 70+ FEATURES PARA ML

Mejora esperada en F1-Score: 0.75 → 0.92-0.95 (+23%)
```

---

**¿Quieres que implemente el formulario completo de 3 pasos con todas estas preferencias visuales?**

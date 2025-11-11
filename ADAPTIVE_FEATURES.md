# 🎨 Sistema de Adaptación Dinámica - Frontend Efímero

## Resumen

Este documento describe el sistema completo de **matching inteligente** y **adaptaciones visuales dinámicas** implementado para el proyecto Frontend Efímero.

## ✅ Características Implementadas

### 1. 🧠 Matching Inteligente de Personas

#### Backend (`backend/app/api/routes/personas.py`)

**Sistema de Puntuación (0-100 pts):**

```python
Criterio                          Puntos    Descripción
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗺️  Region Matching                25      Coincidencia geográfica exacta
📱  Device + Age Correlation       20      Móvil→jóvenes, Desktop→mayores/empresas
⏰  Time + Client Type             20      Horario laboral→empresas, noche→personas
🎉  Weekend Preference             10      Fin de semana favorece personas individuales
🌐  Connection + Visual Prefs      10      Conexión lenta→preferencias visuales simples
🎲  Random Component                15      Mantiene diversidad (evita 100% predictivo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TOTAL                           100
```

**Modelos Pydantic:**
- `ContextoAsignacion`: Recibe 10 campos de contexto del navegador
  - `hora_del_dia` (0-23)
  - `es_fin_de_semana` (boolean)
  - `ciudad`, `region`, `pais`
  - `es_movil`, `es_tablet`
  - `sistema_operativo`, `tipo_conexion`

**Funciones principales:**
- `calcular_score_persona()`: Calcula score para cada persona vs contexto
- `obtener_persona_con_matching()`: Selecciona persona con mayor score
- `obtener_o_crear_asignacion()`: Gestiona asignación con persistencia

**Endpoint actualizado:**
```http
POST /api/v1/personas/assign
Content-Type: application/json
X-Session-ID: <uuid>

Body:
{
  "hora_del_dia": 14,
  "es_fin_de_semana": false,
  "region": "Santiago",
  "es_movil": true,
  "tipo_conexion": "4g"
}

Response:
{
  "success": true,
  "persona": {...},
  "session_id": "...",
  "is_new_assignment": true,
  "matching_score": 75.5,
  "matching_info": {
    "used_context": true,
    "context_fields": {...}
  }
}
```

#### Frontend (`frontend/src/hooks/usePersona.ts`)

**Nuevas funciones:**
- `transformContextToBackend()`: Convierte datos de `useEphemeralContext` a formato backend
- `assignPersona()`: Ahora envía contexto en el body del request
- `refreshPersonaWithContext()`: Refresh inteligente con contexto

**Integración con contexto efímero:**
```typescript
const context = useEphemeralContext(); // 45+ datos del navegador
const contextoBackend = transformContextToBackend(context);
// Envía: hora, región, dispositivo, conexión, etc.
```

### 2. 🎨 Adaptaciones Visuales Dinámicas

#### Variables CSS Adaptativas (`AdaptiveUIProvider.tsx`)

El sistema ahora inyecta **7 variables CSS dinámicas** basadas en la persona:

```css
Variable                          Basado en                  Valores posibles
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
--adaptive-font-size-base         edad                       16px, 18px, 20px
--adaptive-primary-color          tipo_cliente + color_fav   #3B82F6 o personalizado
--adaptive-animation-duration     nivel_animaciones          0.1s, 0.3s, 0.5s
--adaptive-spacing-unit           densidad_informacion       0.75rem, 1rem, 1.5rem
--adaptive-border-radius          preferencia_layout         0.25rem, 0.5rem, 0.75rem
--adaptive-bg-color              (futuro)                   #ffffff
--adaptive-text-color            (futuro)                   #111827
```

**Lógica de adaptación:**

```typescript
// 1. Font Size por Edad
edad < 40    → 16px  // Jóvenes: tamaño normal
edad 40-59   → 18px  // Adultos: más legible
edad >= 60   → 20px  // Mayores: máxima legibilidad

// 2. Color por Tipo Cliente
tipo === 'empresa' → #3B82F6 (azul profesional)
tipo === 'persona' → persona.color_favorito (personalizado)

// 3. Animaciones por Nivel
nivel === 'bajo'  → 0.1s (rápido)
nivel === 'medio' → 0.3s (equilibrado)
nivel === 'alto'  → 0.5s (suave)

// 4. Espaciado por Densidad
densidad === 'compacta' → 0.75rem (apretado)
densidad === 'comoda'   → 1rem    (normal)
densidad === 'amplia'   → 1.5rem  (espacioso)

// 5. Border Radius por Layout
layout === 'minimalista' → 0.25rem (cuadrado)
layout === 'cards'       → 0.75rem (redondeado)
layout === 'grid'        → 0.5rem  (intermedio)
```

#### Estilos Globales (`frontend/src/app/globals.css`)

Nuevas clases CSS automáticas:

```css
/* Aplicadas dinámicamente por el ML + persona */
.densidad-compacta
.densidad-comoda
.densidad-amplia

.animacion-bajo
.animacion-medio
.animacion-alto

.layout-minimalista
.layout-cards
.layout-grid

/* Clases de utilidad */
.adaptive-button    /* Usa todas las variables adaptativas */
.adaptive-card      /* Transiciones suaves con variables */
```

### 3. 📊 Componente de Demostración Visual

#### `AdaptiveShowcase.tsx`

Nuevo componente que visualiza **6 adaptaciones** en tiempo real:

1. **📝 Font Size** - Muestra texto con tamaño adaptado a edad
2. **🎨 Color Primario** - Box con color adaptado a tipo cliente
3. **⚡ Velocidad Animaciones** - 3 elementos animados a diferentes velocidades
4. **📏 Espaciado** - Barras con gap adaptado a densidad
5. **🔲 Border Radius** - 3 cajas con redondez adaptada
6. **🎯 Resumen** - Tabla con todos los valores actuales

Cada card muestra:
- Criterio de adaptación (edad, tipo_cliente, etc.)
- Valor actual de la persona
- Adaptación aplicada (descripción)
- Variable CSS usada (`--adaptive-*`)
- Vista previa interactiva

#### Página Demo Actualizada (`frontend/src/app/demo/page.tsx`)

```tsx
// Ahora incluye AdaptiveShowcase en la parte superior
<AdaptiveShowcase />

// Luego las cards originales con preferencias de persona
// Footer instructivo actualizado
```

### 4. 🔄 Panel de Debug Mejorado

#### `PersonaDebugPanel.tsx`

Actualizado para usar matching inteligente:
- Ahora usa `useEphemeralContext()` para obtener datos del navegador
- Botón refresh usa `refreshPersonaWithContext()` con contexto actual
- Tooltip actualizado: "Cambiar persona con matching inteligente"

## 📊 Flujo Completo del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│  1. USUARIO VISITA LA PÁGINA                                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. CAPTURA DE CONTEXTO (useEphemeralContext)                   │
│     - 45+ datos del navegador sin permisos                      │
│     - hora, región, dispositivo, conexión, etc.                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. TRANSFORMACIÓN (transformContextToBackend)                  │
│     UserContextData → ContextoAsignacion                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. REQUEST CON CONTEXTO                                        │
│     POST /api/v1/personas/assign + body JSON                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. MATCHING INTELIGENTE (Backend)                              │
│     calcular_score_persona() → 0-100 pts                        │
│     obtener_persona_con_matching() → mejor match                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. RESPUESTA CON SCORE                                         │
│     persona + matching_score + matching_info                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. PREDICCIÓN ML (AdaptiveUIProvider)                          │
│     53 campos → XGBoost → tokens CSS                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  8. INYECCIÓN DE TOKENS + ADAPTACIONES DINÁMICAS                │
│     - Tokens ML (css_classes, css_variables)                    │
│     - Variables dinámicas (--adaptive-*)                        │
│     - Basadas en edad, tipo, preferencias                       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  9. UI ADAPTADA VISIBLE                                         │
│     - Font size ajustado                                        │
│     - Colores personalizados                                    │
│     - Animaciones a la velocidad correcta                       │
│     - Espaciado según densidad                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🧪 Escenarios de Prueba

### Escenario 1: Usuario Joven en Móvil (Noche)
```
Contexto:
  - edad: 25 años
  - dispositivo: móvil
  - hora: 21:00
  - día: sábado
  - conexión: 4G

Adaptaciones esperadas:
  ✅ Font: 16px (estándar para jóvenes)
  ✅ Persona tipo: individual (no empresa fuera de horario laboral)
  ✅ Color: color favorito del usuario
  ✅ Animaciones: 0.3s (medio)
  ✅ Matching score: 60-80 (buena coincidencia)
```

### Escenario 2: Empresa en Desktop (Día Laboral)
```
Contexto:
  - edad: 45 años
  - dispositivo: desktop
  - hora: 10:00
  - día: martes
  - conexión: fibra óptica

Adaptaciones esperadas:
  ✅ Font: 18px (más grande para adultos)
  ✅ Persona tipo: empresa con flota
  ✅ Color: #3B82F6 (azul profesional)
  ✅ Animaciones: 0.1s-0.3s (eficiente)
  ✅ Matching score: 75-90 (excelente coincidencia)
```

### Escenario 3: Adulto Mayor en Tablet
```
Contexto:
  - edad: 68 años
  - dispositivo: tablet
  - hora: 15:00
  - día: miércoles
  - conexión: WiFi

Adaptaciones esperadas:
  ✅ Font: 20px (máxima legibilidad)
  ✅ Densidad: amplia (más espacioso)
  ✅ Animaciones: 0.5s (suaves)
  ✅ Bordes: 0.75rem (amigable)
  ✅ Matching score: 70-85
```

## 🎯 Logs del Sistema

### Console Logs del Frontend

```javascript
// Al cargar persona con matching
[Persona] 🧠 Usando matching inteligente con contexto: {
  hora: 14,
  fin_semana: false,
  region: "Santiago",
  dispositivo: "móvil",
  conexion: "4g"
}

[Persona] ✅ Asignación exitosa: {
  persona: "María García",
  tipo: "empresa",
  edad: 45,
  matchingScore: 75.5
}

// Al inyectar adaptaciones
🎨 Tokens de diseño inyectados: {
  css_classes: ["densidad-comoda", "fuente-sans", "modo-claro"],
  css_variables: {...}
}

🎭 Adaptaciones dinámicas aplicadas: {
  edad: 45,
  fontSize: "18px",
  tipo_cliente: "empresa",
  primaryColor: "#3B82F6",
  nivel_animaciones: "medio",
  animationDuration: "0.3s",
  densidad_informacion: "comoda",
  spacingUnit: "1rem",
  preferencia_layout: "cards",
  borderRadius: "0.75rem"
}
```

### Backend Logs

```python
[MATCHING] Contexto recibido: hora=14, región=Santiago, móvil=True, fin_semana=False

[MATCHING] Calculando scores para 26 personas...
[MATCHING] - Ana López (empresa, 45, Santiago): score=78.50
[MATCHING] - Carlos Ruiz (persona, 28, Valparaíso): score=42.00
[MATCHING] - María García (empresa, 52, Santiago): score=81.20
...

[MATCHING] Persona seleccionada: María García (score: 81.20, tipo: empresa, edad: 52)
```

## 📁 Archivos Modificados/Creados

```
Backend:
✅ backend/app/api/routes/personas.py         (MODIFICADO - matching)
   - ContextoAsignacion model
   - calcular_score_persona()
   - obtener_persona_con_matching()
   - POST /assign endpoint actualizado

Frontend:
✅ frontend/src/hooks/usePersona.ts           (MODIFICADO - contexto)
   - transformContextToBackend()
   - refreshPersonaWithContext()
   - assignPersona() con contexto

✅ frontend/src/components/adaptive/AdaptiveUIProvider.tsx (MODIFICADO)
   - injectDesignTokens() con adaptaciones dinámicas
   - 7 variables CSS adaptativas

✅ frontend/src/components/adaptive/AdaptiveShowcase.tsx (NUEVO)
   - Visualización de 6 adaptaciones
   - Cards interactivas con previews

✅ frontend/src/components/persona/PersonaDebugPanel.tsx (MODIFICADO)
   - Usa useEphemeralContext
   - Refresh inteligente

✅ frontend/src/app/demo/page.tsx             (MODIFICADO)
   - Incluye AdaptiveShowcase

✅ frontend/src/app/globals.css               (MODIFICADO)
   - Variables CSS por defecto
   - Clases de utilidad adaptativas
   - Transiciones suaves

✅ frontend/src/types/persona.ts              (MODIFICADO)
   - matching_score y matching_info

Documentación:
✅ ADAPTIVE_FEATURES.md                       (NUEVO - este archivo)
```

## 🚀 Cómo Probar

1. **Backend corriendo**: `http://localhost:8000`
2. **Frontend**: `npm run dev` en carpeta frontend
3. **Abrir**: `http://localhost:3000/demo`
4. **Observar**:
   - Panel de persona (top-right)
   - Adaptaciones visuales (primer bloque)
   - Console logs con matching score
5. **Cambiar persona**: Click en 🔄 (panel debug)
6. **Ver diferencias**: Refrescar varias veces con diferentes contextos

## 🎨 Variables CSS Disponibles

Puedes usar estas variables en cualquier componente:

```css
.mi-componente {
  font-size: var(--adaptive-font-size-base);
  color: var(--adaptive-primary-color);
  padding: var(--adaptive-spacing-unit);
  border-radius: var(--adaptive-border-radius);
  transition: all var(--adaptive-animation-duration) ease;
}
```

## 📈 Próximas Mejoras

- [ ] Modo oscuro/claro dinámico por esquema_colores
- [ ] Tipografía adaptativa (sans-serif vs serif)
- [ ] Layout switching (grid vs lista vs cards)
- [ ] A/B testing del matching score
- [ ] Métricas de conversión por adaptación
- [ ] Dashboard analytics de matching effectiveness
- [ ] Cache del matching en localStorage
- [ ] Refresh automático cada X minutos

## 🙌 Resumen

El sistema ahora combina:
1. **Matching inteligente** (5 criterios, 100 pts)
2. **ML predictions** (XGBoost, 53 campos)
3. **Adaptaciones dinámicas** (7 variables CSS)
4. **UI showcase** (6 cards visuales)
5. **Persistencia** (24h localStorage)
6. **Logs detallados** (debugging fácil)

**Resultado**: Una experiencia completamente personalizada que considera tanto el contexto del usuario como sus preferencias demográficas simuladas. 🎉

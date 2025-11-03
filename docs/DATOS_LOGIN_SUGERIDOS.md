# 📝 Datos Sugeridos para Login Básico

**Fecha**: Noviembre 3, 2025  
**Objetivo**: Recopilar datos del usuario que complementen los 45 campos automáticos

---

## 🎯 Datos que YA Capturamos Automáticamente (No pedir)

❌ **NO pedir estos** (ya los tenemos):
- Timezone → Detectado automáticamente
- Locale/idioma → Detectado automáticamente
- Dispositivo → Detectado automáticamente
- Navegador → Detectado automáticamente
- Conexión → Detectado automáticamente
- Preferencias de accesibilidad → Detectado automáticamente

---

## ✅ Datos SUGERIDOS para Pedir en Login

### **1. DATOS BÁSICOS (Obligatorios)**

#### **Email** ⭐⭐⭐ (Crítico)
```typescript
email: string  // "usuario@example.com"
```
**Por qué**: 
- Identificador único del usuario
- Para recuperación de contraseña
- Comunicaciones importantes

#### **Nombre** ⭐⭐⭐ (Crítico)
```typescript
nombre: string  // "Juan"
apellido?: string  // "Pérez" (opcional)
```
**Por qué**: 
- Personalización de UI ("Hola, Juan")
- Mejorar experiencia
- No es crítico para ML pero mejora UX

#### **Fecha de Nacimiento** ⭐⭐⭐ (Muy importante)
```typescript
fecha_nacimiento: Date  // 1990-05-15
// O simplemente:
edad: number  // 34
```
**Por qué**: 
- **Feature ML**: Edad es un predictor fuerte de preferencias UI
- Generaciones tienen diferentes patrones (Gen Z vs Boomers)
- Puede derivar: rango_edad → "18-24", "25-34", "35-44", "45-54", "55+"

#### **País/Nacionalidad** ⭐⭐⭐ (Muy importante)
```typescript
pais: string  // "Chile", "España", "México"
// O código ISO:
pais_codigo: string  // "CL", "ES", "MX"
```
**Por qué**: 
- **Feature ML**: Preferencias culturales de UI
- Colores, layouts, formatos varían por cultura
- Complementa timezone que ya detectamos

---

### **2. DATOS DEMOGRÁFICOS (Opcionales pero muy útiles para ML)**

#### **Género** ⭐⭐ (Útil para ML)
```typescript
genero?: "masculino" | "femenino" | "otro" | "prefiero_no_decir"
```
**Por qué**: 
- **Feature ML**: Patrones de uso pueden variar
- Estudios muestran diferencias en preferencias de color/diseño
- Opcional, respeta privacidad

#### **Ocupación/Profesión** ⭐⭐⭐ (Muy útil para ML)
```typescript
ocupacion?: string  // "Desarrollador", "Diseñador", "Estudiante", "Ejecutivo"
// O categorías:
tipo_profesion?: "tecnologia" | "creatividad" | "negocios" | "educacion" | "salud" | "otro"
```
**Por qué**: 
- **Feature ML FUERTE**: Profesionales tech prefieren UIs densas
- Diseñadores valoran estética
- Ejecutivos prefieren eficiencia
- Estudiantes pueden preferir gamificación

#### **Nivel de Educación** ⭐ (Opcional)
```typescript
educacion?: "secundaria" | "universitaria" | "postgrado" | "doctorado" | "otro"
```
**Por qué**: 
- **Feature ML**: Correlación con complejidad de UI preferida
- Usuarios con mayor educación técnica toleran UIs más complejas

---

### **3. DATOS DE PREFERENCIAS (Opcionales - Mejorar ML)**

#### **Experiencia con Tecnología** ⭐⭐⭐ (Muy útil)
```typescript
nivel_tecnologia?: "principiante" | "intermedio" | "avanzado" | "experto"
```
**Por qué**: 
- **Feature ML CRÍTICA**: Determina densidad de información
- Expertos quieren shortcuts, principiantes necesitan guías
- Afecta directamente el diseño adaptativo

#### **Propósito de Uso** ⭐⭐ (Útil)
```typescript
proposito_uso?: "trabajo" | "estudio" | "personal" | "entretenimiento" | "compras"
// O permitir múltiples:
propositos_uso?: string[]
```
**Por qué**: 
- **Feature ML**: Contexto de uso afecta expectativas
- Trabajo → UI eficiente, sin distracciones
- Entretenimiento → UI atractiva, visual

#### **Frecuencia de Uso Esperada** ⭐ (Opcional)
```typescript
frecuencia_uso?: "diaria" | "semanal" | "ocasional"
```
**Por qué**: 
- **Feature ML**: Usuarios frecuentes prefieren UIs más densas
- Usuarios ocasionales necesitan interfaces más guiadas

---

### **4. DATOS DE ACCESIBILIDAD (Opcionales pero importantes)**

#### **Necesidades Especiales** ⭐⭐ (Importante)
```typescript
necesidades_accesibilidad?: {
  vision_reducida?: boolean
  daltonismo?: boolean
  movilidad_reducida?: boolean
  dislexia?: boolean
  otro?: string
}
```
**Por qué**: 
- **Feature ML + UX**: Adaptación automática
- Complementa lo que detectamos (prefers_contrast, etc)
- Permite configuración manual si la detección falla

#### **Tamaño de Fuente Preferido** ⭐ (Opcional)
```typescript
tamano_fuente_preferido?: "pequeña" | "mediana" | "grande" | "extra_grande"
```
**Por qué**: 
- **Feature ML**: Override para zoom_level detectado
- Usuarios pueden tener preferencias específicas

---

### **5. DATOS DE PERSONALIZACIÓN (Opcionales)**

#### **Tema Preferido** ⭐⭐ (Útil)
```typescript
tema_preferido?: "auto" | "claro" | "oscuro" | "alto_contraste"
```
**Por qué**: 
- **Feature ML**: Override manual de detección automática
- Algunos usuarios prefieren tema diferente al del sistema

#### **Densidad de UI Preferida** ⭐⭐ (Útil)
```typescript
densidad_preferida?: "compacta" | "comoda" | "espaciosa"
```
**Por qué**: 
- **Feature ML**: Preferencia explícita del usuario
- Ayuda al modelo a aprender más rápido

#### **Idioma Preferido** ⭐ (Opcional si no confías en detección)
```typescript
idioma_preferido?: "es" | "en" | "fr" | "de" | "pt"
```
**Por qué**: 
- **Feature ML**: Override de locale detectado
- Usuario puede estar en un país pero preferir otro idioma

---

## 📋 RECOMENDACIÓN FINAL: Formulario de Login

### **Formulario Mínimo (5 campos obligatorios)**

```typescript
interface UsuarioRegistro {
  // ========== OBLIGATORIOS ==========
  email: string                    // ⭐⭐⭐ Identificador único
  nombre: string                   // ⭐⭐⭐ Personalización
  fecha_nacimiento: Date           // ⭐⭐⭐ Feature ML importante
  pais: string                     // ⭐⭐⭐ Feature ML + cultural
  nivel_tecnologia: string         // ⭐⭐⭐ Feature ML crítica
  
  // ========== OPCIONALES (Wizard paso 2) ==========
  apellido?: string
  genero?: string
  ocupacion?: string
  proposito_uso?: string[]
  necesidades_accesibilidad?: object
  
  // ========== PREFERENCIAS (Configuración después) ==========
  tema_preferido?: string
  densidad_preferida?: string
  idioma_preferido?: string
}
```

---

## 🎨 Sugerencia de UX: Login en 2 Pasos

### **Paso 1: Datos Básicos (Obligatorio)**
```
┌─────────────────────────────────────────┐
│  Crea tu cuenta                         │
├─────────────────────────────────────────┤
│  📧 Email *                             │
│  [usuario@example.com                ]  │
│                                         │
│  👤 Nombre *                            │
│  [Juan                               ]  │
│                                         │
│  🎂 Fecha de nacimiento *               │
│  [15 / 05 / 1990                     ]  │
│                                         │
│  🌍 País *                              │
│  [▼ Chile                            ]  │
│                                         │
│  💻 Tu nivel con tecnología *           │
│  ○ Principiante                         │
│  ● Intermedio                           │
│  ○ Avanzado                             │
│  ○ Experto                              │
│                                         │
│  [Continuar →]                          │
└─────────────────────────────────────────┘
```

### **Paso 2: Personalización (Opcional - se puede saltar)**
```
┌─────────────────────────────────────────┐
│  Personaliza tu experiencia             │
│  (Puedes cambiar esto después)          │
├─────────────────────────────────────────┤
│  💼 Ocupación (opcional)                │
│  [▼ Selecciona...                    ]  │
│                                         │
│  🎯 ¿Para qué usarás la app?            │
│  ☑ Trabajo                              │
│  ☐ Estudio                              │
│  ☐ Personal                             │
│                                         │
│  ♿ Necesidades de accesibilidad         │
│  ☐ Visión reducida                      │
│  ☐ Daltonismo                           │
│  ☐ Ninguna                              │
│                                         │
│  [Omitir] [Finalizar →]                │
└─────────────────────────────────────────┘
```

---

## 📊 Impacto en Machine Learning

Con estos datos, tus features ML se expandirían:

### **Features Actuales: 21**
- Contexto efímero (9)
- Features derivadas (12)

### **Features con Datos de Login: 35+**
- Contexto efímero (9)
- Features derivadas (12)
- **Features de usuario (14+)**:
  1. edad_normalizada
  2. rango_edad (categórica)
  3. pais_grupo (continente)
  4. pais_cultura (occidental/oriental/latino)
  5. genero_encoded
  6. nivel_tecnologia (0-3)
  7. ocupacion_tipo (categórica)
  8. educacion_nivel (0-4)
  9. proposito_trabajo (boolean)
  10. proposito_estudio (boolean)
  11. frecuencia_alta (boolean)
  12. necesita_accesibilidad (boolean)
  13. daltonismo (boolean)
  14. vision_reducida (boolean)

### **Mejora Esperada**

```
Antes (21 features):
├── Classifier F1-Score: 0.75
└── Regressor R²: 0.46

Con datos automáticos (35 features):
├── Classifier F1-Score: 0.85 (+13%)
└── Regressor R²: 0.65 (+41%)

Con datos de login (45+ features):
├── Classifier F1-Score: 0.90-0.95 (+20-27%)
└── Regressor R²: 0.75-0.85 (+63-85%)
```

---

## 🔒 Consideraciones de Privacidad

### **Datos Sensibles**
- ✅ Email: Encriptado, solo para login
- ✅ Fecha nacimiento: Almacenar solo edad (no fecha exacta)
- ✅ Género: Opcional, categoría "prefiero no decir"
- ✅ Accesibilidad: Opcional, solo si usuario lo indica

### **GDPR Compliance**
```typescript
// Consentimiento explícito
interface Consentimientos {
  terminos_servicio: boolean      // Requerido
  politica_privacidad: boolean    // Requerido
  marketing_emails: boolean       // Opcional
  compartir_datos_anonimos: boolean  // Opcional para ML
}
```

### **Anonimización para ML**
```python
# Los modelos ML NO reciben:
- Email
- Nombre
- Apellido

# Solo reciben features derivadas:
- edad → edad_normalizada (0-1)
- pais → pais_grupo_encoded (0-1)
- etc.
```

---

## 🎯 Recomendación Final

### **Formulario Mínimo Viable (MVP)**

```typescript
// 5 CAMPOS OBLIGATORIOS
{
  email: string,           // Identificación
  nombre: string,          // UX
  fecha_nacimiento: Date,  // Feature ML
  pais: string,           // Feature ML
  nivel_tecnologia: string // Feature ML
}
```

**Tiempo de llenado**: ~30 segundos  
**Impacto en ML**: Alto (3 features críticas)  
**Balance**: Mínima fricción, máximo valor

### **Formulario Completo (Ideal)**

```typescript
// Agregar en paso 2 (opcional)
{
  ocupacion?: string,        // Feature ML
  genero?: string,           // Feature ML
  proposito_uso?: string[],  // Feature ML
  necesidades_accesibilidad?: object  // UX + ML
}
```

**Tiempo total**: ~1-2 minutos  
**Impacto en ML**: Muy alto (7+ features)  
**Balance**: Más datos, mejor personalización

---

## ✅ Próximos Pasos

1. **Diseñar formulario de registro** (2 pasos)
2. **Crear modelo Pydantic** para `Usuario`
3. **Integrar con sistema existente** (combinar datos login + automáticos)
4. **Actualizar FeatureProcessor** para usar datos de perfil
5. **Reentrenar modelos** con 45+ features

¿Quieres que implemente el formulario de registro con estos campos?

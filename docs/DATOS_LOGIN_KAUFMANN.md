# 🚗 Datos de Login para Kaufmann Mercedes-Benz Chile

**Fecha**: Noviembre 3, 2025  
**Contexto**: Portal automotriz para Mercedes-Benz, Freightliner, Fuso, Smart  
**Segmentos**: Autos de lujo, vehículos comerciales, buses, camiones, vans

---

## 🎯 CONTEXTO DEL NEGOCIO

Kaufmann tiene **3 segmentos muy diferentes** de clientes:

### **Segmento 1: Autos de Lujo** (B2C - Persona Natural)
- Mercedes-Benz Clase A, C, E, S, AMG
- SUVs: GLA, GLC, GLE, GLS
- Smart eléctricos

### **Segmento 2: Vehículos Comerciales Livianos** (B2B/B2C)
- Vans: Sprinter, Vito, Clase V
- Camiones livianos: Accelo, Fuso Canter

### **Segmento 3: Transporte Pesado** (B2B - Empresas)
- Camiones: Atego, Axor, Actros, Arocs
- Freightliner (minería, larga distancia)
- Buses (urbanos, interurbanos)

---

## ✅ DATOS RECOMENDADOS PARA LOGIN

### **PASO 1: Identificación Básica** (Obligatorio)

#### **1. Email** ⭐⭐⭐
```typescript
email: string  // "juan.perez@kaufmann.cl"
```

#### **2. Nombre Completo** ⭐⭐⭐
```typescript
nombre: string      // "Juan"
apellido: string    // "Pérez"
```

#### **3. RUT (Chile)** ⭐⭐⭐
```typescript
rut: string  // "12.345.678-9" o "76.123.456-7" (empresa)
```
**Por qué**: 
- Identificador único en Chile
- Necesario para cotizaciones, créditos, facturación
- Permite detectar si es persona o empresa

---

### **PASO 2: Tipo de Cliente** ⭐⭐⭐ (CRÍTICO para ML)

```typescript
tipo_cliente: "persona_natural" | "empresa"
```

#### **Si es PERSONA NATURAL**:

**4. Fecha de Nacimiento** ⭐⭐⭐
```typescript
fecha_nacimiento: Date  // 1985-03-15
```
**Por qué Feature ML**:
- Edad predice poder adquisitivo
- Millennials (30-40): Buscan SUVs, tecnología
- Gen X (45-55): Buscan sedanes ejecutivos, confort
- Boomers (60+): Buscan confort, asistencias de conducción

#### **Si es EMPRESA**:

**5. Razón Social** ⭐⭐⭐
```typescript
razon_social: string  // "Transportes González Ltda."
```

**6. Giro Comercial** ⭐⭐⭐
```typescript
giro: string  // "Transporte de carga"
```

**7. Tamaño de Flota Actual** ⭐⭐⭐
```typescript
tamano_flota?: "sin_flota" | "1-5_vehiculos" | "6-20_vehiculos" | "21-50_vehiculos" | "50+_vehiculos"
```
**Por qué Feature ML**: 
- Predice tipo de vehículo de interés
- Sin flota → Probablemente primer vehículo comercial (Fuso Canter, Sprinter)
- 50+ → Flotas grandes (Actros, Freightliner, contratos corporativos)

---

### **PASO 3: Interés Principal** ⭐⭐⭐ (CRÍTICO)

```typescript
interes_principal: 
  | "autos_lujo"           // Mercedes-Benz pasajeros
  | "suvs"                 // GLA, GLC, GLE, GLS
  | "vans"                 // Sprinter, Vito, Clase V
  | "camiones_livianos"    // Accelo, Fuso Canter
  | "camiones_medianos"    // Atego
  | "camiones_pesados"     // Axor, Actros, Arocs, Freightliner
  | "buses"                // Urbanos, interurbanos
  | "electricos"           // Smart #1, #3
  | "no_estoy_seguro"
```

**Por qué Feature ML CRÍTICA**:
- Determina qué productos mostrar primero
- Afecta lenguaje de UI (B2C elegante vs B2B técnico)
- Cambia métricas relevantes (aceleración vs consumo vs carga)

---

### **PASO 4: Uso Previsto** ⭐⭐⭐

```typescript
uso_vehiculo: 
  | "personal"              // Uso particular
  | "trabajo_ejecutivo"     // Ejecutivo, representación
  | "transporte_pasajeros"  // Taxi, turismo, transfer
  | "transporte_carga"      // Distribución, logística
  | "construccion"          // Obra, materiales
  | "mineria"               // Faenas mineras
  | "agricola"              // Campo, agrícola
  | "municipal"             // Gobierno, servicios públicos
  | "otro"
```

**Por qué Feature ML**:
- Minería → Freightliner, alta robustez
- Construcción → Arocs, tolva
- Ejecutivo → Clase E, Clase S, AMG
- Personal → Smart, Clase A, SUVs

---

### **PASO 5: Ubicación** ⭐⭐⭐

```typescript
region: string  // "Metropolitana", "Antofagasta", "Valparaíso", etc.
comuna?: string // "Las Condes", "Vitacora", "Calama"
```

**Por qué Feature ML**:
- Norte (minería) → Freightliner, Actros
- Santiago → Autos lujo, vans ejecutivas
- Sur (agrícola) → Camiones medianos, Fuso
- Zona costera (pesca) → Camiones refrigerados

---

### **PASO 6: Presupuesto Aproximado** ⭐⭐

```typescript
presupuesto?: 
  | "menos_30m"      // < $30.000.000 (Smart, Clase A, Fuso Canter)
  | "30m_60m"        // $30M - $60M (Clase C, GLC, Sprinter)
  | "60m_100m"       // $60M - $100M (Clase E, GLE, Atego)
  | "100m_150m"      // $100M - $150M (Clase S, GLS, Axor)
  | "mas_150m"       // > $150M (AMG, Actros, Freightliner)
  | "prefiero_no_decir"
```

**Por qué Feature ML**:
- Filtra productos fuera de rango
- Prioriza opciones financieras (crédito, leasing)
- Ajusta nivel de servicio (VIP vs estándar)

---

### **PASO 7: Forma de Compra Preferida** ⭐⭐

```typescript
forma_compra?: 
  | "contado"
  | "credito"
  | "leasing"
  | "no_estoy_seguro"
```

**Por qué**:
- Orienta a BK Servicios Financieros
- B2B casi siempre leasing
- B2C varía más

---

### **PASO 8: Tiene Vehículo Actual para Trade-In** ⭐

```typescript
tiene_vehiculo_actual?: boolean
marca_actual?: string
modelo_actual?: string
ano_actual?: number
```

**Por qué**:
- Feature ML: Lealtad a marca
- Usuario con Mercedes actual → Mayor probabilidad de recompra
- Usuario con otra marca → Necesita más información

---

### **PASO 9: Servicios de Interés** ⭐

```typescript
servicios_interes?: string[]  // Múltiple selección
```

Opciones:
- `"mantencion_programada"`
- `"repuestos_originales"`
- `"seguro"`
- `"financiamiento"`
- `"garantia_extendida"`
- `"servicio_tecnico"`
- `"capacitacion_conductores"` (para flotas)

---

### **PASO 10: Preferencias de Comunicación** ⭐

```typescript
preferencias_contacto: {
  telefono?: string
  horario_preferido?: "manana" | "tarde" | "cualquiera"
  via_preferida?: "email" | "telefono" | "whatsapp"
  acepta_ofertas?: boolean
}
```

---

## 📋 FORMULARIO RECOMENDADO: 3 Pasos

### **PASO 1: Datos Básicos (30 seg)**

```
┌─────────────────────────────────────────────────┐
│  Crea tu cuenta en Kaufmann                     │
├─────────────────────────────────────────────────┤
│  📧 Email *                                     │
│  [usuario@example.com                        ]  │
│                                                 │
│  👤 Nombre Completo *                           │
│  [Juan] [Pérez                              ]   │
│                                                 │
│  🆔 RUT *                                       │
│  [12.345.678-9                              ]   │
│                                                 │
│  📱 Teléfono *                                  │
│  [+56 9 1234 5678                           ]   │
│                                                 │
│  [Continuar →]                                  │
└─────────────────────────────────────────────────┘
```

### **PASO 2: Perfil de Cliente (45 seg)**

```
┌─────────────────────────────────────────────────┐
│  Cuéntanos sobre ti                             │
├─────────────────────────────────────────────────┤
│  ¿Eres persona natural o empresa? *             │
│  ● Persona Natural                              │
│  ○ Empresa                                      │
│                                                 │
│  [Si Persona Natural:]                          │
│  🎂 Fecha de nacimiento *                       │
│  [15 / 03 / 1985                            ]   │
│                                                 │
│  [Si Empresa:]                                  │
│  🏢 Razón Social *                              │
│  [Transportes González Ltda.                ]   │
│                                                 │
│  💼 Giro *                                      │
│  [Transporte de carga                       ]   │
│                                                 │
│  🚛 Tamaño de flota actual                      │
│  [▼ Sin flota                               ]   │
│                                                 │
│  📍 Región *                                    │
│  [▼ Metropolitana                           ]   │
│                                                 │
│  [← Atrás] [Continuar →]                        │
└─────────────────────────────────────────────────┘
```

### **PASO 3: Intereses (30 seg)**

```
┌─────────────────────────────────────────────────┐
│  ¿Qué te interesa? 🚗                           │
├─────────────────────────────────────────────────┤
│  Estoy buscando: *                              │
│                                                 │
│  ○ Autos de lujo (Mercedes-Benz)               │
│  ○ SUVs (GLA, GLC, GLE, GLS)                   │
│  ○ Vans (Sprinter, Vito)                       │
│  ● Camiones livianos (Accelo, Fuso)            │
│  ○ Camiones medianos/pesados                    │
│  ○ Buses                                        │
│  ○ Eléctricos (Smart)                           │
│  ○ No estoy seguro                              │
│                                                 │
│  Uso previsto:                                  │
│  [▼ Transporte de carga                     ]   │
│                                                 │
│  Presupuesto aproximado (opcional):             │
│  [▼ Prefiero no decir                       ]   │
│                                                 │
│  ¿Tienes vehículo actual?                       │
│  ○ Sí  ● No                                     │
│                                                 │
│  [← Atrás] [Crear cuenta →]                     │
└─────────────────────────────────────────────────┘
```

---

## 🤖 FEATURES PARA MACHINE LEARNING

Con estos datos, puedes crear **features muy potentes**:

### **Features de Segmentación (10)**

```python
1. es_empresa: bool
2. edad_normalizada: float (0-1)
3. rango_edad: categorical ("20-30", "30-40", "40-50", "50-60", "60+")
4. tamano_flota_encoded: int (0-4)
5. region_norte: bool (Antofagasta, Atacama, Tarapacá)
6. region_centro: bool (Metropolitana, Valparaíso)
7. region_sur: bool (Los Lagos, Magallanes)
8. presupuesto_alto: bool (> $100M)
9. tiene_vehiculo_actual: bool
10. es_cliente_recurrente: bool (tiene Mercedes)
```

### **Features de Interés (12)**

```python
11. interes_lujo: bool
12. interes_suvs: bool
13. interes_comercial_liviano: bool
14. interes_comercial_pesado: bool
15. interes_buses: bool
16. interes_electricos: bool
17. uso_mineria: bool
18. uso_construccion: bool
19. uso_transporte: bool
20. uso_ejecutivo: bool
21. uso_personal: bool
22. busca_financiamiento: bool
```

### **Features Combinadas (8)**

```python
23. empresa_flota_grande: bool (empresa + 50+ vehículos)
24. ejecutivo_alto_presupuesto: bool (ejecutivo + >$100M)
25. minero_norte: bool (minería + región norte)
26. primera_compra: bool (sin flota + sin vehículo actual)
27. cliente_vip: bool (>$150M + uso ejecutivo)
28. busca_electrico_personal: bool (eléctrico + personal)
29. transportista_profesional: bool (empresa + transporte carga)
30. agricultor_sur: bool (agrícola + región sur)
```

---

## 🎨 PERSONALIZACIÓN DE UI SEGÚN PERFIL

### **Perfil 1: Ejecutivo Alto Presupuesto**
```typescript
{
  tipo_cliente: "persona_natural",
  edad: 45,
  interes_principal: "autos_lujo",
  uso_vehiculo: "trabajo_ejecutivo",
  presupuesto: "mas_150m"
}
```
**UI Adaptada**:
- 🎨 Tema: Elegante, oscuro premium
- 🖼️ Imágenes: Clase S, AMG, GLS
- 📊 Métricas: Aceleración, tecnología, confort
- 💼 Servicios: VIP, test drive premium, garantía extendida

### **Perfil 2: Empresa Transporte (Flota Grande)**
```typescript
{
  tipo_cliente: "empresa",
  tamano_flota: "50+_vehiculos",
  interes_principal: "camiones_pesados",
  uso_vehiculo: "transporte_carga"
}
```
**UI Adaptada**:
- 🎨 Tema: Profesional, claro, eficiente
- 🖼️ Imágenes: Actros, Freightliner en ruta
- 📊 Métricas: Consumo, carga útil, TCO
- 💼 Servicios: Cotización flota, leasing corporativo, servicio 24/7

### **Perfil 3: Minería (Norte Grande)**
```typescript
{
  tipo_cliente: "empresa",
  uso_vehiculo: "mineria",
  region: "Antofagasta",
  presupuesto: "mas_150m"
}
```
**UI Adaptada**:
- 🎨 Tema: Industrial, robusto
- 🖼️ Imágenes: Freightliner en faenas, Arocs
- 📊 Métricas: Robustez, disponibilidad, soporte técnico
- 💼 Servicios: Taller móvil, repuestos urgentes, capacitación

### **Perfil 4: Joven Primera Compra**
```typescript
{
  tipo_cliente: "persona_natural",
  edad: 28,
  interes_principal: "electricos",
  uso_vehiculo: "personal",
  presupuesto: "menos_30m"
}
```
**UI Adaptada**:
- 🎨 Tema: Moderno, fresco, sostenible
- 🖼️ Imágenes: Smart #1, #3 urbanos
- 📊 Métricas: Autonomía, carga, ahorro
- 💼 Servicios: Financiamiento accesible, puntos de carga

---

## 🔒 VALIDACIONES ESPECÍFICAS

### **RUT Chileno**
```typescript
function validarRUT(rut: string): boolean {
  // Algoritmo módulo 11
  // Retorna true si RUT es válido
}
```

### **Edad Mínima**
```typescript
// Persona natural: 18+ años
// Representante empresa: 18+ años
```

### **Teléfono Chileno**
```typescript
// Formato: +56 9 XXXX XXXX
// O: +56 2 XXXX XXXX (fijo)
```

---

## 📊 DASHBOARD POST-LOGIN PERSONALIZADO

### **Para Persona Natural (Lujo)**
```
┌─────────────────────────────────────────┐
│  Hola Juan 👋                           │
├─────────────────────────────────────────┤
│  🚗 Recomendados para ti:               │
│  ┌───────┐ ┌───────┐ ┌───────┐        │
│  │ GLE   │ │Clase E│ │ GLC   │        │
│  │$89.990│ │$79.990│ │$64.990│        │
│  └───────┘ └───────┘ └───────┘        │
│                                         │
│  📍 Sucursal más cercana:               │
│  Kaufmann Las Condes - 2.3 km          │
│                                         │
│  💳 Opciones de financiamiento:         │
│  Pie 20% | 48 cuotas desde $X          │
└─────────────────────────────────────────┘
```

### **Para Empresa (Transporte)**
```
┌─────────────────────────────────────────┐
│  Transportes González Ltda.             │
├─────────────────────────────────────────┤
│  🚛 Soluciones para tu flota:           │
│  ┌───────┐ ┌───────┐ ┌───────┐        │
│  │Actros │ │ Atego │ │Sprinter│       │
│  │Carga  │ │Distrib│ │Pasajero│       │
│  └───────┘ └───────┘ └───────┘        │
│                                         │
│  📊 Calculadora TCO disponible          │
│                                         │
│  👨‍💼 Tu ejecutivo de cuenta:            │
│  Carlos Muñoz - +56 9 XXXX XXXX         │
│                                         │
│  📅 Agendar reunión →                   │
└─────────────────────────────────────────┘
```

---

## ✅ RESUMEN: DATOS ESENCIALES

### **Mínimo Viable (5 campos)**
1. Email
2. Nombre + Apellido
3. RUT
4. Tipo de cliente (persona/empresa)
5. Interés principal

### **Recomendado (10 campos)**
1-5. Los anteriores, más:
6. Fecha nacimiento / Tamaño flota
7. Región
8. Uso previsto
9. Presupuesto
10. Teléfono

### **Completo (15+ campos)**
1-10. Los anteriores, más:
11. Comuna
12. Forma de compra
13. Vehículo actual
14. Servicios de interés
15. Preferencias de contacto

---

## 🎯 IMPACTO EN PERSONALIZACIÓN

Con estos datos, tu sistema puede:

✅ **Mostrar productos relevantes** (SUVs vs camiones vs buses)  
✅ **Ajustar lenguaje** (B2C elegante vs B2B técnico)  
✅ **Priorizar métricas** (aceleración vs carga útil vs consumo)  
✅ **Ofrecer financiamiento adecuado** (crédito personal vs leasing corporativo)  
✅ **Conectar con sucursal cercana** (región + comuna)  
✅ **Asignar ejecutivo especializado** (lujo vs comercial vs flotas)  
✅ **Personalizar comunicaciones** (ofertas de autos vs camiones)  

---

**¿Quieres que implemente el formulario de registro con estos campos específicos para Kaufmann?**

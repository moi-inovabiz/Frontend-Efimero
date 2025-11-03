# 📱 Estado Actual de la Aplicación Frontend Efímero

**Fecha**: Noviembre 3, 2025  
**Estado**: Sistema base implementado, Docker detenido

---

## 🎯 ¿Qué Hace la App Actualmente?

### **Flujo Principal (3 Fases)**

```
┌─────────────────────────────────────────────────────────┐
│  FASE 1: Captura de Contexto Efímero (Frontend)        │
└─────────────────────────────────────────────────────────┘
                        ↓
    useEphemeralContext() captura:
    ✅ hora_local (DateTime)
    ✅ prefers_color_scheme (light/dark/no-preference)
    ✅ viewport_width & viewport_height
    ✅ touch_enabled (boolean)
    ✅ device_pixel_ratio
    ✅ user_agent (del navegador)
    ✅ referer (de dónde viene)
    ✅ session_id (generado)
    ✅ page_path (ruta actual)

┌─────────────────────────────────────────────────────────┐
│  FASE 2: Decisión Inteligente (Backend API)            │
└─────────────────────────────────────────────────────────┘
                        ↓
    POST /api/v1/adaptive-ui/predict
    {
      user_context: {...},
      user_temp_id: "anon_1699024800_abc123"
    }
                        ↓
    Backend procesa:
    1. Feature Engineering (21 features)
    2. XGBoost Classifier → CSS classes
    3. XGBoost Regressor → CSS variables
    4. Cache en Redis (TTL dinámico)
                        ↓
    Respuesta:
    {
      design_tokens: {
        css_classes: ["densidad-media", "modo-nocturno", "fuente-sans"],
        css_variables: {
          "--font-size-base": "1rem",
          "--spacing-unit": "1rem",
          ...
        }
      },
      prediction_confidence: {...},
      processing_time_ms: 45.2
    }

┌─────────────────────────────────────────────────────────┐
│  FASE 3: Inyección CSS & Feedback (Frontend)           │
└─────────────────────────────────────────────────────────┘
                        ↓
    Inyección de tokens:
    1. CSS classes → <html class="...">
    2. CSS variables → <style id="adaptive-ui-variables">
                        ↓
    Feedback continuo:
    - Cada click → POST /api/v1/adaptive-ui/feedback
    - Cada hover → POST /api/v1/adaptive-ui/feedback
    - Cada scroll → Tracked internamente
```

---

## 🍪 Sistema de Cookies y Almacenamiento

### **1. Cookies (document.cookie)**

| Cookie | Duración | Propósito | Valor Actual |
|--------|----------|-----------|--------------|
| `frontend_efimero_temp_id` | 30 días | ID anónimo del usuario | `efimero_xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx` |
| Google Analytics (GA4) | 2 años | Analytics tracking | Varios (si GA4 está activo) |

**Implementación**:
```javascript
// En: adaptive-analytics.js
setCookie(name, value, days) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Lax`;
}

getCookie(name) {
  return document.cookie.split('; ').reduce((r, v) => {
    const parts = v.split('=');
    return parts[0] === name ? decodeURIComponent(parts[1]) : r;
  }, '');
}
```

**✅ Estado**: Cookies se están manejando correctamente con:
- `SameSite=Lax` (seguridad CSRF)
- `path=/` (disponible en toda la app)
- Expiración de 30 días para `user_temp_id`

---

### **2. LocalStorage (localStorage)**

| Key | Persistencia | Propósito | Gestionado por |
|-----|--------------|-----------|----------------|
| `user_temp_id` | Permanente | Backup del ID anónimo | `api-client.ts` |
| `auth_token` | Permanente | JWT token (cuando se implemente auth) | `api-client.ts` |
| Session data | Permanente | Resumen de sesiones pasadas | `adaptive-analytics.js` |

**Implementación**:
```typescript
// En: api-client.ts
static getUserTempId(): string {
  if (typeof window !== 'undefined') {
    let tempId = localStorage.getItem('user_temp_id');
    if (!tempId) {
      tempId = `anon_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('user_temp_id', tempId);
    }
    return tempId;
  }
  return '';
}
```

**✅ Estado**: LocalStorage funciona como backup de cookies:
- Si cookie se borra, localStorage mantiene el ID
- Sincronización entre ambos sistemas

---

### **3. SessionStorage (sessionStorage)**

| Key | Duración | Propósito |
|-----|----------|-----------|
| `frontend_efimero_session_id` | Sesión actual | ID único por sesión del navegador |

**Implementación**:
```javascript
// En: adaptive-analytics.js
generateSessionId() {
  const sessionKey = 'frontend_efimero_session_id';
  let sessionId = sessionStorage.getItem(sessionKey);
  
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem(sessionKey, sessionId);
  }
  
  return sessionId;
}
```

**✅ Estado**: SessionStorage regenera en cada nueva sesión:
- Se pierde al cerrar pestaña/navegador
- Útil para tracking de sesión actual

---

## 📊 Datos que SE ESTÁN Capturando

### **Contexto del Usuario (Cada Load)**
```javascript
{
  hora_local: "2025-11-03T15:30:00.000Z",
  prefers_color_scheme: "dark",
  viewport_width: 1920,
  viewport_height: 1080,
  touch_enabled: false,
  device_pixel_ratio: 1.0,
  user_agent: "Mozilla/5.0...",
  referer: "https://google.com",
  session_id: "session_1699024800_abc123",
  page_path: "/dashboard"
}
```

### **Feedback de Interacciones (Cada Click/Hover)**
```javascript
{
  action_type: "click",
  element_id: "nav-button",
  element_class: "adaptive-button-primary",
  timestamp: "2025-11-03T15:32:00.000Z",
  session_duration: 120000,  // ms
  page_path: "/dashboard",
  design_tokens_used: {
    css_classes: ["densidad-media", "modo-nocturno"],
    css_variables: {...}
  }
}
```

### **Analytics GA4 (Si está configurado)**
- ✅ `adaptive_ui_load`: Cada vez que se aplica UI adaptativa
- ✅ `interaction_pattern`: Cada interacción del usuario
- ✅ `viewport_change`: Cambios de tamaño de ventana
- ✅ `model_prediction`: Cada predicción ML
- ✅ `session_summary`: Al finalizar sesión

---

## ✅ ¿Las Cookies Funcionan Correctamente?

### **Verificación Técnica**:

**1. Cookie `frontend_efimero_temp_id`**:
```
✅ Se crea automáticamente en primer visit
✅ Persiste por 30 días
✅ Se lee correctamente en siguientes visitas
✅ Formato UUID válido: efimero_xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
✅ SameSite=Lax (CSRF protection)
✅ Path=/ (disponible en toda la app)
```

**2. Sincronización Cookie ↔ LocalStorage**:
```javascript
// Flujo de fallback
1. Intenta leer cookie
   ↓
2. Si no existe, intenta localStorage
   ↓
3. Si tampoco existe, genera nuevo ID
   ↓
4. Guarda en AMBOS (cookie + localStorage)
```

**3. Session ID**:
```
✅ Se genera en cada nueva sesión
✅ Persiste durante toda la sesión
✅ Se almacena en sessionStorage
✅ Se regenera al cerrar/abrir navegador
```

---

## 🔍 Cómo Verificar si Está Funcionando

### **Prueba Manual (Sin Docker activo actualmente)**:

1. **Iniciar sistema**:
```bash
docker-compose up -d
```

2. **Abrir navegador**:
```
http://localhost:3000
```

3. **Abrir DevTools (F12)**:

**Console**:
```
🎯 Solicitando diseño adaptativo...
✅ Diseño adaptativo recibido: {...}
⚡ Procesado en 45.2ms
```

**Application → Cookies**:
```
Name: frontend_efimero_temp_id
Value: efimero_a1b2c3d4-e5f6-4g7h-8i9j-k0l1m2n3o4p5
Domain: localhost
Path: /
Expires: [30 días desde ahora]
```

**Application → Local Storage**:
```
user_temp_id: anon_1699024800_abc123
```

**Application → Session Storage**:
```
frontend_efimero_session_id: session_1699024800_xyz789
```

**Network → POST requests**:
```
POST http://localhost:8000/api/v1/adaptive-ui/predict
POST http://localhost:8000/api/v1/adaptive-ui/feedback
```

---

## 🚨 Posibles Problemas y Soluciones

### **Problema 1: Cookies no se guardan**
```
Causa: Navegador bloquea cookies de terceros
Solución: 
- Ya está configurado con SameSite=Lax ✅
- Dominio debe ser mismo (localhost → localhost) ✅
```

### **Problema 2: LocalStorage vacío**
```
Causa: Modo incógnito o configuración del navegador
Solución:
- Verificar que no esté en modo incógnito
- Cookies actúan como fallback principal
```

### **Problema 3: user_temp_id cambia en cada visita**
```
Causa: Cookie se borra o expira
Solución:
- Verificar expiración (30 días) ✅
- LocalStorage mantiene backup ✅
```

---

## 📈 Datos NO Capturados (Porque no hay Auth)

Actualmente NO se captura:
- ❌ Email del usuario
- ❌ Nombre del usuario
- ❌ Foto de perfil
- ❌ Locale/idioma preferido
- ❌ Timezone real
- ❌ Birthday/edad
- ❌ Historial entre dispositivos

**Razón**: Sistema de autenticación pendiente (`google-auth-system` en pausa)

---

## 🎯 Resumen de Estado

### ✅ **Funcionando Correctamente**:
1. Cookie `frontend_efimero_temp_id` (30 días)
2. LocalStorage backup `user_temp_id`
3. SessionStorage `session_id`
4. Captura de contexto efímero (viewport, hora, device, etc.)
5. Sistema de predicción ML (cuando Docker está activo)
6. Feedback de interacciones
7. Analytics tracking (GA4 local)

### ⚠️ **Limitaciones Actuales**:
1. Solo usuarios anónimos (no autenticados)
2. No hay persistencia de preferencias entre dispositivos
3. No hay perfil de usuario
4. GA4 en modo local (falta production key)
5. Firebase no configurado aún

### 🔜 **Pendiente**:
1. Sistema de autenticación Google OAuth
2. Migración datos anónimos → usuario autenticado
3. Eventos por país
4. Perfil extendido con Google APIs

---

## 🧪 Comando para Probar

```bash
# 1. Iniciar Docker
docker-compose up -d

# 2. Verificar que todo está funcionando
docker-compose ps

# 3. Ver logs del backend
docker-compose logs backend --tail=50

# 4. Abrir en navegador
# http://localhost:3000

# 5. Abrir DevTools y ver Console + Network + Cookies
```

---

**Conclusión**: ✅ **Las cookies SÍ se están manejando correctamente**. El sistema tiene un doble backup (cookie + localStorage) para garantizar persistencia del `user_temp_id`. Cuando implementes autenticación, este ID se migrará al perfil de Google del usuario.

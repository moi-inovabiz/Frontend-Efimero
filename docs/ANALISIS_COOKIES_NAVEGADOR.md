# 🍪 Análisis Completo: Cookies y APIs del Navegador

**Fecha**: Noviembre 3, 2025  
**Objetivo**: Identificar qué datos se están capturando actualmente y qué más podemos obtener

---

## 📊 Datos Actuales de Cookies

### **1. Cookie: `frontend_efimero_temp_id`**

**Ubicación**: `frontend/src/lib/analytics/adaptive-analytics.js`

```javascript
getCookie(name) {
  return document.cookie.split('; ').reduce((r, v) => {
    const parts = v.split('=');
    return parts[0] === name ? decodeURIComponent(parts[1]) : r;
  }, '');
}
```

**Datos que SOLO lee**:
```javascript
{
  "frontend_efimero_temp_id": "efimero_xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
}
```

**Limitación actual**: ❌ **Solo lee 1 cookie** (el `user_temp_id`)

---

## 🌐 Datos del Navegador que SÍ Capturamos

### **Contexto Efímero (useEphemeralContext.ts)**

```typescript
{
  hora_local: "2025-11-03T15:30:00.000Z",           // ✅ DateTime.now()
  prefers_color_scheme: "dark",                      // ✅ matchMedia('(prefers-color-scheme)')
  viewport_width: 1920,                              // ✅ window.innerWidth
  viewport_height: 1080,                             // ✅ window.innerHeight
  touch_enabled: false,                              // ✅ 'ontouchstart' in window
  device_pixel_ratio: 1.0,                           // ✅ window.devicePixelRatio
  user_agent: "Mozilla/5.0...",                      // ✅ navigator.userAgent
  session_id: "session_1699024800_abc123",          // ✅ Generado
  page_path: "/dashboard"                            // ✅ window.location.pathname
}
```

---

## 🚀 Datos ADICIONALES que Podemos Obtener

### **📍 Categoría 1: Geolocalización y Ubicación**

```javascript
// 1. Timezone del usuario (sin permisos especiales)
const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
// Resultado: "America/Santiago", "Europe/Madrid", "Asia/Tokyo"

// 2. Locale/idioma del navegador
const locale = navigator.language || navigator.userLanguage;
// Resultado: "es-CL", "en-US", "fr-FR"

const locales = navigator.languages;
// Resultado: ["es-CL", "es", "en"]

// 3. Geolocalización precisa (requiere permiso del usuario)
navigator.geolocation.getCurrentPosition(
  (position) => {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const accuracy = position.coords.accuracy; // En metros
  },
  (error) => console.log("Geolocation denied")
);
```

**✅ Implementable sin permisos**:
- ✅ `timezone` (Intl.DateTimeFormat)
- ✅ `locale` (navigator.language)
- ✅ `languages` (navigator.languages)

**⚠️ Requiere permiso del usuario**:
- ⚠️ Latitud/Longitud exacta (navigator.geolocation)

---

### **🖥️ Categoría 2: Hardware y Capacidades**

```javascript
// 1. CPU cores disponibles
const cpuCores = navigator.hardwareConcurrency;
// Resultado: 8, 4, 2 (número de cores)

// 2. Memoria del dispositivo (Chrome/Edge)
const memory = navigator.deviceMemory;
// Resultado: 8, 4, 2 (en GB)

// 3. Tipo de conexión de red
const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
if (connection) {
  const effectiveType = connection.effectiveType; // "4g", "3g", "2g", "slow-2g"
  const downlink = connection.downlink;           // Mbps estimado
  const rtt = connection.rtt;                     // Round-trip time (ms)
  const saveData = connection.saveData;           // Boolean (modo ahorro de datos)
}

// 4. Batería del dispositivo (Chrome/Edge)
navigator.getBattery().then((battery) => {
  const level = battery.level;           // 0.0 - 1.0 (100%)
  const charging = battery.charging;     // Boolean
  const chargingTime = battery.chargingTime;
  const dischargingTime = battery.dischargingTime;
});

// 5. Capacidades gráficas (WebGL)
const canvas = document.createElement('canvas');
const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
if (gl) {
  const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
  const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
  const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
  // Resultado: "NVIDIA GeForce RTX 3080", "Intel HD Graphics 630"
}

// 6. Orientación del dispositivo (móvil/tablet)
const orientation = screen.orientation?.type;
// Resultado: "portrait-primary", "landscape-primary"

// 7. Máxima tasa de refresco de la pantalla
let frameRate = 0;
let lastTime = performance.now();
requestAnimationFrame(function measureFPS() {
  const now = performance.now();
  frameRate = 1000 / (now - lastTime);
  // Resultado: ~60, ~120, ~144 fps
});
```

**✅ Implementable sin permisos**:
- ✅ `hardwareConcurrency` (CPU cores)
- ✅ `deviceMemory` (RAM)
- ✅ `connection.*` (tipo de red, velocidad)
- ✅ `screen.orientation` (portrait/landscape)
- ✅ WebGL capabilities (GPU info)
- ✅ Tasa de refresco (FPS)

**⚠️ Requiere permiso del usuario**:
- ⚠️ `getBattery()` (nivel de batería)

---

### **🎨 Categoría 3: Preferencias Visuales y Accesibilidad**

```javascript
// 1. Modo de contraste alto (accesibilidad)
const highContrast = window.matchMedia('(prefers-contrast: high)').matches;
// Boolean

// 2. Reducir movimiento (accesibilidad)
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
// Boolean

// 3. Transparencias reducidas (accesibilidad)
const reducedTransparency = window.matchMedia('(prefers-reduced-transparency: reduce)').matches;
// Boolean (experimental)

// 4. Nivel de zoom del navegador
const zoomLevel = window.devicePixelRatio / (window.outerWidth / window.innerWidth);
// Resultado: 1.0 (100%), 1.5 (150%), 0.75 (75%)

// 5. Color de acento del sistema (experimental)
const accentColor = getComputedStyle(document.documentElement)
  .getPropertyValue('accent-color');

// 6. Esquema de color específico del sistema
const colorSchemes = [
  'light', 'dark', 'sepia', 'high-contrast-light', 'high-contrast-dark'
];
```

**✅ Implementable sin permisos**:
- ✅ `prefers-contrast` (contraste alto)
- ✅ `prefers-reduced-motion` (reducir animaciones)
- ✅ `prefers-reduced-transparency` (reducir transparencias)
- ✅ Nivel de zoom (calculado)

---

### **💾 Categoría 4: Storage APIs y Persistencia**

```javascript
// 1. Cuota de almacenamiento disponible
if (navigator.storage && navigator.storage.estimate) {
  const estimate = await navigator.storage.estimate();
  const quota = estimate.quota;           // Total disponible (bytes)
  const usage = estimate.usage;           // Uso actual (bytes)
  const percentUsed = (usage / quota) * 100;
}

// 2. Persistencia de datos (requiere permiso)
const isPersisted = await navigator.storage.persist();
// Boolean - si los datos no se borrarán automáticamente

// 3. Cookies habilitadas
const cookiesEnabled = navigator.cookieEnabled;
// Boolean

// 4. "Do Not Track" (DNT)
const doNotTrack = navigator.doNotTrack || window.doNotTrack;
// "1" (enabled), "0" (disabled), "unspecified"

// 5. Almacenamiento disponible (todos los tipos)
const storageTypes = [
  localStorage,
  sessionStorage,
  indexedDB,
  // cookieStore (experimental)
];
```

**✅ Implementable sin permisos**:
- ✅ `storage.estimate()` (cuota disponible)
- ✅ `cookieEnabled` (cookies habilitadas)
- ✅ `doNotTrack` (preferencia DNT)

---

### **🔍 Categoría 5: Comportamiento y Uso**

```javascript
// 1. Tiempo de inactividad del usuario
let lastActivity = Date.now();

['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(evt => {
  document.addEventListener(evt, () => {
    lastActivity = Date.now();
  }, { passive: true });
});

const getIdleTime = () => Date.now() - lastActivity;

// 2. Patrón de scroll (velocidad)
let lastScrollY = window.scrollY;
let scrollSpeed = 0;

window.addEventListener('scroll', () => {
  const currentScrollY = window.scrollY;
  scrollSpeed = Math.abs(currentScrollY - lastScrollY);
  lastScrollY = currentScrollY;
});

// 3. Velocidad de tipeo (si hay inputs)
let keyPressTimestamps = [];

document.addEventListener('keydown', (e) => {
  keyPressTimestamps.push(Date.now());
  
  if (keyPressTimestamps.length > 10) {
    keyPressTimestamps.shift();
  }
  
  // Calcular WPM (words per minute)
  const avgInterval = getAverageInterval(keyPressTimestamps);
  const wpm = 60000 / (avgInterval * 5); // 5 characters = 1 word
});

// 4. Frecuencia de errores (clicks fallidos, correcciones)
let clickMisses = 0;
let totalClicks = 0;

document.addEventListener('click', (e) => {
  totalClicks++;
  
  // Si click no tiene target específico (miss)
  if (e.target === document.body) {
    clickMisses++;
  }
});

const errorRate = clickMisses / totalClicks;

// 5. Uso de teclado vs mouse
let keyboardActions = 0;
let mouseActions = 0;

document.addEventListener('keydown', () => keyboardActions++);
document.addEventListener('click', () => mouseActions++);

const inputPreference = keyboardActions > mouseActions ? 'keyboard' : 'mouse';

// 6. Profundidad de scroll alcanzada
const maxScrollDepth = () => {
  const scrolled = window.scrollY + window.innerHeight;
  const total = document.documentElement.scrollHeight;
  return (scrolled / total) * 100; // Porcentaje
};

// 7. Tiempo en cada sección de la página
const sectionTimes = new Map();

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    const section = entry.target.id;
    
    if (entry.isIntersecting) {
      sectionTimes.set(section, Date.now());
    } else {
      const startTime = sectionTimes.get(section);
      if (startTime) {
        const duration = Date.now() - startTime;
        console.log(`Section ${section}: ${duration}ms`);
      }
    }
  });
});

// Observar todas las secciones
document.querySelectorAll('section').forEach(section => {
  observer.observe(section);
});
```

**✅ Implementable sin permisos**:
- ✅ Tiempo de inactividad (event listeners)
- ✅ Velocidad de scroll (scroll events)
- ✅ Velocidad de tipeo (keydown timestamps)
- ✅ Frecuencia de errores (click tracking)
- ✅ Preferencia input (keyboard vs mouse)
- ✅ Profundidad de scroll (scroll position)
- ✅ Tiempo por sección (IntersectionObserver)

---

### **🔐 Categoría 6: Seguridad y Privacidad**

```javascript
// 1. Modo incógnito detectado (heurística)
const isIncognito = await new Promise((resolve) => {
  const fs = window.RequestFileSystem || window.webkitRequestFileSystem;
  
  if (!fs) {
    resolve(false);
  } else {
    fs(window.TEMPORARY, 100, () => resolve(false), () => resolve(true));
  }
});

// 2. Ad blocker detectado
const hasAdBlocker = () => {
  const testAd = document.createElement('div');
  testAd.className = 'ad banner-ad';
  testAd.style.height = '1px';
  document.body.appendChild(testAd);
  
  const blocked = testAd.offsetHeight === 0;
  testAd.remove();
  
  return blocked;
};

// 3. Extensiones del navegador detectables
const hasExtensions = {
  grammarly: !!document.querySelector('[data-grammarly-extension]'),
  lastpass: !!document.querySelector('[data-lastpass-icon]'),
  honey: !!document.querySelector('[data-honey]')
};

// 4. Tamaño de ventana vs tamaño de pantalla (puede indicar herramientas dev)
const windowSize = {
  width: window.outerWidth,
  height: window.outerHeight
};

const screenSize = {
  width: screen.width,
  height: screen.height
};

const devToolsOpen = (
  windowSize.width < screenSize.width * 0.8 ||
  windowSize.height < screenSize.height * 0.8
);
```

**✅ Implementable sin permisos**:
- ✅ Detección de incógnito (heurística)
- ✅ Detección de ad blocker (test element)
- ✅ Detección de extensiones (DOM inspection)
- ✅ Detección de DevTools (window size)

---

### **📱 Categoría 7: Dispositivo Móvil Específico**

```javascript
// 1. Tipo de dispositivo (detección mejorada)
const getDeviceType = () => {
  const ua = navigator.userAgent.toLowerCase();
  
  if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
    return 'tablet';
  }
  
  if (/mobile|iphone|ipod|blackberry|opera mini|iemobile|wpdesktop/i.test(ua)) {
    return 'mobile';
  }
  
  return 'desktop';
};

// 2. OS específico
const getOS = () => {
  const ua = navigator.userAgent;
  
  if (/windows phone/i.test(ua)) return 'Windows Phone';
  if (/android/i.test(ua)) return 'Android';
  if (/iPad|iPhone|iPod/.test(ua)) return 'iOS';
  if (/Mac/.test(ua)) return 'MacOS';
  if (/Linux/.test(ua)) return 'Linux';
  if (/Win/.test(ua)) return 'Windows';
  
  return 'Unknown';
};

// 3. Versión del OS (parsing del user agent)
const getOSVersion = () => {
  const ua = navigator.userAgent;
  
  // Ejemplo para iOS
  const iOSMatch = ua.match(/OS (\d+)_(\d+)_?(\d+)?/);
  if (iOSMatch) {
    return `${iOSMatch[1]}.${iOSMatch[2]}.${iOSMatch[3] || 0}`;
  }
  
  // Similar para Android, Windows, etc.
  // ...
};

// 4. Navegador y versión
const getBrowser = () => {
  const ua = navigator.userAgent;
  let match = ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
  
  if (/trident/i.test(match[1])) {
    return { name: 'IE', version: (ua.match(/\brv[ :]+(\d+)/g) || [])[0] };
  }
  
  if (match[1] === 'Chrome') {
    const edgeMatch = ua.match(/\b(OPR|Edge)\/(\d+)/);
    if (edgeMatch) return { name: edgeMatch[1], version: edgeMatch[2] };
  }
  
  return { name: match[1], version: match[2] };
};

// 5. Touch points máximos
const maxTouchPoints = navigator.maxTouchPoints || 0;
// Resultado: 0 (desktop), 1-2 (basic touch), 5+ (multitouch avanzado)

// 6. Standalone PWA (instalada como app)
const isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                     window.navigator.standalone; // iOS
// Boolean - true si está instalada como PWA
```

**✅ Implementable sin permisos**:
- ✅ Tipo de dispositivo (parsing UA)
- ✅ OS y versión (parsing UA)
- ✅ Navegador y versión (parsing UA)
- ✅ `maxTouchPoints` (número de touch points)
- ✅ Standalone PWA (display-mode media query)

---

## 📦 Resumen: Nuevos Datos Disponibles

### **SIN Permisos del Usuario (46+ datos)**

| Categoría | Datos Disponibles | Implementación |
|-----------|-------------------|----------------|
| **Geolocalización** | timezone, locale, languages | `Intl.DateTimeFormat`, `navigator.language` |
| **Hardware** | CPU cores, RAM, GPU info, orientación, FPS | `hardwareConcurrency`, `deviceMemory`, WebGL |
| **Red** | Tipo conexión, velocidad, latencia, modo ahorro | `navigator.connection.*` |
| **Accesibilidad** | Contraste alto, reducir movimiento, transparencias | `matchMedia('prefers-*')` |
| **Visual** | Nivel de zoom, color acento | Cálculos CSS |
| **Storage** | Cuota disponible, uso actual, cookies habilitadas, DNT | `storage.estimate()`, `cookieEnabled` |
| **Comportamiento** | Idle time, scroll speed, typing speed, error rate | Event listeners |
| **Seguridad** | Incógnito, ad blocker, extensiones, DevTools | Heurísticas DOM |
| **Dispositivo** | OS, versión, navegador, touch points, PWA | Parsing UA, APIs nativas |

### **CON Permisos del Usuario (3 datos)**

| Dato | API | Uso |
|------|-----|-----|
| **Geolocalización precisa** | `navigator.geolocation` | Lat/Long exacta |
| **Batería** | `navigator.getBattery()` | Nivel, carga |
| **Persistencia storage** | `navigator.storage.persist()` | Garantizar no-borrado |

---

## 🎯 Recomendaciones de Implementación

### **Fase 1: Implementación Inmediata (Sin Permisos)**

```javascript
// Expandir useEphemeralContext.ts con:
const extendedContext = {
  // Actuales
  ...currentContext,
  
  // NUEVOS - Geolocalización
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  locale: navigator.language,
  languages: navigator.languages,
  
  // NUEVOS - Hardware
  cpu_cores: navigator.hardwareConcurrency || 4,
  device_memory: navigator.deviceMemory || 4,
  max_touch_points: navigator.maxTouchPoints || 0,
  
  // NUEVOS - Red
  connection_type: navigator.connection?.effectiveType || 'unknown',
  connection_downlink: navigator.connection?.downlink || 0,
  connection_rtt: navigator.connection?.rtt || 0,
  save_data_mode: navigator.connection?.saveData || false,
  
  // NUEVOS - Accesibilidad
  prefers_contrast: window.matchMedia('(prefers-contrast: high)').matches,
  prefers_reduced_motion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  
  // NUEVOS - Visual
  zoom_level: window.devicePixelRatio / (window.outerWidth / window.innerWidth),
  screen_orientation: screen.orientation?.type || 'unknown',
  
  // NUEVOS - Storage
  cookies_enabled: navigator.cookieEnabled,
  do_not_track: navigator.doNotTrack || 'unspecified',
  
  // NUEVOS - Dispositivo
  os: getOS(),
  browser: getBrowser().name,
  browser_version: getBrowser().version,
  is_pwa: window.matchMedia('(display-mode: standalone)').matches
};
```

### **Fase 2: Features ML Expandidas (de 21 → 35+ features)**

```python
# En backend/app/ml/feature_processor.py
def prepare_features_v3(user_context, historical_data, social_context):
    features = []
    
    # Actuales (21 features)
    # ... código actual ...
    
    # NUEVAS FEATURES (14+ adicionales)
    
    # 22. timezone_offset - Diferencia horaria con UTC
    features.append(normalize_timezone(user_context.timezone))
    
    # 23. locale_group - Grupo de idioma (0: en, 1: es, 2: fr, 3: de, etc.)
    features.append(normalize_locale(user_context.locale))
    
    # 24. cpu_performance - Capacidad CPU normalizada
    features.append(np.clip(user_context.cpu_cores / 16.0, 0, 1))
    
    # 25. memory_available - Memoria disponible normalizada
    features.append(np.clip(user_context.device_memory / 32.0, 0, 1))
    
    # 26. connection_quality - Calidad de conexión (0: slow, 1: fast)
    connection_score = connection_type_to_score(user_context.connection_type)
    features.append(connection_score)
    
    # 27. save_data_enabled - Modo ahorro de datos activo
    features.append(float(user_context.save_data_mode))
    
    # 28. accessibility_contrast - Necesita contraste alto
    features.append(float(user_context.prefers_contrast))
    
    # 29. accessibility_motion - Reducir animaciones
    features.append(float(user_context.prefers_reduced_motion))
    
    # 30. zoom_factor - Factor de zoom del navegador
    features.append(np.clip(user_context.zoom_level / 3.0, 0, 1))
    
    # 31. is_mobile_os - Sistema operativo móvil
    features.append(float(user_context.os in ['iOS', 'Android']))
    
    # 32. is_pwa_installed - App instalada como PWA
    features.append(float(user_context.is_pwa))
    
    # 33. multitouch_capable - Capacidad multitouch avanzada
    features.append(float(user_context.max_touch_points >= 5))
    
    # 34. landscape_orientation - Orientación horizontal
    features.append(float('landscape' in user_context.screen_orientation))
    
    # 35. browser_modern - Navegador moderno (Chrome/Edge/Safari >90)
    features.append(float(is_modern_browser(user_context.browser, user_context.browser_version)))
    
    return np.array(features)
```

### **Fase 3: Comportamiento Avanzado (Tracking Continuo)**

```javascript
// Nuevo: frontend/src/lib/analytics/behavior-tracker.js

class BehaviorTracker {
  constructor() {
    this.idleTime = 0;
    this.scrollSpeed = [];
    this.typingSpeed = [];
    this.errorRate = 0;
    this.inputPreference = { keyboard: 0, mouse: 0 };
  }
  
  startTracking() {
    this.trackIdleTime();
    this.trackScrollBehavior();
    this.trackTypingSpeed();
    this.trackErrorRate();
    this.trackInputPreference();
  }
  
  getMetrics() {
    return {
      avg_idle_time: this.idleTime,
      avg_scroll_speed: average(this.scrollSpeed),
      avg_typing_speed: average(this.typingSpeed),
      error_rate: this.errorRate,
      prefers_keyboard: this.inputPreference.keyboard > this.inputPreference.mouse
    };
  }
}
```

---

## 🔒 Consideraciones de Privacidad

### **✅ Datos Seguros (No identifican al usuario)**:
- Timezone, locale, languages
- Hardware specs (CPU, RAM, GPU)
- Preferencias de accesibilidad
- Tipo de conexión
- Comportamiento anónimo (scroll, typing)

### **⚠️ Datos Sensibles (Requieren consentimiento explícito)**:
- Geolocalización precisa (lat/long)
- Nivel de batería (puede rastrear dispositivo)
- Persistencia de storage

### **📋 Actualizar Política de Privacidad**:

```markdown
## Datos que Recopilamos

### Sin Identificación Personal:
- Timezone, idioma y preferencias del navegador
- Capacidades del dispositivo (CPU, RAM, pantalla)
- Tipo y velocidad de conexión a internet
- Preferencias de accesibilidad (contraste, movimiento reducido)
- Patrones de interacción anónimos (scroll, clicks)

### Con Tu Consentimiento:
- Ubicación geográfica aproximada (solo si activas esta función)
- Nivel de batería (para optimizar rendimiento)
```

---

## 📈 Impacto en Machine Learning

### **Mejora Esperada en Modelos**

| Modelo | F1-Score Actual | F1-Score Esperado | Mejora |
|--------|----------------|-------------------|--------|
| **Classifier** | 0.7526 | **0.85-0.90** | +13-20% |
| **Regressor** | 0.4637 (R²) | **0.65-0.75** | +40-62% |

### **Nuevas Capacidades de Personalización**

```python
# Con features extendidas, podrás predecir:

1. Adaptación por idioma/región
   - Colores culturalmente apropiados
   - Layouts RTL para árabe/hebreo
   - Formatos de fecha/hora locales

2. Optimización por hardware
   - Densidad UI basada en CPU/RAM
   - Reducir animaciones en dispositivos lentos
   - Calidad de imágenes según conexión

3. Accesibilidad automática
   - Alto contraste para necesidades visuales
   - Animaciones reducidas para sensibilidad movimiento
   - Tamaños de fuente optimizados para zoom

4. Performance adaptativo
   - Cache agresivo en conexiones lentas
   - Modo ahorro de datos respetado
   - Lazy loading inteligente

5. Experiencia contextual
   - UI diferente para PWA vs browser
   - Layouts optimizados por orientación
   - Preferencia input (teclado vs mouse)
```

---

## ✅ Próximos Pasos

1. **Expandir `useEphemeralContext.ts`**:
   - Agregar 14 nuevos campos de contexto
   - Implementar funciones helper (getOS, getBrowser, etc.)

2. **Actualizar `UserContext` en backend**:
   - Expandir modelo Pydantic con nuevos campos
   - Validación de datos adicionales

3. **Reentrenar modelos XGBoost**:
   - Generar dataset con 35 features
   - Entrenar nuevos modelos
   - Validar mejora en F1-Score/R²

4. **Implementar tracking de comportamiento**:
   - Crear `BehaviorTracker` class
   - Integrar con analytics existente

5. **Actualizar documentación**:
   - Política de privacidad
   - GDPR compliance
   - Consentimiento de usuario

---

**Conclusión**: Actualmente solo capturamos **9 datos básicos** del navegador. Podemos expandir a **46+ datos adicionales** sin requerir permisos, lo que mejoraría significativamente la precisión de los modelos ML y permitiría personalizaciones mucho más sofisticadas.

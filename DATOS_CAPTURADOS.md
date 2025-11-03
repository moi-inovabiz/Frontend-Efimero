# 📊 Análisis de Datos Capturados - Frontend Efímero

> **Fecha de análisis**: Noviembre 3, 2025  
> **Versión del sistema**: 1.0 (XGBoost Models implementados)  
> **Privacidad**: Todos los datos son **ANÓNIMOS** y orientados a mejorar la experiencia del usuario

---

## 🎯 Resumen Ejecutivo

El sistema Frontend Efímero captura **dos tipos principales de datos**:

1. **Datos de Contexto** (FASE 1) - Para predicción inicial
2. **Datos de Comportamiento** (FASE 3) - Para feedback y reentrenamiento

**Importante**: No se captura información personal identificable (PII). El sistema usa `user_temp_id` anónimos almacenados en cookies con expiración de 30 días.

---

## 📥 1. DATOS DE CONTEXTO (FASE 1 → Predicción)

### 1.1 Endpoint: `/api/v1/adaptive-ui/predict`

Estos datos se envían cuando el usuario carga la página para obtener una UI adaptada:

```json
{
  "user_context": {
    "hora_local": "2025-11-03T14:30:00.000Z",
    "prefers_color_scheme": "dark",
    "viewport_width": 1920,
    "viewport_height": 1080,
    "touch_enabled": false,
    "device_pixel_ratio": 1.0,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "referer": "https://google.com",
    "session_id": "session_1699024800000_abc123",
    "page_path": "/home"
  },
  "user_temp_id": "efimero_xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
}
```

#### Desglose de campos:

| Campo | Tipo | Propósito | Sensible |
|-------|------|-----------|----------|
| `hora_local` | DateTime | Predecir preferencias según hora del día | ❌ No |
| `prefers_color_scheme` | String | Detectar preferencia de tema (light/dark) | ❌ No |
| `viewport_width` | Integer | Adaptar diseño responsive | ❌ No |
| `viewport_height` | Integer | Optimizar espaciado vertical | ❌ No |
| `touch_enabled` | Boolean | Detectar dispositivo táctil (mobile/tablet) | ❌ No |
| `device_pixel_ratio` | Float | Optimizar recursos para pantallas retina | ❌ No |
| `user_agent` | String | Detectar navegador y SO (solo para compatibilidad) | ⚠️ Técnico |
| `referer` | String | Entender flujo de navegación | ⚠️ Bajo |
| `session_id` | String | Identificar sesión única (se regenera) | ❌ No |
| `page_path` | String | Adaptar UI según contexto de página | ❌ No |
| `user_temp_id` | String | ID anónimo temporal (cookie 30 días) | ⚠️ Anónimo |

**Almacenamiento**: 
- ✅ Solo en cache Redis (TTL: 3-15 minutos según confianza)
- ❌ NO se persiste en base de datos
- 🔄 Se usa únicamente para generar predicción ML

---

## 📤 2. DATOS DE FEEDBACK (FASE 3 → Reentrenamiento)

### 2.1 Endpoint: `/api/v1/adaptive-ui/feedback`

Estos datos se envían cuando el usuario interactúa con elementos de la UI:

```json
{
  "action_type": "click",
  "element_id": "nav-menu-button",
  "element_class": "adaptive-button-primary",
  "timestamp": "2025-11-03T14:32:15.000Z",
  "session_duration": 135000,
  "page_path": "/dashboard",
  "design_tokens_used": {
    "css_classes": ["densidad-media", "modo-nocturno", "fuente-sans"],
    "css_variables": {
      "--font-size-base": "1rem",
      "--spacing-base": "1rem",
      "--border-radius": "0.5rem"
    }
  },
  "performance_metrics": {
    "render_time_ms": 45,
    "interaction_time_ms": 12
  }
}
```

#### Desglose de campos:

| Campo | Tipo | Propósito | Sensible |
|-------|------|-----------|----------|
| `action_type` | String | Tipo de interacción (click/scroll/hover/focus) | ❌ No |
| `element_id` | String | Identificador del elemento interactuado | ❌ No |
| `element_class` | String | Clases CSS del elemento | ❌ No |
| `timestamp` | DateTime | Momento exacto de la interacción | ❌ No |
| `session_duration` | Integer | Tiempo en la sesión actual (ms) | ❌ No |
| `page_path` | String | Ruta de la página actual | ❌ No |
| `design_tokens_used` | Object | Tokens CSS que estaban activos | ❌ No |
| `performance_metrics` | Object | Métricas de rendimiento | ❌ No |

**Almacenamiento**: 
- 🔄 Actualmente: Solo logs en consola (placeholder)
- 📝 Futuro: Firestore (estructura: `behaviors/{user_temp_id}/logs/{timestamp}`)
- 🎯 Propósito: Reentrenar modelos XGBoost con comportamiento real

---

## 📊 3. DATOS DE GOOGLE ANALYTICS 4 (GA4)

### 3.1 Eventos Personalizados Enviados

El sistema envía 5 tipos de eventos GA4 para análisis agregado:

#### 3.1.1 Evento: `adaptive_ui_load`

```javascript
{
  // IDs anónimos
  user_temp_id: "efimero_abc123...",
  session_id: "session_1699024800000_xyz",
  
  // Tokens aplicados
  css_classes_applied: '["densidad-media","modo-nocturno","fuente-sans"]',
  css_variables_count: 12,
  
  // Contexto del usuario
  device_category: "desktop",
  viewport_width: 1920,
  viewport_height: 1080,
  touch_enabled: false,
  device_pixel_ratio: 1.0,
  color_scheme_preference: "dark",
  
  // Métricas de predicción ML
  prediction_confidence_classes: 0.87,
  prediction_confidence_variables: 0.82,
  processing_time_ms: 45.2,
  
  // Metadatos
  timestamp: "2025-11-03T14:30:00.000Z",
  page_url: "http://localhost:3000/dashboard",
  referrer: "https://google.com"
}
```

#### 3.1.2 Evento: `interaction_pattern`

```javascript
{
  user_temp_id: "efimero_abc123...",
  session_id: "session_1699024800000_xyz",
  
  // Interacción
  element_type: "button",
  interaction_action: "click",
  element_classes: "adaptive-button-primary",
  element_position: "header",
  
  // Timing
  time_on_page: 135,
  scroll_depth: 0.35,
  
  // Estado UI actual
  current_ui_density: "media",
  current_color_scheme: "dark",
  
  timestamp: "2025-11-03T14:32:15.000Z"
}
```

#### 3.1.3 Evento: `viewport_change`

```javascript
{
  user_temp_id: "efimero_abc123...",
  session_id: "session_1699024800000_xyz",
  
  // Cambio de viewport
  old_viewport_width: 1920,
  old_viewport_height: 1080,
  new_viewport_width: 768,
  new_viewport_height: 1024,
  
  // Categorización
  old_device_category: "desktop",
  new_device_category: "tablet",
  device_category_changed: true,
  
  timestamp: "2025-11-03T14:35:00.000Z"
}
```

#### 3.1.4 Evento: `model_prediction`

```javascript
{
  user_temp_id: "efimero_abc123...",
  session_id: "session_1699024800000_xyz",
  
  // Input del modelo
  feature_count: 21,
  feature_temporal_hour: 0.866, // hour_sin
  feature_device_touch: 0,
  feature_viewport_aspect: 1.78,
  
  // Output del modelo
  predicted_classes_count: 3,
  predicted_variables_count: 12,
  
  // Métricas
  model_version: "v1.0.0",
  prediction_confidence: 0.85,
  processing_time_ms: 45.2,
  
  timestamp: "2025-11-03T14:30:00.000Z"
}
```

#### 3.1.5 Evento: `session_summary`

```javascript
{
  user_temp_id: "efimero_abc123...",
  session_id: "session_1699024800000_xyz",
  
  // Métricas de sesión
  session_duration_seconds: 420,
  total_interactions: 15,
  pages_viewed: 5,
  max_scroll_depth: 0.85,
  
  // Contexto promedio
  avg_viewport_width: 1920,
  device_changes: 0,
  ui_adaptations_count: 3,
  
  timestamp: "2025-11-03T14:37:00.000Z"
}
```

**Privacidad GA4**:
```javascript
{
  anonymize_ip: true,                        // IPs anonimizadas
  allow_google_signals: false,               // Sin señales cruzadas
  allow_ad_personalization_signals: false    // Sin personalización de ads
}
```

---

## 🔒 4. Política de Privacidad y Seguridad

### 4.1 Principios de Privacidad

✅ **Cumplidos**:
- ✅ No se captura información personal identificable (PII)
- ✅ IDs anónimos temporales con expiración de 30 días
- ✅ IPs anonimizadas en GA4
- ✅ Sin tracking entre dominios
- ✅ Sin personalización de ads
- ✅ Datos de comportamiento solo para ML interno

⚠️ **En desarrollo**:
- ⏳ Banner de consentimiento de cookies (GDPR/CCPA)
- ⏳ Opción de opt-out de analytics
- ⏳ Panel de preferencias de privacidad del usuario

### 4.2 Almacenamiento de Datos

| Tipo de Dato | Ubicación | Persistencia | Encriptación |
|--------------|-----------|--------------|--------------|
| Contexto de Usuario | Redis Cache | 3-15 min | En tránsito (TLS) |
| Feedback de Comportamiento | Firestore (futuro) | Indefinido | At rest + in transit |
| Analytics GA4 | Google Analytics | 14 meses | Google managed |
| Cookies `user_temp_id` | Navegador | 30 días | HttpOnly, SameSite=Lax |
| Session Storage | Navegador | Sesión actual | No (local) |

### 4.3 Acceso a Datos

| Quién | Qué puede acceder | Propósito |
|-------|-------------------|-----------|
| Backend API | Contexto + Feedback | Predicción ML |
| Redis Cache | Solo contexto temporal | Performance |
| Firebase (futuro) | Logs de comportamiento | Reentrenamiento |
| Google Analytics | Eventos agregados | Análisis de producto |
| Desarrolladores | Logs anonimizados | Debugging |
| Usuario final | Sus propios datos (GDPR) | Transparencia |

---

## 📈 5. Uso de Datos para Machine Learning

### 5.1 Pipeline de Entrenamiento

```
1. CAPTURA (FASE 3)
   ├─ Feedback de comportamiento
   ├─ Contexto de interacción
   └─ Tokens aplicados

2. ALMACENAMIENTO
   ├─ Firestore: behaviors/{user_temp_id}/logs/{timestamp}
   └─ Agregación periódica (daily)

3. PREPROCESAMIENTO
   ├─ Feature engineering (21 features)
   ├─ Normalización (StandardScaler por grupos)
   └─ Balance de clases (oversampling si es necesario)

4. REENTRENAMIENTO
   ├─ XGBoost Classifier (CSS classes)
   ├─ XGBoost Regressor (CSS variables)
   └─ Validación cruzada (GridSearchCV)

5. DESPLIEGUE
   ├─ Actualización de modelos en backend/models/
   └─ Rollback automático si métricas bajan
```

### 5.2 Features Generadas (21 features)

| Feature | Fuente | Tipo |
|---------|--------|------|
| `hour_sin`, `hour_cos` | `hora_local` | Temporal |
| `day_of_week` | `hora_local` | Temporal |
| `viewport_width` | Directo | Dispositivo |
| `viewport_height` | Directo | Dispositivo |
| `touch_enabled` | Directo | Dispositivo |
| `device_pixel_ratio` | Directo | Dispositivo |
| `viewport_aspect_ratio` | Calculado | Compuesta |
| `viewport_area` | Calculado | Compuesta |
| `prefers_dark_mode` | `prefers_color_scheme` | Preferencia |
| `is_mobile` | Calculado | Dispositivo |
| `is_tablet` | Calculado | Dispositivo |
| `is_desktop` | Calculado | Dispositivo |
| `has_referer` | `referer` | Navegación |
| `session_duration_normalized` | `session_duration` | Temporal |
| `interactions_per_minute` | Calculado | Comportamiento |
| `scroll_depth` | Frontend tracking | Comportamiento |
| `dark_mode_social_context` | Agregación | Social |
| `high_density_social_context` | Agregación | Social |
| `serif_preference_social_context` | Agregación | Social |
| `device_category_popularity` | Agregación | Social |
| `time_slot_popularity` | Agregación | Social |

---

## 🛡️ 6. Recomendaciones de Seguridad

### 6.1 Implementaciones Pendientes

1. **Consentimiento de Usuario**
   ```typescript
   // TODO: Implementar banner de cookies
   interface CookieConsent {
     analytics: boolean;
     performance: boolean;
     functional: boolean;
   }
   ```

2. **Data Retention Policy**
   ```yaml
   # TODO: Configurar en Firestore
   retention_rules:
     behavior_logs: 6 months
     analytics_events: 14 months (GA4 default)
     cached_predictions: 15 minutes max
   ```

3. **User Data Export (GDPR)**
   ```typescript
   // TODO: Endpoint para exportar datos del usuario
   GET /api/v1/users/{user_temp_id}/data-export
   ```

4. **Right to be Forgotten**
   ```typescript
   // TODO: Endpoint para eliminar datos
   DELETE /api/v1/users/{user_temp_id}/data
   ```

### 6.2 Configuración de Seguridad Actual

```python
# backend/app/config/settings.py
SECURITY_SETTINGS = {
    "cors": {
        "allow_origins": ["http://localhost:3000"],
        "allow_credentials": True
    },
    "rate_limiting": {
        "predict": "100/hour",
        "feedback": "1000/hour"
    },
    "cache": {
        "max_ttl": 900,  # 15 minutos
        "max_memory_mb": 100
    }
}
```

---

## 📞 7. Contacto y Transparencia

Para consultas sobre datos capturados o privacidad:

- **Email**: privacy@frontend-efimero.com (TODO: configurar)
- **Documentación**: https://docs.frontend-efimero.com/privacy
- **GitHub**: https://github.com/moi-inovabiz/Frontend-Efimero

### 7.1 Registro de Cambios en Captura de Datos

| Fecha | Cambio | Impacto |
|-------|--------|---------|
| 2025-11-03 | Implementación inicial XGBoost | Sistema base de captura |
| TBD | Banner de consentimiento | Opt-in obligatorio |
| TBD | Data export endpoint | Cumplimiento GDPR |

---

## ✅ Conclusión

El sistema Frontend Efímero captura **únicamente datos técnicos y de comportamiento anónimos** necesarios para proporcionar una experiencia de usuario adaptativa mediante Machine Learning.

**Datos NO capturados**:
- ❌ Nombres, emails, teléfonos
- ❌ Direcciones IP sin anonimizar
- ❌ Contenido de formularios
- ❌ Contraseñas o datos sensibles
- ❌ Información financiera
- ❌ Geolocalización precisa
- ❌ Archivos subidos por usuarios

**Datos SÍ capturados (anónimos)**:
- ✅ Configuración de dispositivo (viewport, touch, pixel ratio)
- ✅ Preferencias de tema (light/dark)
- ✅ Hora local (para predicciones temporales)
- ✅ Interacciones con UI (clicks, hovers, scroll)
- ✅ Performance metrics (render time, interaction time)
- ✅ Tokens CSS aplicados (para feedback loop)

**Propósito**: Mejorar la experiencia de usuario mediante UI adaptativa inteligente.

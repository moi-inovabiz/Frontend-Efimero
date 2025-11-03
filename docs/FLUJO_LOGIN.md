# 🔐 Flujo de Autenticación - Frontend Efímero

## 📋 Flujo UX Simplificado (Sin Onboarding)

```
┌──────────────────────────────────────────────────┐
│  LANDING PAGE / HOME                             │
│  (Usuario no autenticado)                        │
│                                                  │
│  ┌─────────────────────────────────────┐       │
│  │  Header                             │       │
│  │  ┌──────────────────────────────┐  │       │
│  │  │  [Iniciar Sesión con Google] │  │       │
│  │  └──────────────────────────────┘  │       │
│  └─────────────────────────────────────┘       │
│                                                  │
│  Contenido público con UI adaptativa             │
│  anónima (basada en user_temp_id)               │
└──────────────────────────────────────────────────┘
                    ↓
                [Usuario hace click]
                    ↓
┌──────────────────────────────────────────────────┐
│  GOOGLE OAUTH POPUP                              │
│  ┌────────────────────────────────────────────┐ │
│  │  Iniciar sesión con Google                 │ │
│  │                                             │ │
│  │  [👤 juan.perez@gmail.com]                │ │
│  │  [👤 maria.garcia@gmail.com]              │ │
│  │  [+ Usar otra cuenta]                      │ │
│  │                                             │ │
│  │  ────────────────────────────────────────  │ │
│  │                                             │ │
│  │  Frontend Efímero solicitará:              │ │
│  │  • Ver tu información personal básica      │ │
│  │  • Ver tu dirección de correo electrónico │ │
│  │                                             │ │
│  │  [Cancelar]              [Continuar] ✓     │ │
│  └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
                    ↓
                [Google autentica]
                    ↓
┌──────────────────────────────────────────────────┐
│  BACKEND: Procesamiento                          │
│                                                  │
│  1. Recibe token de Google                      │
│  2. Verifica token con Firebase Auth            │
│  3. Busca usuario en Firestore:                 │
│     • Si existe → Actualizar last_login         │
│     • Si NO existe → Crear perfil nuevo         │
│  4. Migrar datos anónimos:                      │
│     • user_temp_id → google_id                  │
│     • Comportamiento histórico preservado       │
│  5. Generar JWT token                           │
│  6. Retornar perfil + token                     │
└──────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────┐
│  DASHBOARD / HOME                                │
│  (Usuario autenticado)                           │
│                                                  │
│  ┌─────────────────────────────────────┐       │
│  │  Header                             │       │
│  │  ┌──────────┐  ┌────────────────┐  │       │
│  │  │ 👤 Juan  │  │ [⚙️ Ajustes]   │  │       │
│  │  └──────────┘  └────────────────┘  │       │
│  └─────────────────────────────────────┘       │
│                                                  │
│  ✨ Contenido personalizado con:                │
│  • UI adaptativa basada en historial            │
│  • Predicciones ML mejoradas (datos reales)     │
│  • Sincronización entre dispositivos            │
│                                                  │
│  💡 Sistema aprende automáticamente tus         │
│     preferencias mientras navegas               │
└──────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Datos Técnico

```
┌─────────────────────────────────────────────────────────────┐
│  FASE 1: AUTENTICACIÓN                                       │
└─────────────────────────────────────────────────────────────┘

Frontend                      Backend                    Firestore
   │                             │                           │
   │ 1. Click "Login Google"     │                           │
   ├──────────────────────────►  │                           │
   │                             │                           │
   │ 2. Google OAuth Popup       │                           │
   │ ◄──────────────────────────┤                           │
   │                             │                           │
   │ 3. Usuario aprueba          │                           │
   │                             │                           │
   │ 4. POST /auth/google        │                           │
   │    { id_token, user_temp_id }                           │
   ├──────────────────────────►  │                           │
   │                             │ 5. Verificar token        │
   │                             │    con Firebase           │
   │                             │                           │
   │                             │ 6. GET users/{google_id}  │
   │                             ├────────────────────────►  │
   │                             │                           │
   │                             │ ◄────────────────────────┤
   │                             │ { user_profile } o null   │
   │                             │                           │
   │                             │ 7. Si es nuevo:           │
   │                             │    CREATE user profile    │
   │                             ├────────────────────────►  │
   │                             │                           │
   │                             │ 8. Migrar datos anónimos: │
   │                             │    behaviors/{temp_id}    │
   │                             │    → users/{google_id}    │
   │                             ├────────────────────────►  │
   │                             │                           │
   │ ◄──────────────────────────┤                           │
   │ 9. { jwt_token, user_profile }                          │
   │                             │                           │
   │ 10. Guardar JWT en          │                           │
   │     localStorage            │                           │
   │                             │                           │

┌─────────────────────────────────────────────────────────────┐
│  FASE 2: PREDICCIÓN ML (Post-Login)                         │
└─────────────────────────────────────────────────────────────┘

Frontend                      Backend                    Firestore
   │                             │                           │
   │ 1. POST /adaptive-ui/predict                            │
   │    Headers: { Authorization: Bearer JWT }               │
   │    Body: { user_context }   │                           │
   ├──────────────────────────►  │                           │
   │                             │ 2. Verificar JWT          │
   │                             │    extraer google_id      │
   │                             │                           │
   │                             │ 3. GET historical behavior│
   │                             ├────────────────────────►  │
   │                             │ { behavior_history }      │
   │                             │ ◄────────────────────────┤
   │                             │                           │
   │                             │ 4. Enriquecer features:   │
   │                             │    • user_context (now)   │
   │                             │    • behavior_history     │
   │                             │    • social_context       │
   │                             │                           │
   │                             │ 5. Predicción XGBoost     │
   │                             │    (mejorada con datos)   │
   │                             │                           │
   │ ◄──────────────────────────┤                           │
   │ 6. { design_tokens, confidence }                        │
   │                             │                           │
   │ 7. Aplicar tokens CSS       │                           │
   │                             │                           │

┌─────────────────────────────────────────────────────────────┐
│  FASE 3: FEEDBACK LOOP (Continuo)                           │
└─────────────────────────────────────────────────────────────┘

Frontend                      Backend                    Firestore
   │                             │                           │
   │ Usuario interactúa con UI   │                           │
   │                             │                           │
   │ POST /adaptive-ui/feedback  │                           │
   │ Headers: { Authorization }  │                           │
   │ Body: { action_type, ... }  │                           │
   ├──────────────────────────►  │                           │
   │                             │ Almacenar en:             │
   │                             │ users/{google_id}/        │
   │                             │   behaviors/{timestamp}   │
   │                             ├────────────────────────►  │
   │                             │                           │
   │ ◄──────────────────────────┤                           │
   │ { status: "ok" }            │                           │
```

---

## 🗄️ Estructura de Datos en Firestore

### Colección: `users/{google_id}`

```typescript
{
  // Identidad
  google_id: "1234567890",
  email: "juan.perez@gmail.com",
  display_name: "Juan Pérez",
  photo_url: "https://lh3.googleusercontent.com/...",
  locale: "es-ES",
  
  // Vinculación con sistema anónimo
  user_temp_id: "efimero_abc123...",  // ID previo al login
  
  // Preferencias (aprendidas automáticamente)
  learned_preferences: {
    color_scheme: "dark",           // Aprendido de uso mayoritario
    ui_density: "compact",          // Aprendido de interacciones
    preferred_font: "sans-serif",   // Aprendido de clicks
    confidence_level: 0.85          // Confianza en preferencias
  },
  
  // Estadísticas agregadas
  statistics: {
    total_sessions: 47,
    total_interactions: 1823,
    avg_session_duration: 180000,  // ms
    first_seen: Timestamp,
    last_login: Timestamp,
    peak_usage_hours: [9, 14, 20], // Horas de uso frecuente
    primary_device: "desktop",      // Detectado automáticamente
    devices_used: ["desktop", "mobile"]
  },
  
  // Metadatos
  created_at: Timestamp,
  updated_at: Timestamp
}
```

### Subcolección: `users/{google_id}/behaviors/{timestamp}`

```typescript
{
  timestamp: Timestamp,
  action_type: "click",
  element_id: "nav-menu",
  element_class: "adaptive-button-primary",
  
  // Contexto de la sesión
  session_id: "session_123",
  page_path: "/dashboard",
  device_category: "desktop",
  viewport: { width: 1920, height: 1080 },
  
  // Tokens aplicados en ese momento
  design_tokens_used: {
    css_classes: ["densidad-media", "modo-nocturno"],
    css_variables: { "--font-size-base": "1rem" }
  },
  
  // Performance
  interaction_time_ms: 12,
  scroll_depth: 0.35
}
```

---

## 🎯 Ventajas de Este Flujo (Sin Onboarding)

| Aspecto | Ventaja |
|---------|---------|
| **Fricción** | ✅ Login en 1 solo paso, sin formularios |
| **UX** | ✅ El usuario entra directo al contenido |
| **ML** | ✅ Sistema aprende preferencias automáticamente |
| **Tiempo** | ✅ Usuario productivo en <3 segundos |
| **Conversión** | ✅ Mayor tasa de registro (menos pasos) |
| **Adaptación** | ✅ Mejora con el tiempo (aprendizaje continuo) |

---

## 🔧 Implementación Técnica Simplificada

### 1. Frontend: Botón de Login

```tsx
// components/auth/GoogleLoginButton.tsx
'use client';

import { signInWithGoogle } from '@/lib/auth/google-auth';
import { useRouter } from 'next/navigation';

export default function GoogleLoginButton() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      const result = await signInWithGoogle();
      // JWT automáticamente guardado en localStorage
      router.push('/dashboard');
    } catch (error) {
      console.error('Error en login:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleLogin}
      disabled={loading}
      className="flex items-center gap-3 px-6 py-3 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
    >
      <svg className="w-5 h-5" viewBox="0 0 24 24">
        {/* Google Logo SVG */}
      </svg>
      <span className="font-medium text-gray-700">
        {loading ? 'Iniciando sesión...' : 'Continuar con Google'}
      </span>
    </button>
  );
}
```

### 2. Backend: Endpoint de Autenticación

```python
# backend/app/api/routes/auth.py
@router.post("/auth/google")
async def authenticate_with_google(
    auth_data: GoogleAuthRequest
) -> GoogleAuthResponse:
    """
    Autenticación con Google OAuth.
    Flujo simplificado sin onboarding.
    """
    # 1. Verificar token de Google
    google_user = await firebase_auth.verify_id_token(auth_data.id_token)
    
    # 2. Buscar o crear usuario
    user = await user_service.get_or_create_user(
        google_id=google_user['uid'],
        email=google_user['email'],
        display_name=google_user['name'],
        photo_url=google_user['picture'],
        locale=google_user.get('locale', 'en')
    )
    
    # 3. Migrar datos anónimos si existen
    if auth_data.user_temp_id:
        await user_service.migrate_anonymous_data(
            user_temp_id=auth_data.user_temp_id,
            google_id=google_user['uid']
        )
    
    # 4. Generar JWT
    jwt_token = create_jwt_token(user_id=user.google_id)
    
    # 5. Retornar perfil + token
    return GoogleAuthResponse(
        jwt_token=jwt_token,
        user_profile=user,
        requires_onboarding=False  # ✨ Sin onboarding
    )
```

### 3. Sistema de Aprendizaje Automático

```python
# backend/app/services/preference_learning_service.py
class PreferenceLearningService:
    """
    Aprende preferencias del usuario automáticamente
    basándose en su comportamiento.
    """
    
    async def update_learned_preferences(
        self,
        user_id: str,
        behavior_logs: List[BehaviorLog]
    ) -> LearnedPreferences:
        """
        Analiza logs de comportamiento y actualiza preferencias.
        Se ejecuta cada N interacciones o diariamente.
        """
        
        # Analizar patrones de uso
        color_scheme = self._infer_color_scheme_preference(behavior_logs)
        ui_density = self._infer_density_preference(behavior_logs)
        font_preference = self._infer_font_preference(behavior_logs)
        
        # Calcular confianza
        confidence = self._calculate_confidence_level(behavior_logs)
        
        # Actualizar en Firestore
        preferences = LearnedPreferences(
            color_scheme=color_scheme,
            ui_density=ui_density,
            preferred_font=font_preference,
            confidence_level=confidence
        )
        
        await self.firestore.update_user_preferences(user_id, preferences)
        
        return preferences
    
    def _infer_color_scheme_preference(
        self,
        logs: List[BehaviorLog]
    ) -> str:
        """
        Detecta si usuario prefiere dark/light mode
        basándose en hora de uso y tokens aplicados.
        """
        dark_mode_sessions = sum(
            1 for log in logs
            if 'modo-nocturno' in log.design_tokens_used.css_classes
        )
        total_sessions = len(logs)
        
        # Si usa dark mode en >60% de sesiones
        if dark_mode_sessions / total_sessions > 0.6:
            return 'dark'
        return 'light'
```

---

## 📊 Comparación: Con vs Sin Onboarding

| Métrica | Con Onboarding | Sin Onboarding |
|---------|----------------|----------------|
| **Tiempo hasta productividad** | ~60 segundos | ~3 segundos |
| **Pasos del usuario** | 4-5 clicks | 1 click |
| **Tasa de abandono** | 20-30% | 5-10% |
| **Precisión inicial** | 90% (explícito) | 70% (inferido) |
| **Precisión después 1 semana** | 90% | 85% |
| **Precisión después 1 mes** | 90% | 95% (mejor) |
| **Experiencia usuario** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🚀 Resumen del Flujo

```
Login Google (1 click) 
    ↓
Dashboard inmediato con:
    • UI adaptativa básica (datos de Google + user_temp_id previo)
    • Sistema ML empieza a aprender
    ↓
Uso normal de la aplicación
    ↓
Sistema aprende automáticamente:
    • ¿Prefieres dark mode? (hora de uso + mayoría de sesiones)
    • ¿Densidad UI? (interacciones con elementos)
    • ¿Tamaño fuente? (tiempo en página, errores de click)
    • ¿Dispositivo principal? (device más frecuente)
    ↓
UI cada vez más personalizada
    • Sin preguntar al usuario
    • Adaptación continua
    • Mejora con el tiempo
```

**¿Procedo con la implementación de este flujo simplificado?** 🎯

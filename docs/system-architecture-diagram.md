# 🏗️ Diagrama Arquitectura Completa - Frontend Efímero con GA4

## 📊 Flujo Completo del Sistema

```mermaid
graph TB
    %% USER LAYER
    subgraph "👤 USUARIO"
        U[Usuario navegando]
        B[Comportamiento real]
        I[Interacciones]
    end

    %% FRONTEND LAYER
    subgraph "🌐 FRONTEND (Next.js 16.0)"
        UI[Interfaz Adaptativa]
        GA4T[GA4 Tracker]
        UUID[UUID Anónimo]
        CSS[CSS Dinámico aplicado]
    end

    %% ANALYTICS LAYER
    subgraph "📈 GOOGLE ANALYTICS 4"
        GA4P[GA4 Property]
        BE[BigQuery Export]
        CE[Custom Events]
    end

    %% BACKEND LAYER
    subgraph "🚀 BACKEND (FastAPI)"
        API["/predict endpoint"]
        AUS[AdaptiveUIService]
        MM[ModelManager]
        
        subgraph "🧠 ML PIPELINE"
            FP[FeatureProcessor]
            FS[FeatureScaler]
            CLS[XGBoost Classifier]
            REG[XGBoost Regressor]
        end
    end

    %% DATA LAYER
    subgraph "💾 DATOS"
        SYNT[Datos Sintéticos 5000]
        REAL[Datos Reales GA4]
        Models[Modelos Entrenados]
    end

    %% TRAINING PIPELINE
    subgraph "🔄 ENTRENAMIENTO OFFLINE"
        EXT[GA4DataExtractor]
        TRAIN[Training Pipeline]
        VALID[Validación]
        DEPLOY[Deploy Modelos]
    end

    %% FLUJO PRINCIPAL
    U --> UI
    UI --> API
    API --> AUS
    AUS --> FP
    FP --> FS
    FS --> CLS
    FS --> REG
    CLS --> MM
    REG --> MM
    MM --> AUS
    AUS --> API
    API --> UI
    UI --> CSS
    CSS --> U

    %% FLUJO ANALYTICS
    B --> GA4T
    I --> GA4T
    GA4T --> UUID
    UUID --> CE
    CE --> GA4P
    GA4P --> BE
    BE --> REAL

    %% FLUJO ENTRENAMIENTO
    REAL --> EXT
    SYNT --> TRAIN
    EXT --> TRAIN
    TRAIN --> VALID
    VALID --> Models
    Models --> DEPLOY
    DEPLOY --> MM

    %% ESTILOS
    classDef userLayer fill:#e1f5fe
    classDef frontendLayer fill:#f3e5f5
    classDef analyticsLayer fill:#e8f5e8
    classDef backendLayer fill:#fff3e0
    classDef dataLayer fill:#fce4ec
    classDef trainingLayer fill:#f1f8e9

    class U,B,I userLayer
    class UI,GA4T,UUID,CSS frontendLayer
    class GA4P,BE,CE analyticsLayer
    class API,AUS,MM,FP,FS,CLS,REG backendLayer
    class SYNT,REAL,Models dataLayer
    class EXT,TRAIN,VALID,DEPLOY trainingLayer
```

## 🔄 Flujo Detallado por Fases

### **FASE 1: Predicción en Tiempo Real (< 100ms)**

```mermaid
sequenceDiagram
    participant User as 👤 Usuario
    participant UI as 🌐 Frontend
    participant API as 🚀 FastAPI
    participant ML as 🧠 ML Pipeline
    participant GA4 as 📊 GA4

    User->>UI: Visita página
    UI->>API: POST /predict (UserContext)
    
    Note over API: 1. AdaptiveUIService
    API->>ML: FeatureProcessor.prepare_features()
    ML->>ML: 20 features extraídas
    
    Note over ML: 2. Feature Scaling
    ML->>ML: FeatureScaler.transform()
    ML->>ML: Features normalizadas por grupo
    
    Note over ML: 3. Doble Predicción
    ML->>ML: XGBoost Classifier → CSS classes
    ML->>ML: XGBoost Regressor → CSS variables
    
    ML->>API: DesignTokens + Confidence
    API->>UI: AdaptiveUIResponse
    
    Note over UI: 4. Aplicación CSS
    UI->>UI: Inyecta CSS antes render
    UI->>User: Interfaz adaptada
    
    Note over GA4: 5. Analytics Tracking
    UI->>GA4: trackAdaptiveUILoad()
    UI->>GA4: trackModelPrediction()
```

### **FASE 2: Recolección de Datos Reales**

```mermaid
flowchart LR
    subgraph "🌐 Frontend Analytics"
        A1[Usuario interactúa]
        A2[AdaptiveUIAnalytics]
        A3[Custom Events]
    end
    
    subgraph "📊 GA4 Events"
        B1[adaptive_ui_load]
        B2[interaction_pattern]
        B3[model_prediction]
        B4[viewport_change]
    end
    
    subgraph "💾 BigQuery"
        C1[Raw Events]
        C2[Processed Data]
        C3[ML Training Data]
    end
    
    A1 --> A2
    A2 --> A3
    A3 --> B1
    A3 --> B2
    A3 --> B3
    A3 --> B4
    
    B1 --> C1
    B2 --> C1
    B3 --> C1
    B4 --> C1
    
    C1 --> C2
    C2 --> C3
```

### **FASE 3: Entrenamiento Offline**

```mermaid
graph LR
    subgraph "📊 Fuentes de Datos"
        S[Datos Sintéticos<br/>5000 samples]
        R[Datos Reales GA4<br/>BigQuery]
    end
    
    subgraph "🔄 Pipeline ML"
        E[GA4DataExtractor]
        P[FeatureProcessor]
        C[Combine Datasets]
        T[XGBoost Training]
    end
    
    subgraph "🎯 Modelos"
        M1[Classifier.joblib]
        M2[Regressor.joblib]
        M3[FeatureScaler.joblib]
    end
    
    S --> C
    R --> E
    E --> P
    P --> C
    C --> T
    T --> M1
    T --> M2
    T --> M3
```

## 🧠 Arquitectura ML Detallada

### **Feature Engineering Pipeline**

```
📥 UserContext Input
├── 🕒 Temporal Features (4)
│   ├── hour_sin/cos → StandardScaler
│   └── day_sin/cos → StandardScaler
├── 📱 Device Features (5)
│   ├── touch_enabled → MinMaxScaler
│   ├── pixel_ratio → MinMaxScaler
│   ├── viewport_aspect → MinMaxScaler
│   ├── screen_area → MinMaxScaler
│   └── color_scheme → MinMaxScaler
├── 📊 Historical Features (5)
│   ├── session_count → RobustScaler
│   ├── avg_duration → RobustScaler
│   ├── interactions_count → RobustScaler
│   ├── page_diversity → RobustScaler
│   └── recent_activity → RobustScaler
├── 👥 Social Features (3)
│   ├── dark_mode_percentage → MinMaxScaler
│   ├── high_density_percentage → MinMaxScaler
│   └── serif_preference → MinMaxScaler
└── 🔗 Composite Features (3)
    ├── touch_vs_mouse_ratio → RobustScaler
    ├── auth_multiplier → RobustScaler
    └── mobile_correlation → RobustScaler

📤 Output: 20 features normalizadas
```

### **Dual XGBoost Architecture**

```
📊 Scaled Features (20)
├── 🎨 XGBoost Classifier
│   ├── Output: CSS Classes
│   │   ├── densidad-alta/media/baja
│   │   ├── fuente-serif/sans/mono
│   │   └── modo-nocturno/claro
│   └── Confidence: 0.0-1.0
└── 📏 XGBoost Regressor
    ├── Output: CSS Variables
    │   ├── --font-size-base: "1.067rem"
    │   ├── --spacing-unit: "0.82rem"
    │   └── --border-radius: "4px"
    └── Confidence: R² score
```

## 📊 GA4 Events Schema

### **adaptive_ui_load Event**
```json
{
  "event_name": "adaptive_ui_load",
  "user_temp_id": "uuid-anon-123",
  "css_classes_applied": ["densidad-alta", "fuente-serif"],
  "css_variables_applied": {
    "--font-size-base": "1.067rem",
    "--spacing-unit": "0.82rem"
  },
  "prediction_confidence": 0.89,
  "device_context": {
    "viewport_width": 1366,
    "viewport_height": 768,
    "pixel_ratio": 1.0,
    "touch_enabled": false
  },
  "processing_time_ms": 87
}
```

### **interaction_pattern Event**
```json
{
  "event_name": "interaction_pattern",
  "user_temp_id": "uuid-anon-123",
  "element_type": "button",
  "interaction_action": "click",
  "timing_ms": 1234,
  "success": true,
  "context_metadata": {
    "page_section": "hero",
    "adaptive_classes": ["densidad-alta"]
  }
}
```

## 🔄 Estados del Sistema

### **Estado Actual (Task 1.4 Completado)**
- ✅ Feature Engineering Pipeline completo
- ✅ GA4 Integration arquitectura implementada
- ✅ Frontend Next.js ejecutándose
- ✅ Datos sintéticos 5000 muestras validadas
- ⚠️ Modelos XGBoost usando mocks (Task 2.1-2.5 pendientes)

### **Próximos Pasos**
1. **Configurar GA4 Property real** → Obtener measurement_id
2. **Implementar modelos XGBoost reales** → Tasks 2.1-2.5  
3. **Setup entrenamiento offline** → Pipeline automático
4. **Validación end-to-end** → Testing completo

## 🎯 Métricas de Performance

- **Inferencia ML**: < 100ms (objetivo)
- **Feature Processing**: ~20ms actual
- **Predicción dual**: ~50ms estimado
- **CSS Injection**: < 10ms
- **Zero Flicker**: CSS antes de render
- **Privacy**: UUID anónimos, no PII

## 🔐 Privacidad y Seguridad

- **Anonimización**: UUID temporal, no tracking cross-site
- **GA4 Config**: IP anonymization, no Google Signals
- **Datos**: Solo comportamiento UI, no contenido personal
- **GDPR Compliance**: Datos agregados, opt-out disponible

# Project Context

## Purpose
Sistema de Adaptación Predictiva Profunda de Interfaz de Usuario (UI) - "Frontend Efímero": Resolución del dilema de personalización mediante un Backend Inteligente que toma decisiones de diseño con alta precisión antes del renderizado.

**Concepto de Frontend Efímero**: UI que se construye dinámicamente en el servidor utilizando una prescripción única de diseño generada por XGBoost para un usuario y contexto específicos. El diseño no es fijo - los parámetros de espaciado, tipografía y color cambian dinámicamente con cada solicitud.

**Adaptación Profunda**: Personalización granular usando modelos de Regresión para predecir valores continuos (Tokens de Diseño), permitiendo ajustes como `font-size: 1.15rem` o `spacing-factor: 0.82`.

**Ventaja Competitiva**: Zero Flicker - eliminación del parpadeo visual inyectando decisiones de diseño directamente en el HTML durante Server-Side Rendering (SSR).

## Tech Stack

### Frontend / Capa de Presentación (SSR)
- **React** (o Next.js) - Desarrollo de componentes UI y Server-Side Rendering
- **Tailwind CSS** - Framework utility-first para consumo directo de clases y variables inyectadas por backend
- **JavaScript/Custom Hooks** - Captura de datos efímeros del navegador (hora local, preferencias SO, capacidad táctil)

### Backend / Capa de Lógica e Inferencia
- **FastAPI (Python)** - Servidor API ultrarrápido, orquestador de las fases de procesamiento
- **XGBoost** - Motor de IA principal (Classifier y Regressor) para predicciones de estilo y valores de tokens de diseño
- **Scikit-learn** - Preprocesamiento de datos (escalado, normalización) para inferencia
- **Pandas/NumPy** - Manipulación y preparación de datos tabulares de logs de comportamiento
- **Firestore (Firebase)** - Base de datos NoSQL para logs de comportamiento histórico y datos de entorno social
- **Joblib/Pickle** - Serialización y carga de modelos XGBoost entrenados en memoria para inferencia instantánea

## Project Conventions

### Code Style
- **Separación de Responsabilidades**: Endpoints FastAPI delgados, lógica de BD e IA en servicios Python separados
- **Inferencia en Memoria**: Modelos XGBoost cargados al inicio (FastAPI startup hook) usando Joblib para eliminar latencia de disco
- **Identificación Segura**: JWT para usuarios autenticados, Cookies de Primera Parte para anónimos recurrentes

### Architecture Patterns
- **Arquitectura de 3 Fases Obligatorias**:
  - **Fase 1**: Inicialización y Recolección - Captura JS de contexto + envío a FastAPI
  - **Fase 2**: Decisión Inteligente (FastAPI + XGBoost) - Momento crítico de inferencia
  - **Fase 3**: Renderizado Efímero y Feedback - Inyección tokens + bucle feedback
- **Doble Predicción Obligatoria**: XGBoost Classifier (clases CSS) + XGBoost Regressor (variables CSS)
- **Tokens de Diseño Generados por IA**:
  - Clases: `<html class="densidad-alta fuente-serif modo-nocturno">`
  - Variables: `:root { --font-size-base: 1.15rem; }`

### Flujo Operacional (3 Fases)
1. **FASE 1**: Cliente → Captura JS (hora local, preferencias SO) → Envío bloqueante a FastAPI
2. **FASE 2**: FastAPI → Consulta Firestore → Preprocesamiento Scikit-learn → Inferencia XGBoost dual → JSON respuesta
3. **FASE 3**: SSR → Inyección tokens → Renderizado React → Entrega Zero Flicker → Bucle feedback

### Frontend Efímero (Diseño)
- **Consumo de Variables CSS**: Componentes React consumen variables CSS generadas por regresión IA
  ```jsx
  style={{fontSize: 'var(--font-size-base)'}}
  ```
- **Clases Condicionales**: Clases predichas por IA como prefijos Tailwind
  ```jsx
  className="densidad-alta:p-4"
  ```
- **Inyección en Esqueleto**: Variables CSS en `<style>` global, clases predichas en `<html>`/`<body>` antes de hidratación React

### Testing Strategy
- **Métricas de Modelo Mandatorias**:
  - Clasificación: F1-Score (equilibrio precisión/recall)
  - Regresión: RMSE (Root Mean Squared Error) para error mínimo en tokens
- **Features Compuestas**: Datos comportamiento/contexto cruzados (ej. `TasaDeError_tactil_vs_mouse`)
- **Transparencia de Datos**: Procesador Scikit-learn estandarizado para features limpias y escaladas
- **Monitoreo Continuo**: Medición de rendimiento del modelo en producción

### Git Workflow
[Pendiente de definir - agregar estrategia de branching y convenciones de commit]

## Domain Context
- **Frontend Efímero**: UI construida dinámicamente por solicitud, no estática
- **Adaptación Profunda**: Personalización granular con valores continuos (no solo binario)
- **Machine Learning**: Sistema dual XGBoost (Classifier + Regressor) para decisiones de diseño
- **Zero Flicker**: Aplicación de cambios antes de renderización inicial (crítico)
- **Perfilado Instantáneo**: Funciona para usuarios anónimos y autenticados sin tracking terceros
- **Contexto Multifuente**: JS (hora local, SO), HTTP headers, Firestore logs, entorno social

## Important Constraints
- **Latencia Crítica**: Inferencia debe ser instantánea (modelos XGBoost en memoria RAM)
- **Zero Flicker**: Cambios UI deben aplicarse antes de renderización inicial (absoluto)
- **Separación ML**: Entrenamiento offline, FastAPI solo inferencia
- **Privacidad**: No cookies terceros, JWT + cookies primera parte
- **Modelos Duales Mandatorios**: Siempre Classifier + Regressor en cada solicitud
- **Identificación Robusta**: Usuarios autenticados (JWT) + anónimos recurrentes (user_temp_id)

## External Dependencies
- **Firebase/Firestore** - Almacenamiento de logs de comportamiento y datos sociales
- **XGBoost** - Motor de Machine Learning para predicciones
- **Tailwind CSS** - Sistema de diseño utility-first
- **FastAPI** - Framework web para backend de alta velocidad

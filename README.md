# Frontend Efímero - Sistema de Adaptación Predictiva Profunda de UI

## 📋 Descripción

Sistema revolucionario que genera interfaces de usuario dinámicas usando Machine Learning. Cada página se adapta automáticamente a cada usuario y contexto específico, eliminando el parpadeo visual (Zero Flicker) mediante Server-Side Rendering inteligente.

## 🎯 Concepto Clave: Frontend Efímero

- **UI Dinámica**: El diseño no es estático - se genera contextualmente por XGBoost
- **Adaptación Profunda**: Personalización granular con valores continuos (ej. `font-size: 1.15rem`)
- **Zero Flicker**: Cambios aplicados antes del renderizado inicial
- **Perfilado Instantáneo**: Funciona para usuarios anónimos y autenticados

## 🏗️ Arquitectura de 3 Fases

### FASE 1: Inicialización y Recolección
- Frontend captura contexto JS (hora local, preferencias SO, viewport)
- Envío bloqueante a FastAPI

### FASE 2: Decisión Inteligente (Momento Crítico)
- FastAPI consulta logs históricos en Firestore
- Preprocesamiento con Scikit-learn
- **Doble predicción obligatoria**: XGBoost Classifier + Regressor
- Respuesta con tokens de diseño

### FASE 3: Renderizado Efímero y Feedback
- SSR inyecta tokens CSS antes de hidratación
- Bucle de feedback continuo para entrenamiento

## 🛠️ Stack Tecnológico

### Backend / Capa de Lógica
- **FastAPI** - Servidor API ultrarrápido
- **XGBoost** - Motor de IA dual (Classifier + Regressor)
- **Scikit-learn** - Preprocesamiento de features
- **Firestore** - Logs de comportamiento y entorno social
- **Joblib** - Modelos en memoria para inferencia instantánea

### Frontend / Capa de Presentación
- **Next.js** - SSR y componentes React
- **Tailwind CSS** - Consumo de variables y clases predichas
- **TypeScript** - Tipado fuerte para robustez

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)
```bash
# Clonar y levantar stack completo
git clone <repo>
cd Frontend_Efimero
docker-compose up -d

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Docs API: http://localhost:8000/docs
```

### Opción 2: Desarrollo Local

#### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env  # Configurar variables
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local  # Configurar API URL
npm run dev
```

## 📊 Ejemplo de Uso

```tsx
import { AdaptiveUIProvider } from '@/components/adaptive/AdaptiveUIProvider';
import { AdaptiveButton, AdaptiveCard } from '@/components/adaptive/AdaptiveComponents';

export default function Dashboard() {
  return (
    <AdaptiveUIProvider>
      <AdaptiveCard title="Panel Personalizado">
        <AdaptiveText>
          Este texto se adapta automáticamente según tu contexto,
          comportamiento histórico y entorno social.
        </AdaptiveText>
        
        <AdaptiveButton variant="primary">
          Botón con espaciado y tipografía predicha por IA
        </AdaptiveButton>
      </AdaptiveCard>
    </AdaptiveUIProvider>
  );
}
```

## 🎨 Tokens de Diseño Predichos

### Clases CSS (XGBoost Classifier)
- `densidad-alta` / `densidad-media` / `densidad-baja`
- `fuente-serif` / `fuente-sans` / `fuente-mono`
- `modo-nocturno` / `modo-claro`

### Variables CSS (XGBoost Regressor)
- `--font-size-base` - Tamaño de fuente adaptativo
- `--spacing-unit` - Espaciado contextual
- `--border-radius` - Bordes personalizados

## 📈 Métricas de Calidad

- **Clasificación**: F1-Score para equilibrio precisión/recall
- **Regresión**: RMSE para error mínimo en tokens numéricos
- **Features Compuestas**: Datos cruzados como `TasaDeError_tactil_vs_mouse`

## 🔧 Estructura del Proyecto

```
Frontend_Efimero/
├── backend/                 # FastAPI + XGBoost + Firestore
│   ├── app/
│   │   ├── main.py         # Aplicación principal
│   │   ├── api/routes/     # Endpoints FASE 2 y 3
│   │   ├── ml/             # Modelos duales obligatorios
│   │   └── services/       # Lógica de negocio modular
│   └── models/             # Modelos XGBoost entrenados
├── frontend/               # Next.js + Tailwind + TypeScript
│   ├── src/
│   │   ├── components/adaptive/  # Componentes Frontend Efímero
│   │   ├── hooks/          # useEphemeralContext (FASE 1)
│   │   └── lib/            # Cliente API
├── shared/                 # Tipos compartidos
└── openspec/              # Especificaciones OpenSpec
```

## 🎯 Características Únicas

- **Latencia Crítica**: Modelos XGBoost en memoria RAM
- **Identificación Robusta**: JWT + cookies primera parte
- **Separación ML**: Entrenamiento offline, FastAPI solo inferencia
- **Privacidad**: Sin cookies de terceros
- **Escalabilidad**: Arquitectura preparada para múltiples usuarios concurrentes

## 📚 Documentación

- [Backend README](./backend/README.md) - Configuración FastAPI y ML
- [Frontend README](./frontend/README.md) - Componentes y hooks
- [OpenSpec](./openspec/) - Especificaciones técnicas detalladas

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

---

**Frontend Efímero** - El futuro de las interfaces adaptativas está aquí. 🎨✨
# Backend FastAPI para Frontend Efímero

## Instalación

1. Crear entorno virtual:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
copy .env.example .env
# Editar .env con tus valores
```

4. Ejecutar servidor de desarrollo:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Estructura del Proyecto

```
backend/
├── app/
│   ├── main.py              # Aplicación FastAPI principal
│   ├── core/
│   │   ├── config.py        # Configuración de la app
│   │   └── lifespan.py      # Eventos startup/shutdown
│   ├── api/
│   │   ├── main.py          # Router principal API
│   │   └── routes/          # Endpoints
│   ├── models/              # Modelos Pydantic
│   ├── services/            # Lógica de negocio
│   └── ml/                  # Machine Learning
├── models/                  # Modelos XGBoost entrenados
├── requirements.txt         # Dependencias Python
└── .env.example            # Variables de entorno ejemplo
```

## Arquitectura de 3 Fases

### FASE 1: Inicialización y Recolección
- Frontend captura contexto JS
- Envío de datos al endpoint `/api/v1/adaptive-ui/predict`

### FASE 2: Decisión Inteligente (FastAPI + XGBoost)
- Consulta logs históricos en Firestore
- Preprocesamiento con Scikit-learn
- Doble predicción XGBoost (Classifier + Regressor)
- Respuesta con tokens de diseño

### FASE 3: Renderizado Efímero
- Frontend inyecta tokens CSS
- Bucle de feedback a `/api/v1/adaptive-ui/feedback`

## Endpoints Principales

- `GET /health` - Health check
- `POST /api/v1/adaptive-ui/predict` - Predicción adaptativa
- `POST /api/v1/adaptive-ui/feedback` - Feedback de comportamiento

## Documentación

### Feature Engineering
- **[Architecture Guide](docs/feature_engineering.md)** - Arquitectura completa del sistema de ingeniería de características
- **[Examples & Use Cases](docs/feature_engineering_examples.md)** - Ejemplos prácticos y casos de uso reales
- **[Quick Reference](docs/feature_engineering_reference.md)** - Referencia rápida para desarrolladores

### Model Training
- **[Training Pipeline](docs/model_training.md)** - Pipeline completo de entrenamiento XGBoost
- **[Training Scripts](docs/training_scripts.md)** - Documentación de scripts de entrenamiento
- **[Data Schemas](docs/model_schemas.md)** - Esquemas de datos y formatos

### Model Retraining
- **[Retraining Guidelines](docs/model_retraining.md)** - Procedimientos completos de reentrenamiento
- **[Retraining Scripts](docs/retraining_scripts.md)** - Scripts automatizados de reentrenamiento

### Performance Monitoring
- **[Monitoring System](docs/performance_monitoring.md)** - Infraestructura completa de monitoreo en tiempo real
- **[Monitoring Scripts](docs/monitoring_scripts.md)** - Scripts de configuración y gestión del monitoreo

### Testing
- **Cobertura**: 74 tests unitarios, integración y rendimiento
- **Performance**: <100ms de latencia validada
- **Fixtures**: Sistema completo de datos de prueba

## Desarrollo

```bash
# Formatear código
black app/
isort app/

# Linting
flake8 app/

# Tests
pytest

# Servidor de producción
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```
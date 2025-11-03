# Docker Compose para Frontend Efímero
# Sistema de Adaptación Predictiva Profunda de UI

## Comandos Básicos

### Desarrollo
```bash
# Construir e iniciar todos los servicios
docker-compose up --build

# Iniciar en modo background
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Producción
```bash
# Usar archivo de producción (si existe)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Escalar servicios
docker-compose up -d --scale backend=2
```

### Gestión
```bash
# Parar todos los servicios
docker-compose down

# Parar y eliminar volúmenes
docker-compose down -v

# Reconstruir servicios
docker-compose build --no-cache

# Reiniciar un servicio específico
docker-compose restart backend

# Ejecutar comandos en contenedores
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Monitoreo
```bash
# Ver estado de servicios
docker-compose ps

# Ver uso de recursos
docker stats $(docker-compose ps -q)

# Inspeccionar red
docker network inspect frontend-efimero_efimero-network
```

## Servicios Disponibles

### Frontend (Next.js)
- **Puerto**: 3000
- **URL**: http://localhost:3000
- **Health Check**: http://localhost:3000/health

### Backend (FastAPI)
- **Puerto**: 8000
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Redis (Cache)
- **Puerto**: 6379
- **Host**: redis:6379 (interno)

### Nginx (Reverse Proxy)
- **Puerto**: 80
- **URL**: http://localhost
- **Frontend**: http://localhost/
- **API**: http://localhost/api/

## Variables de Entorno

### Backend
- `DEBUG`: Modo debug (true/false)
- `SECRET_KEY`: Clave secreta para JWT
- `FIREBASE_PROJECT_ID`: ID del proyecto Firebase
- `CORS_ORIGINS`: Orígenes permitidos para CORS

### Frontend
- `NEXT_PUBLIC_API_URL`: URL del backend API
- `NODE_ENV`: Entorno de Node.js

## Volúmenes

- `models-data`: Modelos XGBoost entrenados
- `redis-data`: Datos persistentes de Redis

## Red

- **Network**: efimero-network (172.20.0.0/16)
- **DNS interno**: Los servicios se comunican por nombre (backend, frontend, redis)

## Troubleshooting

### Backend no inicia
```bash
# Ver logs detallados
docker-compose logs backend

# Verificar variables de entorno
docker-compose exec backend env

# Verificar archivos de modelos
docker-compose exec backend ls -la models/
```

### Frontend no se conecta al backend
```bash
# Verificar conectividad de red
docker-compose exec frontend ping backend

# Verificar variables de entorno
docker-compose exec frontend env | grep API_URL
```

### Problemas de permisos
```bash
# Reconstruir con usuario correcto
docker-compose build --no-cache

# Verificar permisos de volúmenes
docker-compose exec backend ls -la /app/models
```

## Desarrollo Local vs Docker

### Desarrollo Local
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Conexión directa entre servicios

### Docker Compose
- Todo: http://localhost (via Nginx)
- Frontend: http://localhost:3000 (directo)
- Backend: http://localhost:8000 (directo)
- Comunicación interna via nombres de servicio

## Notas Importantes

1. **Modelos ML**: Los modelos se montan como volúmen. Entrena los modelos localmente primero.
2. **Firebase**: Usa credenciales de prueba en desarrollo. Configura Firebase real para producción.
3. **SSL**: Nginx está configurado para HTTP. Descomenta la sección SSL para HTTPS.
4. **Escalabilidad**: Usa `--scale` para múltiples instancias del backend.
5. **Logs**: Los logs se muestran en stdout. Usa un sistema de logging para producción.
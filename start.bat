@echo off
REM Script de inicio rápido para Frontend Efímero - Windows
REM Sistema de Adaptación Predictiva Profunda de UI

echo 🚀 Iniciando Frontend Efímero con Docker Compose...

REM Verificar que Docker esté corriendo
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está corriendo. Inicia Docker Desktop primero.
    pause
    exit /b 1
)

echo ✅ Docker está corriendo

REM Parar servicios existentes si están corriendo
echo 🛑 Parando servicios existentes...
docker-compose down

REM Construir e iniciar servicios
echo 🔨 Construyendo imágenes...
docker-compose build

echo 🚀 Iniciando servicios...
docker-compose up -d

REM Esperar a que los servicios estén listos
echo ⏳ Esperando a que los servicios inicien...
timeout /t 15 /nobreak >nul

REM Verificar servicios
echo 🔍 Verificando servicios...

REM Verificar backend
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host '✅ Backend está funcionando' -ForegroundColor Green } } catch { Write-Host '❌ Backend no responde' -ForegroundColor Red }"

REM Verificar frontend
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000/health' -UseBasicParsing -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host '✅ Frontend está funcionando' -ForegroundColor Green } } catch { Write-Host '❌ Frontend no responde' -ForegroundColor Red }"

echo.
echo 🎉 Frontend Efímero está corriendo!
echo.
echo URLs disponibles:
echo   Frontend:     http://localhost:3000
echo   Backend API:  http://localhost:8000
echo   API Docs:     http://localhost:8000/docs
echo   Nginx Proxy:  http://localhost
echo   Health Checks:
echo     Frontend:   http://localhost:3000/health
echo     Backend:    http://localhost:8000/health
echo.

REM Preguntar si mostrar logs
set /p "show_logs=¿Mostrar logs en tiempo real? (y/n): "
if /i "%show_logs%"=="y" (
    echo 📋 Mostrando logs (Ctrl+C para parar)...
    echo.
    docker-compose logs -f
) else (
    echo.
    echo ℹ️  Para ver logs: docker-compose logs -f
    echo ℹ️  Para parar:    docker-compose down
    pause
)
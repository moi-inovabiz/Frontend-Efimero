#!/bin/bash

# Script de inicio rápido para Frontend Efímero
# Sistema de Adaptación Predictiva Profunda de UI

set -e

echo "🚀 Iniciando Frontend Efímero con Docker Compose..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker no está corriendo. Inicia Docker Desktop primero.${NC}"
    exit 1
fi

# Verificar que Docker Compose esté disponible
if ! command -v docker-compose > /dev/null 2>&1; then
    echo -e "${RED}❌ docker-compose no está instalado.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker está corriendo${NC}"

# Parar servicios existentes si están corriendo
echo -e "${YELLOW}🛑 Parando servicios existentes...${NC}"
docker-compose down

# Construir e iniciar servicios
echo -e "${YELLOW}🔨 Construyendo imágenes...${NC}"
docker-compose build

echo -e "${YELLOW}🚀 Iniciando servicios...${NC}"
docker-compose up -d

# Esperar a que los servicios estén listos
echo -e "${YELLOW}⏳ Esperando a que los servicios inicien...${NC}"
sleep 10

# Verificar estado de servicios
echo -e "${YELLOW}🔍 Verificando estado de servicios...${NC}"

# Función para verificar health check
check_service() {
    local service=$1
    local url=$2
    local retries=10
    local count=0

    while [ $count -lt $retries ]; do
        if curl -f -s $url > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service está funcionando${NC}"
            return 0
        fi
        count=$((count + 1))
        echo -e "${YELLOW}⏳ Esperando $service... ($count/$retries)${NC}"
        sleep 3
    done

    echo -e "${RED}❌ $service no responde después de $retries intentos${NC}"
    return 1
}

# Verificar servicios
echo ""
echo "Verificando servicios:"
check_service "Backend" "http://localhost:8000/health"
check_service "Frontend" "http://localhost:3000/health"

# Mostrar URLs disponibles
echo ""
echo -e "${GREEN}🎉 Frontend Efímero está corriendo!${NC}"
echo ""
echo "URLs disponibles:"
echo -e "  Frontend:     ${GREEN}http://localhost:3000${NC}"
echo -e "  Backend API:  ${GREEN}http://localhost:8000${NC}"
echo -e "  API Docs:     ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  Nginx Proxy:  ${GREEN}http://localhost${NC}"
echo -e "  Health Checks:"
echo -e "    Frontend:   ${GREEN}http://localhost:3000/health${NC}"
echo -e "    Backend:    ${GREEN}http://localhost:8000/health${NC}"
echo ""

# Mostrar logs en tiempo real
echo -e "${YELLOW}📋 Mostrando logs (Ctrl+C para parar)...${NC}"
echo ""
docker-compose logs -f
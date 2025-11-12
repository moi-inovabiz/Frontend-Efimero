# Diagnóstico completo de configuración de Gemini API

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "DIAGNÓSTICO DE GEMINI API" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar archivos .env
Write-Host "1. Variables de entorno en archivos:" -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".env") {
    $envContent = Get-Content ".env" | Where-Object { $_ -match "GEMINI" }
    Write-Host "   .env (Docker):" -ForegroundColor White
    $envContent | ForEach-Object { 
        $masked = $_ -replace '(AIza\w{10})\w+', '$1...[OCULTO]'
        Write-Host "      $masked" -ForegroundColor Gray
    }
} else {
    Write-Host "   ⚠️  .env NO EXISTE" -ForegroundColor Red
}

Write-Host ""

if (Test-Path "frontend/.env.local") {
    $envLocalContent = Get-Content "frontend/.env.local" | Where-Object { $_ -match "GEMINI" }
    Write-Host "   frontend/.env.local:" -ForegroundColor White
    $envLocalContent | ForEach-Object { 
        $masked = $_ -replace '(AIza\w{10})\w+', '$1...[OCULTO]'
        Write-Host "      $masked" -ForegroundColor Gray
    }
} else {
    Write-Host "   ⚠️  frontend/.env.local NO EXISTE" -ForegroundColor Red
}

Write-Host ""
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host ""

# 2. Verificar contenedor Docker
Write-Host "2. Variables en contenedor Docker:" -ForegroundColor Yellow
Write-Host ""

try {
    $containerVar = docker exec frontend-efimero-frontend-1 env 2>$null | Select-String -Pattern "NEXT_PUBLIC_GEMINI_API_KEY"
    if ($containerVar) {
        $masked = $containerVar -replace '(AIza\w{10})\w+', '$1...[OCULTO]'
        Write-Host "   ✅ Variable encontrada: $masked" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Variable NO encontrada en contenedor" -ForegroundColor Red
    }
} catch {
    Write-Host "   ⚠️  Contenedor no está corriendo" -ForegroundColor Red
}

Write-Host ""
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host ""

# 3. Probar API key directamente
Write-Host "3. Prueba de API key con Gemini:" -ForegroundColor Yellow
Write-Host ""

$apiKey = $null
if (Test-Path ".env") {
    $envLine = Get-Content ".env" | Where-Object { $_ -match "^GEMINI_API_KEY=" }
    if ($envLine) {
        $apiKey = $envLine -replace '^GEMINI_API_KEY=', ''
    }
}

if ($apiKey) {
    Write-Host "   Probando API key..." -ForegroundColor Gray
    $URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$apiKey"
    
    $body = @{
        contents = @(
            @{
                parts = @(
                    @{
                        text = "Responde solo: OK"
                    }
                )
            }
        )
    } | ConvertTo-Json -Depth 5
    
    try {
        $response = Invoke-RestMethod -Uri $URL -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
        $result = $response.candidates[0].content.parts[0].text
        Write-Host "   ✅ API key VÁLIDA - Gemini respondió: $result" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ API key INVÁLIDA - Error: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "   ⚠️  No se pudo leer la API key del archivo .env" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host ""

# 4. Estado de contenedores
Write-Host "4. Estado de contenedores:" -ForegroundColor Yellow
Write-Host ""

$containers = docker compose ps --format "table {{.Name}}\t{{.Status}}" 2>$null
if ($containers) {
    $containers | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
} else {
    Write-Host "   ⚠️  No hay contenedores corriendo" -ForegroundColor Red
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "DIAGNÓSTICO COMPLETADO" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "SIGUIENTE PASO:" -ForegroundColor Yellow
Write-Host "  Abre en el navegador: http://localhost:3000/efimero" -ForegroundColor White
Write-Host "  Abre DevTools (F12) → Console para ver logs" -ForegroundColor White
Write-Host ""

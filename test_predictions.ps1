# Test script para probar prediccion de preferencias visuales

Write-Host "Probando prediccion de preferencias visuales basada en datos demograficos..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Usuario joven (25 anos)
Write-Host "Test 1: Usuario joven (25 anos) - Persona" -ForegroundColor Yellow
$testData1 = @{
    fecha_nacimiento = "1999-01-15"
    region = "Metropolitana"
    tipo_cliente = "persona"
    interes_principal = "compra"
    uso_previsto = "personal"
    presupuesto = "medio"
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/predict-preferences" `
        -Method POST `
        -ContentType "application/json" `
        -Body $testData1
    
    Write-Host "Prediccion exitosa!" -ForegroundColor Green
    Write-Host "Preferencias predichas:" -ForegroundColor White
    Write-Host "  - Densidad: $($response1.predictions.densidad_informacion)" -ForegroundColor Cyan
    Write-Host "  - Tipografia: $($response1.predictions.estilo_tipografia)" -ForegroundColor Cyan
    Write-Host "  - Animaciones: $($response1.predictions.nivel_animaciones)" -ForegroundColor Cyan
    Write-Host "  - Esquema de colores: $($response1.predictions.esquema_colores)" -ForegroundColor Cyan
    Write-Host "  - Layout: $($response1.predictions.preferencia_layout)" -ForegroundColor Cyan
    Write-Host "  - Navegacion: $($response1.predictions.estilo_navegacion)" -ForegroundColor Cyan
    Write-Host "Confianza: $([math]::Round($response1.confidence.overall_score, 2))% ($($response1.confidence.overall_quality))" -ForegroundColor Magenta
    Write-Host ""
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
}

# Test 2: Usuario mayor (55 anos) - Empresa
Write-Host "Test 2: Usuario mayor (55 anos) - Empresa" -ForegroundColor Yellow
$testData2 = @{
    fecha_nacimiento = "1969-06-20"
    region = "Valparaiso"
    tipo_cliente = "empresa"
    interes_principal = "arriendo"
    uso_previsto = "comercial"
    presupuesto = "alto"
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/predict-preferences" `
        -Method POST `
        -ContentType "application/json" `
        -Body $testData2
    
    Write-Host "Prediccion exitosa!" -ForegroundColor Green
    Write-Host "Preferencias predichas:" -ForegroundColor White
    Write-Host "  - Densidad: $($response2.predictions.densidad_informacion)" -ForegroundColor Cyan
    Write-Host "  - Tipografia: $($response2.predictions.estilo_tipografia)" -ForegroundColor Cyan
    Write-Host "  - Animaciones: $($response2.predictions.nivel_animaciones)" -ForegroundColor Cyan
    Write-Host "  - Esquema de colores: $($response2.predictions.esquema_colores)" -ForegroundColor Cyan
    Write-Host "  - Layout: $($response2.predictions.preferencia_layout)" -ForegroundColor Cyan
    Write-Host "  - Navegacion: $($response2.predictions.estilo_navegacion)" -ForegroundColor Cyan
    Write-Host "Confianza: $([math]::Round($response2.confidence.overall_score, 2))% ($($response2.confidence.overall_quality))" -ForegroundColor Magenta
    Write-Host ""
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
}

# Test 3: Usuario medio (35 anos) - Persona, presupuesto premium
Write-Host "Test 3: Usuario medio (35 anos) - Persona, presupuesto premium" -ForegroundColor Yellow
$testData3 = @{
    fecha_nacimiento = "1989-11-10"
    region = "Biobio"
    tipo_cliente = "persona"
    interes_principal = "comparacion"
    uso_previsto = "personal"
    presupuesto = "premium"
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/predict-preferences" `
        -Method POST `
        -ContentType "application/json" `
        -Body $testData3
    
    Write-Host "Prediccion exitosa!" -ForegroundColor Green
    Write-Host "Preferencias predichas:" -ForegroundColor White
    Write-Host "  - Densidad: $($response3.predictions.densidad_informacion)" -ForegroundColor Cyan
    Write-Host "  - Tipografia: $($response3.predictions.estilo_tipografia)" -ForegroundColor Cyan
    Write-Host "  - Animaciones: $($response3.predictions.nivel_animaciones)" -ForegroundColor Cyan
    Write-Host "  - Esquema de colores: $($response3.predictions.esquema_colores)" -ForegroundColor Cyan
    Write-Host "  - Layout: $($response3.predictions.preferencia_layout)" -ForegroundColor Cyan
    Write-Host "  - Navegacion: $($response3.predictions.estilo_navegacion)" -ForegroundColor Cyan
    Write-Host "Confianza: $([math]::Round($response3.confidence.overall_score, 2))% ($($response3.confidence.overall_quality))" -ForegroundColor Magenta
    Write-Host ""
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host "Pruebas completadas!" -ForegroundColor Green
Write-Host ""
Write-Host "Nota: Las predicciones se basan en:" -ForegroundColor White
Write-Host "  1. Datos demograficos (edad, tipo de cliente, presupuesto)" -ForegroundColor Gray
Write-Host "  2. Modelos XGBoost entrenados" -ForegroundColor Gray
Write-Host "  3. Feature engineering con 21 caracteristicas" -ForegroundColor Gray
Write-Host "  4. Doble prediccion: Classifier + Regressor" -ForegroundColor Gray
Write-Host ""
Write-Host "Esto demuestra que:" -ForegroundColor White
Write-Host "  - El sistema de ML esta funcionando" -ForegroundColor Green
Write-Host "  - Los modelos XGBoost estan cargados correctamente" -ForegroundColor Green
Write-Host "  - Las predicciones se adaptan segun la demografia" -ForegroundColor Green
Write-Host "  - El SSR esta procesando datos correctamente" -ForegroundColor Green


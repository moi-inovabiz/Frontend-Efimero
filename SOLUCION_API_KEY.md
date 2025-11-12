# 🔧 Solución: API Key de Gemini Comprometida

## 🔴 Problema
La API key de Gemini fue reportada como "leaked" (filtrada) porque estaba en texto plano en el repositorio Git. Google la deshabilitó automáticamente por seguridad.

**Error mostrado:**
```
Gemini API error: Your API key was reported as leaked. Please use another API key
```

---

## ✅ Solución Rápida

### **Paso 1: Obtener nueva API Key**

1. Ve a: https://aistudio.google.com/app/apikey
2. Inicia sesión con tu cuenta de Google
3. Click en **"Create API Key"** o **"Get API Key"**
4. Copia la nueva API key (empieza con `AIza...`)

### **Paso 2: Configurar en desarrollo local (sin Docker)**

Edita el archivo `frontend/.env.local`:

```bash
# frontend/.env.local
NEXT_PUBLIC_GEMINI_API_KEY=AIzaSy... # <- Pega aquí tu nueva API key
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Luego reinicia el servidor:

```powershell
cd frontend
npm run dev
```

### **Paso 3: Configurar en Docker**

Edita el archivo `.env` en la raíz del proyecto:

```bash
# .env (raíz del proyecto)
GEMINI_API_KEY=AIzaSy... # <- Pega aquí tu nueva API key
```

Luego reconstruye los contenedores:

```powershell
docker compose down
docker compose up -d --build
```

---

## 🔒 Seguridad: Prevenir Futuros Leaks

### **1. Verificar que .env está en .gitignore**

Asegúrate que estos archivos estén en `.gitignore`:

```gitignore
# .gitignore
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
```

### **2. Remover API keys del historial de Git**

Si ya commiteaste la API key, necesitas limpiar el historial:

```powershell
# Ver commits con API key
git log --all --full-history -- docker-compose.yml

# Opción 1: Revertir solo ese commit (si es reciente)
git revert <commit-hash>

# Opción 2: Limpiar historial completo (PELIGROSO - solo si es necesario)
# git filter-branch --force --index-filter "git rm --cached --ignore-unmatch docker-compose.yml" --prune-empty --tag-name-filter cat -- --all
```

### **3. Rotar la API key vieja**

En Google AI Studio:
1. Ve a tus API keys
2. **Desactiva** o **elimina** la API key vieja (`AIzaSyDmTRpiiVF7RGr8X8VnfCzeObff3zMqngo`)
3. Usa SOLO la nueva API key

---

## 📝 Archivos Modificados

Los siguientes archivos fueron actualizados para usar variables de entorno en lugar de valores hardcodeados:

### ✅ `docker-compose.yml`
```yaml
# ANTES (INSEGURO):
- NEXT_PUBLIC_GEMINI_API_KEY=AIzaSyDmTRpiiVF7RGr8X8VnfCzeObff3zMqngo

# AHORA (SEGURO):
- NEXT_PUBLIC_GEMINI_API_KEY=${GEMINI_API_KEY}
```

### ✅ `frontend/.env.local` (nuevo archivo)
```bash
NEXT_PUBLIC_GEMINI_API_KEY=TU_NUEVA_API_KEY_AQUI
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_BACKEND_URL=http://backend:8000
INTERNAL_API_URL=http://backend:8000/api/v1
```

### ✅ `.env` (nuevo archivo en raíz)
```bash
GEMINI_API_KEY=TU_NUEVA_API_KEY_AQUI
```

### ✅ `frontend/src/hooks/useGeminiUI.ts`
- Agregado detección de API key leaked/invalid
- Previene loop infinito cuando hay error de API key
- Mensaje de error más claro

### ✅ `frontend/src/app/efimero/page.tsx`
- Agregado `hasErroredRef` para evitar loops
- UI mejorada con instrucciones paso a paso
- Botón "Reintentar" deshabilitado si es error de API key

---

## 🧪 Testing

### **Test 1: Verificar que la nueva API key funciona**

```powershell
# En desarrollo
cd frontend
npm run dev

# Navega a: http://localhost:3000/demo
# Click en "Frontend Efímero Personalizado"
# Deberías ver la UI generada por Gemini
```

### **Test 2: Verificar en Docker**

```powershell
docker compose up -d --build
docker compose logs -f frontend

# Navega a: http://localhost:3000/efimero
# Verifica en la consola del navegador que NO haya errores "leaked"
```

---

## 🐛 Troubleshooting

### **Error: "Gemini API key no configurada"**

**Causa:** La variable de entorno no está definida.

**Solución:**
```powershell
# Verifica que .env.local existe
ls frontend/.env.local

# Si no existe, créalo con:
echo "NEXT_PUBLIC_GEMINI_API_KEY=TU_API_KEY" > frontend/.env.local
```

### **Error: Loop infinito en consola**

**Causa:** El código intentaba reintentar infinitamente cuando había error.

**Solución:** Ya está arreglado con `hasErroredRef` flag. Si persiste:
1. Limpia caché del navegador (Ctrl+Shift+Delete)
2. Limpia sessionStorage: DevTools → Application → Session Storage → Clear
3. Recarga la página con Ctrl+F5

### **Error 403: "API key not valid"**

**Causa:** La API key es inválida o no tiene permisos.

**Solución:**
1. Verifica que copiaste la API key completa
2. En Google AI Studio, verifica que la API key tenga el servicio "Gemini API" habilitado
3. Crea una nueva API key si la actual no funciona

### **Error 429: "Resource has been exhausted"**

**Causa:** Límite de cuota gratuita de Gemini alcanzado.

**Solución:** 
- El sistema automáticamente usa un fallback UI
- Espera unas horas o actualiza a plan de pago
- Verás una UI estática de Mercedes-Benz mientras tanto

---

## 💡 Buenas Prácticas

### ✅ DO (Hacer)
- Usar variables de entorno para API keys
- Agregar `.env*` a `.gitignore`
- Rotar API keys periódicamente
- Usar diferentes API keys para dev/staging/production

### ❌ DON'T (No Hacer)
- Hardcodear API keys en código
- Commitear archivos `.env` a Git
- Compartir API keys por email/chat
- Usar la misma API key en múltiples proyectos

---

## 📞 Soporte

Si sigues teniendo problemas:

1. **Revisa los logs del navegador:** DevTools → Console
2. **Revisa los logs del servidor:** `docker compose logs -f frontend`
3. **Verifica la API key:** Copia y pega directamente sin espacios extra

---

## ✅ Checklist de Verificación

- [ ] Nueva API key obtenida de Google AI Studio
- [ ] Archivo `frontend/.env.local` creado con la nueva key
- [ ] Archivo `.env` en raíz creado (para Docker)
- [ ] `.gitignore` incluye `.env` y `.env.local`
- [ ] API key vieja desactivada en Google AI Studio
- [ ] Servidor reiniciado (`npm run dev` o `docker compose up`)
- [ ] Test: `/efimero` carga sin errores
- [ ] Test: Consola no muestra "leaked" o "invalid"
- [ ] Commit de cambios SIN incluir archivos `.env`

---

**Última actualización:** 12 de Noviembre, 2025

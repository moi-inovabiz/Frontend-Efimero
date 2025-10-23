#!/usr/bin/env python3
"""
Script de inicialización para el Backend del Frontend Efímero
Configura el entorno de desarrollo
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_backend():
    """Configura el entorno backend"""
    backend_dir = Path(__file__).parent
    
    print("🚀 Configurando Backend del Frontend Efímero...")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        sys.exit(1)
    
    # Crear entorno virtual si no existe
    venv_path = backend_dir / "venv"
    if not venv_path.exists():
        print("📦 Creando entorno virtual...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=backend_dir)
    
    # Activar entorno e instalar dependencias
    if os.name == 'nt':  # Windows
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:  # Linux/Mac
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    print("📚 Instalando dependencias...")
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], cwd=backend_dir)
    
    # Crear archivo .env si no existe
    env_file = backend_dir / ".env"
    env_example = backend_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("⚙️ Creando archivo .env...")
        with open(env_example) as f:
            content = f.read()
        
        # Generar claves secretas básicas para desarrollo
        import secrets
        secret_key = secrets.token_urlsafe(32)
        jwt_secret = secrets.token_urlsafe(32)
        
        content = content.replace("your-super-secret-key-change-in-production", secret_key)
        content = content.replace("your-jwt-secret-key-change-in-production", jwt_secret)
        
        with open(env_file, 'w') as f:
            f.write(content)
    
    # Crear directorio para modelos
    models_dir = backend_dir / "models"
    models_dir.mkdir(exist_ok=True)
    
    print("✅ Backend configurado exitosamente!")
    print(f"🐍 Python: {python_path}")
    print(f"📁 Directorio: {backend_dir}")
    
    print("\n🚀 Para iniciar el servidor:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("   uvicorn app.main:app --reload")

if __name__ == "__main__":
    setup_backend()
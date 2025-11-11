"""
Script de prueba del sistema de matching inteligente
Simula diferentes contextos de usuario y muestra el matching
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"

def test_matching(contexto, descripcion):
    """Prueba el matching con un contexto específico"""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {descripcion}")
    print(f"{'='*80}")
    
    # Crear sesión nueva (UUID aleatorio)
    import uuid
    session_id = str(uuid.uuid4())
    
    print(f"\n📝 Contexto enviado:")
    for key, value in contexto.items():
        print(f"   {key}: {value}")
    
    # Hacer request con contexto
    response = requests.post(
        f"{API_BASE}/personas/assign",
        headers={
            "Content-Type": "application/json",
            "X-Session-ID": session_id
        },
        json=contexto
    )
    
    if response.status_code == 200:
        data = response.json()
        persona = data["persona"]
        score = data.get("matching_score", "N/A")
        
        print(f"\n✅ RESULTADO:")
        print(f"   Persona: {persona['nombre']} {persona['apellido']}")
        print(f"   Tipo: {persona['tipo_cliente']}")
        print(f"   Edad: {persona['edad']} años")
        print(f"   Región: {persona['region']}")
        print(f"   Matching Score: {score}")
        
        if "matching_info" in data:
            print(f"\n📊 Info del Matching:")
            info = data["matching_info"]
            print(f"   Usó contexto: {info['used_context']}")
            if "context_fields" in info:
                fields = info["context_fields"]
                print(f"   Hora: {fields['hora']}h")
                print(f"   Región: {fields['region']}")
                print(f"   Dispositivo: {fields['dispositivo']}")
                print(f"   Fin de semana: {fields['fin_semana']}")
        
        print(f"\n🎨 Preferencias Visuales:")
        print(f"   Densidad: {persona.get('densidad_informacion', 'N/A')}")
        print(f"   Animaciones: {persona.get('nivel_animaciones', 'N/A')}")
        print(f"   Layout: {persona.get('preferencia_layout', 'N/A')}")
        print(f"   Color favorito: {persona.get('color_favorito', 'N/A')}")
        
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)

def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 TEST DE MATCHING INTELIGENTE - Frontend Efímero       ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Test 1: Usuario joven en móvil, noche, fin de semana
    test_matching(
        {
            "hora_del_dia": 21,
            "es_fin_de_semana": True,
            "ciudad": "CL",
            "region": "Santiago",
            "pais": "America",
            "es_movil": True,
            "es_tablet": False,
            "sistema_operativo": "Android",
            "tipo_conexion": "4g"
        },
        "Usuario joven en móvil - Noche de sábado"
    )
    
    # Test 2: Empresa en desktop, día laboral
    test_matching(
        {
            "hora_del_dia": 10,
            "es_fin_de_semana": False,
            "ciudad": "CL",
            "region": "Santiago",
            "pais": "America",
            "es_movil": False,
            "es_tablet": False,
            "sistema_operativo": "Windows",
            "tipo_conexion": "ethernet"
        },
        "Empresa en desktop - Martes 10:00 AM"
    )
    
    # Test 3: Tablet en tarde, día laboral
    test_matching(
        {
            "hora_del_dia": 15,
            "es_fin_de_semana": False,
            "ciudad": "CL",
            "region": "Valparaiso",
            "pais": "America",
            "es_movil": False,
            "es_tablet": True,
            "sistema_operativo": "iOS",
            "tipo_conexion": "wifi"
        },
        "Tablet iPad - Miércoles 15:00 PM en Valparaíso"
    )
    
    # Test 4: Sin contexto (fallback a aleatorio)
    print(f"\n{'='*80}")
    print(f"🧪 TEST: Sin contexto (fallback)")
    print(f"{'='*80}")
    
    import uuid
    session_id = str(uuid.uuid4())
    
    response = requests.post(
        f"{API_BASE}/personas/assign",
        headers={
            "Content-Type": "application/json",
            "X-Session-ID": session_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        persona = data["persona"]
        print(f"\n✅ RESULTADO:")
        print(f"   Persona: {persona['nombre']} {persona['apellido']}")
        print(f"   Tipo: {persona['tipo_cliente']}")
        print(f"   Info: {data.get('matching_info', {}).get('note', 'N/A')}")
    
    print(f"\n{'='*80}")
    print("✅ Tests completados")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se puede conectar al backend")
        print("   Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

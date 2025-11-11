"""
Script para generar y poblar personas simuladas en la base de datos.
Crea perfiles variados y realistas para testing y demos.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine, init_db, Base
from app.models.persona_simulada import PersonaSimuladaDB


# Datos para generar personas realistas
NOMBRES_PERSONA = [
    "María", "José", "Carlos", "Ana", "Luis", "Carmen", "Pedro", "Isabel",
    "Francisco", "Rosa", "Miguel", "Elena", "Juan", "Patricia", "Andrés"
]

APELLIDOS = [
    "González", "Muñoz", "Rojas", "Silva", "Contreras", "Fernández", 
    "López", "Martínez", "Pérez", "Sánchez", "Ramírez", "Torres",
    "Flores", "Rivera", "Gómez", "Díaz", "Morales", "Vásquez"
]

NOMBRES_EMPRESA = [
    "Transportes", "Logística", "Distribuidora", "Comercial", "Empresa",
    "Servicios", "Soluciones", "Gestión", "Grupo", "Corporación"
]

APELLIDOS_EMPRESA = [
    "Del Sur", "Central", "Express", "Global", "Rápido", "Premium",
    "Profesional", "Integral", "Universal", "Elite"
]

REGIONES = [
    "Metropolitana", "Valparaíso", "Biobío", "Araucanía", "Los Lagos",
    "Maule", "O'Higgins", "Coquimbo", "Antofagasta", "Atacama"
]

INTERESES = ["compra", "arriendo", "comparacion", "informacion"]
USOS = ["personal", "familiar", "comercial", "transporte"]
PRESUPUESTOS = ["bajo", "medio", "alto", "premium"]

ESQUEMAS_COLOR = ["light", "dark", "auto"]
COLORES = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]
TIPOGRAFIAS = ["sans-serif", "serif"]
DENSIDADES = ["compacta", "normal", "espaciosa"]
ANIMACIONES = ["bajo", "medio", "alto"]
LAYOUTS = ["list", "grid", "cards"]
NAVEGACIONES = ["top", "hamburger", "sidebar"]


def generar_fecha_nacimiento(edad: int) -> datetime:
    """Genera una fecha de nacimiento aproximada para la edad dada."""
    hoy = datetime.now()
    anios_atras = edad + random.randint(-2, 2)  # Variación de ±2 años
    meses_atras = random.randint(0, 11)
    dias_atras = random.randint(0, 28)
    
    fecha = hoy - timedelta(days=365*anios_atras + 30*meses_atras + dias_atras)
    return fecha.date()


async def crear_personas_simuladas():
    """Crea un conjunto variado de personas simuladas."""
    
    personas = []
    
    # ===== PERSONAS INDIVIDUALES =====
    
    # 1. Jóvenes (20-30 años) - Tech savvy, animaciones altas
    for i in range(5):
        edad = random.randint(20, 30)
        personas.append({
            "nombre": random.choice(NOMBRES_PERSONA),
            "apellido": random.choice(APELLIDOS),
            "edad": edad,
            "fecha_nacimiento": generar_fecha_nacimiento(edad),
            "region": random.choice(REGIONES),
            "tipo_cliente": "persona",
            "interes_principal": random.choice(["compra", "comparacion"]),
            "uso_previsto": random.choice(["personal", "familiar"]),
            "presupuesto": random.choice(["medio", "bajo"]),
            "tiene_vehiculo_actual": random.choice([True, False]),
            "tamano_flota": None,
            "esquema_colores": random.choice(["light", "dark"]),
            "color_favorito": random.choice(COLORES),
            "estilo_tipografia": "sans-serif",
            "densidad_informacion": "normal",
            "nivel_animaciones": "alto",
            "preferencia_layout": random.choice(["grid", "cards"]),
            "estilo_navegacion": "hamburger",
            "descripcion": f"Persona joven ({edad} años), usuario digital activo"
        })
    
    # 2. Adultos medios (31-50 años) - Balance entre funcionalidad y estética
    for i in range(8):
        edad = random.randint(31, 50)
        personas.append({
            "nombre": random.choice(NOMBRES_PERSONA),
            "apellido": random.choice(APELLIDOS),
            "edad": edad,
            "fecha_nacimiento": generar_fecha_nacimiento(edad),
            "region": random.choice(REGIONES),
            "tipo_cliente": "persona",
            "interes_principal": random.choice(INTERESES),
            "uso_previsto": random.choice(["personal", "familiar", "comercial"]),
            "presupuesto": random.choice(PRESUPUESTOS),
            "tiene_vehiculo_actual": random.choice([True, True, False]),  # Más probabilidad de tener
            "tamano_flota": None,
            "esquema_colores": "light",
            "color_favorito": random.choice(COLORES),
            "estilo_tipografia": random.choice(["sans-serif", "serif"]),
            "densidad_informacion": random.choice(["normal", "compacta"]),
            "nivel_animaciones": "medio",
            "preferencia_layout": random.choice(LAYOUTS),
            "estilo_navegacion": random.choice(["top", "hamburger"]),
            "descripcion": f"Adulto ({edad} años), usuario equilibrado"
        })
    
    # 3. Adultos mayores (51-70 años) - Simplicidad, menos animaciones
    for i in range(4):
        edad = random.randint(51, 70)
        personas.append({
            "nombre": random.choice(NOMBRES_PERSONA),
            "apellido": random.choice(APELLIDOS),
            "edad": edad,
            "fecha_nacimiento": generar_fecha_nacimiento(edad),
            "region": random.choice(REGIONES),
            "tipo_cliente": "persona",
            "interes_principal": random.choice(["compra", "arriendo"]),
            "uso_previsto": random.choice(["personal", "familiar"]),
            "presupuesto": random.choice(["medio", "alto", "premium"]),
            "tiene_vehiculo_actual": True,
            "tamano_flota": None,
            "esquema_colores": "light",
            "color_favorito": random.choice(COLORES[:3]),  # Colores conservadores
            "estilo_tipografia": "serif",
            "densidad_informacion": "espaciosa",
            "nivel_animaciones": "bajo",
            "preferencia_layout": "list",
            "estilo_navegacion": "top",
            "descripcion": f"Adulto mayor ({edad} años), prefiere simplicidad"
        })
    
    # ===== EMPRESAS =====
    
    # 4. Pequeñas empresas (1-5 vehículos)
    for i in range(4):
        edad = random.randint(35, 55)  # Edad del representante
        tamano = random.randint(1, 5)
        personas.append({
            "nombre": random.choice(NOMBRES_EMPRESA),
            "apellido": random.choice(APELLIDOS_EMPRESA),
            "edad": edad,
            "fecha_nacimiento": generar_fecha_nacimiento(edad),
            "region": random.choice(REGIONES),
            "tipo_cliente": "empresa",
            "interes_principal": random.choice(["compra", "arriendo"]),
            "uso_previsto": "comercial",
            "presupuesto": random.choice(["medio", "alto"]),
            "tiene_vehiculo_actual": True,
            "tamano_flota": tamano,
            "esquema_colores": "light",
            "color_favorito": random.choice(COLORES),
            "estilo_tipografia": "sans-serif",
            "densidad_informacion": "compacta",
            "nivel_animaciones": "medio",
            "preferencia_layout": "grid",
            "estilo_navegacion": "sidebar",
            "descripcion": f"Pequeña empresa, {tamano} vehículos"
        })
    
    # 5. Medianas empresas (6-20 vehículos)
    for i in range(3):
        edad = random.randint(40, 60)
        tamano = random.randint(6, 20)
        personas.append({
            "nombre": random.choice(NOMBRES_EMPRESA),
            "apellido": random.choice(APELLIDOS_EMPRESA),
            "edad": edad,
            "fecha_nacimiento": generar_fecha_nacimiento(edad),
            "region": random.choice(REGIONES[:5]),  # Regiones principales
            "tipo_cliente": "empresa",
            "interes_principal": random.choice(["arriendo", "compra"]),
            "uso_previsto": "comercial",
            "presupuesto": random.choice(["alto", "premium"]),
            "tiene_vehiculo_actual": True,
            "tamano_flota": tamano,
            "esquema_colores": "light",
            "color_favorito": random.choice(COLORES),
            "estilo_tipografia": "sans-serif",
            "densidad_informacion": "compacta",
            "nivel_animaciones": "bajo",
            "preferencia_layout": "grid",
            "estilo_navegacion": "sidebar",
            "descripcion": f"Mediana empresa, {tamano} vehículos"
        })
    
    # 6. Grandes empresas (20+ vehículos)
    for i in range(2):
        edad = random.randint(45, 65)
        tamano = random.randint(20, 100)
        personas.append({
            "nombre": random.choice(NOMBRES_EMPRESA),
            "apellido": random.choice(APELLIDOS_EMPRESA),
            "edad": edad,
            "fecha_nacimiento": generar_fecha_nacimiento(edad),
            "region": "Metropolitana",  # Grandes empresas en Santiago
            "tipo_cliente": "empresa",
            "interes_principal": "arriendo",
            "uso_previsto": "comercial",
            "presupuesto": "premium",
            "tiene_vehiculo_actual": True,
            "tamano_flota": tamano,
            "esquema_colores": "light",
            "color_favorito": COLORES[0],  # Azul corporativo
            "estilo_tipografia": "sans-serif",
            "densidad_informacion": "compacta",
            "nivel_animaciones": "bajo",
            "preferencia_layout": "grid",
            "estilo_navegacion": "sidebar",
            "descripcion": f"Gran empresa, {tamano} vehículos"
        })
    
    return personas


async def poblar_base_de_datos():
    """Función principal que puebla la base de datos con personas simuladas."""
    
    print("🔄 Inicializando base de datos...")
    
    # Crear tablas si no existen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Base de datos inicializada")
    print("🔄 Generando personas simuladas...")
    
    # Generar personas
    personas_data = await crear_personas_simuladas()
    
    print(f"📊 Generadas {len(personas_data)} personas simuladas")
    print("🔄 Insertando en base de datos...")
    
    # Insertar en la base de datos
    async with AsyncSession(engine) as session:
        try:
            for persona_data in personas_data:
                persona = PersonaSimuladaDB(**persona_data)
                session.add(persona)
            
            await session.commit()
            print(f"✅ {len(personas_data)} personas simuladas creadas exitosamente!")
            
            # Mostrar resumen
            print("\n📊 Resumen de personas creadas:")
            personas_count = len([p for p in personas_data if p["tipo_cliente"] == "persona"])
            empresas_count = len([p for p in personas_data if p["tipo_cliente"] == "empresa"])
            print(f"   - Personas individuales: {personas_count}")
            print(f"   - Empresas: {empresas_count}")
            print(f"   - Total: {len(personas_data)}")
            
        except Exception as e:
            print(f"❌ Error insertando personas: {e}")
            await session.rollback()
            raise
    
    print("\n🎉 ¡Proceso completado!")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 GENERADOR DE PERSONAS SIMULADAS")
    print("=" * 60)
    print()
    
    asyncio.run(poblar_base_de_datos())

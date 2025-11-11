"""
Rutas API para gestión de Personas Simuladas.
Permite asignar perfiles genéricos a usuarios no autenticados.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.persona_simulada import PersonaSimuladaDB, AsignacionPersonaDB

router = APIRouter(prefix="/personas", tags=["personas-simuladas"])


# ==================== HELPER FUNCTIONS ====================

def persona_to_dict(persona: PersonaSimuladaDB) -> Dict[str, Any]:
    """Convierte PersonaSimuladaDB a diccionario."""
    return {
        "id": persona.id,
        "nombre": persona.nombre,
        "apellido": persona.apellido,
        "edad": persona.edad,
        "fecha_nacimiento": persona.fecha_nacimiento.isoformat() if persona.fecha_nacimiento else None,
        "region": persona.region,
        "tipo_cliente": persona.tipo_cliente,
        "interes_principal": persona.interes_principal,
        "uso_previsto": persona.uso_previsto,
        "presupuesto": persona.presupuesto,
        "tiene_vehiculo_actual": persona.tiene_vehiculo_actual,
        "tamano_flota": persona.tamano_flota,
        "esquema_colores": persona.esquema_colores,
        "color_favorito": persona.color_favorito,
        "estilo_tipografia": persona.estilo_tipografia,
        "densidad_informacion": persona.densidad_informacion,
        "nivel_animaciones": persona.nivel_animaciones,
        "preferencia_layout": persona.preferencia_layout,
        "estilo_navegacion": persona.estilo_navegacion,
        "descripcion": persona.descripcion
    }


async def obtener_persona_aleatoria(db: AsyncSession) -> PersonaSimuladaDB:
    """Obtiene una persona simulada aleatoria de la base de datos."""
    # Query para obtener persona aleatoria
    query = select(PersonaSimuladaDB).where(
        PersonaSimuladaDB.es_activa == True
    ).order_by(func.random()).limit(1)
    
    result = await db.execute(query)
    persona = result.scalar_one_or_none()
    
    if not persona:
        raise HTTPException(
            status_code=404,
            detail="No hay personas simuladas disponibles. Ejecutar script de población."
        )
    
    return persona


async def obtener_o_crear_asignacion(
    session_id: str,
    db: AsyncSession,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> tuple[PersonaSimuladaDB, AsignacionPersonaDB, bool]:
    """
    Obtiene la asignación existente o crea una nueva.
    
    Returns:
        tuple: (persona, asignacion, es_nueva)
    """
    # Buscar asignación existente
    query = select(AsignacionPersonaDB).where(
        AsignacionPersonaDB.session_id == session_id
    )
    result = await db.execute(query)
    asignacion = result.scalar_one_or_none()
    
    if asignacion:
        # Actualizar last_seen_at y page_views
        asignacion.last_seen_at = datetime.utcnow()
        asignacion.page_views += 1
        await db.commit()
        await db.refresh(asignacion)
        
        # Obtener persona asociada
        query_persona = select(PersonaSimuladaDB).where(
            PersonaSimuladaDB.id == asignacion.persona_id
        )
        result_persona = await db.execute(query_persona)
        persona = result_persona.scalar_one()
        
        return persona, asignacion, False
    
    else:
        # Crear nueva asignación
        persona = await obtener_persona_aleatoria(db)
        
        nueva_asignacion = AsignacionPersonaDB(
            session_id=session_id,
            persona_id=persona.id,
            user_agent=user_agent,
            ip_address=ip_address,
            page_views=1
        )
        
        db.add(nueva_asignacion)
        await db.commit()
        await db.refresh(nueva_asignacion)
        
        return persona, nueva_asignacion, True


def extraer_session_id(request: Request, x_session_id: Optional[str] = None) -> str:
    """Extrae o genera un session_id para el usuario."""
    # Prioridad:
    # 1. Header X-Session-ID (enviado por frontend)
    # 2. Cookie de sesión
    # 3. Generar nuevo UUID
    
    if x_session_id:
        return x_session_id
    
    # Intentar obtener de cookies
    session_id_cookie = request.cookies.get("session_id")
    if session_id_cookie:
        return session_id_cookie
    
    # Generar nuevo
    return str(uuid.uuid4())


# ==================== ENDPOINTS ====================

@router.post("/assign")
async def asignar_persona(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Asigna una persona simulada a un session_id.
    
    Si el session_id ya tiene una persona asignada, retorna esa misma.
    Si no, asigna una persona aleatoria y la persiste.
    
    Headers opcionales:
        X-Session-ID: ID de sesión del cliente (generado por frontend)
    
    Returns:
        {
            "persona": {...},
            "session_id": "...",
            "is_new_assignment": bool,
            "assignment_info": {...}
        }
    """
    try:
        # Extraer o generar session_id
        session_id = extraer_session_id(request, x_session_id)
        
        # Obtener info del cliente
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None
        
        # Obtener o crear asignación
        persona, asignacion, es_nueva = await obtener_o_crear_asignacion(
            session_id=session_id,
            db=db,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        return {
            "success": True,
            "persona": persona_to_dict(persona),
            "session_id": session_id,
            "is_new_assignment": es_nueva,
            "assignment_info": {
                "assigned_at": asignacion.assigned_at.isoformat(),
                "last_seen_at": asignacion.last_seen_at.isoformat(),
                "page_views": asignacion.page_views
            },
            "message": "Nueva persona asignada" if es_nueva else "Persona existente recuperada"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Error asignando persona: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al asignar persona: {str(e)}"
        )


@router.get("/me")
async def obtener_mi_persona(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Obtiene la persona simulada asignada al session_id actual.
    
    Si no existe asignación, retorna 404 (el cliente debe llamar a /assign primero).
    
    Headers opcionales:
        X-Session-ID: ID de sesión del cliente
    
    Returns:
        {
            "persona": {...},
            "session_id": "...",
            "assignment_info": {...}
        }
    """
    try:
        # Extraer session_id
        session_id = extraer_session_id(request, x_session_id)
        
        # Buscar asignación
        query = select(AsignacionPersonaDB).where(
            AsignacionPersonaDB.session_id == session_id
        )
        result = await db.execute(query)
        asignacion = result.scalar_one_or_none()
        
        if not asignacion:
            raise HTTPException(
                status_code=404,
                detail="No hay persona asignada para este session_id. Llamar a POST /assign primero."
            )
        
        # Actualizar last_seen
        asignacion.last_seen_at = datetime.utcnow()
        asignacion.page_views += 1
        await db.commit()
        
        # Obtener persona
        query_persona = select(PersonaSimuladaDB).where(
            PersonaSimuladaDB.id == asignacion.persona_id
        )
        result_persona = await db.execute(query_persona)
        persona = result_persona.scalar_one()
        
        return {
            "success": True,
            "persona": persona_to_dict(persona),
            "session_id": session_id,
            "assignment_info": {
                "assigned_at": asignacion.assigned_at.isoformat(),
                "last_seen_at": asignacion.last_seen_at.isoformat(),
                "page_views": asignacion.page_views
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Error obteniendo persona: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al obtener persona: {str(e)}"
        )


@router.get("/list")
async def listar_personas(
    db: AsyncSession = Depends(get_db),
    tipo_cliente: Optional[str] = None,
    limit: int = 50
):
    """
    Lista todas las personas simuladas disponibles.
    
    Query params:
        tipo_cliente: Filtrar por 'persona' o 'empresa'
        limit: Número máximo de resultados (default: 50)
    
    Returns:
        {
            "personas": [...],
            "total": int
        }
    """
    try:
        query = select(PersonaSimuladaDB).where(
            PersonaSimuladaDB.es_activa == True
        )
        
        if tipo_cliente:
            query = query.where(PersonaSimuladaDB.tipo_cliente == tipo_cliente)
        
        query = query.limit(limit)
        
        result = await db.execute(query)
        personas = result.scalars().all()
        
        return {
            "success": True,
            "personas": [persona_to_dict(p) for p in personas],
            "total": len(personas),
            "filters": {
                "tipo_cliente": tipo_cliente,
                "limit": limit
            }
        }
        
    except Exception as e:
        print(f"[ERROR] Error listando personas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al listar personas: {str(e)}"
        )


@router.get("/stats")
async def obtener_estadisticas(db: AsyncSession = Depends(get_db)):
    """
    Obtiene estadísticas sobre las personas simuladas y asignaciones.
    
    Returns:
        {
            "total_personas": int,
            "total_asignaciones": int,
            "personas_por_tipo": {...},
            "asignaciones_activas": int
        }
    """
    try:
        # Total personas
        query_personas = select(func.count()).select_from(PersonaSimuladaDB).where(
            PersonaSimuladaDB.es_activa == True
        )
        result_personas = await db.execute(query_personas)
        total_personas = result_personas.scalar()
        
        # Personas por tipo
        query_personas_tipo = select(
            PersonaSimuladaDB.tipo_cliente,
            func.count(PersonaSimuladaDB.id)
        ).where(
            PersonaSimuladaDB.es_activa == True
        ).group_by(PersonaSimuladaDB.tipo_cliente)
        result_tipo = await db.execute(query_personas_tipo)
        personas_por_tipo = dict(result_tipo.all())
        
        # Total asignaciones
        query_asignaciones = select(func.count()).select_from(AsignacionPersonaDB)
        result_asignaciones = await db.execute(query_asignaciones)
        total_asignaciones = result_asignaciones.scalar()
        
        # Asignaciones activas (vistas en últimas 24h)
        hace_24h = datetime.utcnow() - timedelta(hours=24)
        query_activas = select(func.count()).select_from(AsignacionPersonaDB).where(
            AsignacionPersonaDB.last_seen_at >= hace_24h
        )
        result_activas = await db.execute(query_activas)
        asignaciones_activas = result_activas.scalar()
        
        return {
            "success": True,
            "stats": {
                "total_personas": total_personas,
                "total_asignaciones": total_asignaciones,
                "personas_por_tipo": personas_por_tipo,
                "asignaciones_activas_24h": asignaciones_activas,
                "tasa_asignacion": f"{(asignaciones_activas / total_personas * 100):.1f}%" if total_personas > 0 else "0%"
            }
        }
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al obtener estadísticas: {str(e)}"
        )


# Importar timedelta si no está
from datetime import timedelta

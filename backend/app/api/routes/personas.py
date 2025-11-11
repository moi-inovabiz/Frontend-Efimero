"""
Rutas API para gestión de Personas Simuladas.
Permite asignar perfiles genéricos a usuarios no autenticados.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
import random

from app.core.database import get_db
from app.models.persona_simulada import PersonaSimuladaDB, AsignacionPersonaDB

router = APIRouter(prefix="/personas", tags=["personas-simuladas"])


# ==================== MODELOS PYDANTIC ====================

class ContextoAsignacion(BaseModel):
    """Contexto del usuario para matching inteligente de persona."""
    # Temporal
    hora_del_dia: Optional[int] = None  # 0-23
    es_fin_de_semana: Optional[bool] = None
    
    # Ubicación
    ciudad: Optional[str] = None
    region: Optional[str] = None
    pais: Optional[str] = None
    
    # Dispositivo
    es_movil: Optional[bool] = None
    es_tablet: Optional[bool] = None
    sistema_operativo: Optional[str] = None
    
    # Red
    tipo_conexion: Optional[str] = None  # wifi, 4g, 3g, etc.


# ==================== HELPER FUNCTIONS ====================

def calcular_score_persona(persona: PersonaSimuladaDB, contexto: Optional[ContextoAsignacion] = None) -> float:
    """
    Calcula un score para determinar qué tan bien matchea una persona con el contexto del usuario.
    Mayor score = mejor match.
    
    Args:
        persona: Persona simulada a evaluar
        contexto: Contexto del usuario (opcional, si no hay contexto usa scoring aleatorio)
    
    Returns:
        float: Score de matching (0-100)
    """
    if not contexto:
        # Sin contexto, retornar score puramente aleatorio
        return random.uniform(0, 100)
    
    score = 0.0
    
    # ===== REGIÓN (Peso: 25 puntos) =====
    if contexto.region and persona.region:
        # Match exacto de región
        if contexto.region.lower() in persona.region.lower() or persona.region.lower() in contexto.region.lower():
            score += 25
        # Match parcial por país
        elif contexto.pais and "chile" in contexto.pais.lower():
            score += 10  # Cualquier región chilena tiene bonus
    
    # ===== DISPOSITIVO + EDAD (Peso: 20 puntos) =====
    if persona.edad:
        if contexto.es_movil:
            # Móviles prefieren personas jóvenes
            if persona.edad < 35:
                score += 20
            elif persona.edad < 50:
                score += 10
        elif contexto.es_tablet:
            # Tablets para rango medio
            if 30 <= persona.edad <= 60:
                score += 20
            else:
                score += 10
        else:
            # Desktop para todas las edades, bonus para empresas y mayores
            if persona.tipo_cliente == "empresa":
                score += 20
            elif persona.edad >= 40:
                score += 15
            else:
                score += 10
    
    # ===== HORARIO + TIPO DE CLIENTE (Peso: 20 puntos) =====
    if contexto.hora_del_dia is not None:
        if 9 <= contexto.hora_del_dia <= 18:
            # Horario laboral: preferir empresas
            if persona.tipo_cliente == "empresa":
                score += 20
            else:
                score += 8
        else:
            # Fuera de horario laboral: preferir personas individuales
            if persona.tipo_cliente == "persona":
                score += 20
            else:
                score += 8
    
    # ===== FIN DE SEMANA (Peso: 10 puntos) =====
    if contexto.es_fin_de_semana is not None:
        if contexto.es_fin_de_semana:
            # Fin de semana: preferir personas individuales
            if persona.tipo_cliente == "persona":
                score += 10
        else:
            # Entre semana: ligera preferencia por empresas
            if persona.tipo_cliente == "empresa":
                score += 10
            else:
                score += 5
    
    # ===== CONEXIÓN + PREFERENCIAS VISUALES (Peso: 10 puntos) =====
    if contexto.tipo_conexion:
        conexion_lenta = contexto.tipo_conexion.lower() in ["3g", "2g", "slow-2g"]
        
        if conexion_lenta:
            # Conexión lenta: preferir animaciones bajas, densidad compacta
            if persona.nivel_animaciones == "bajo":
                score += 5
            if persona.densidad_informacion == "compacta":
                score += 5
        else:
            # Conexión rápida: cualquier configuración está bien
            score += 5
    
    # ===== COMPONENTE ALEATORIO (Peso: 15 puntos) =====
    # Mantener diversidad y evitar asignaciones 100% predecibles
    score += random.uniform(0, 15)
    
    return score


async def obtener_persona_con_matching(
    db: AsyncSession, 
    contexto: Optional[ContextoAsignacion] = None
) -> PersonaSimuladaDB:
    """
    Obtiene una persona simulada usando matching inteligente basado en contexto.
    
    Args:
        db: Sesión de base de datos
        contexto: Contexto del usuario para matching
    
    Returns:
        PersonaSimuladaDB: Persona seleccionada con mejor score
    """
    # Obtener todas las personas activas
    query = select(PersonaSimuladaDB).where(
        PersonaSimuladaDB.es_activa == True
    )
    result = await db.execute(query)
    personas = result.scalars().all()
    
    if not personas:
        raise HTTPException(
            status_code=404,
            detail="No hay personas simuladas disponibles. Ejecutar script de población."
        )
    
    # Calcular scores para cada persona
    personas_con_score = [
        (persona, calcular_score_persona(persona, contexto))
        for persona in personas
    ]
    
    # Ordenar por score (mayor a menor) y seleccionar la mejor
    personas_con_score.sort(key=lambda x: x[1], reverse=True)
    
    mejor_persona, mejor_score = personas_con_score[0]
    
    print(f"[MATCHING] Persona seleccionada: {mejor_persona.nombre} {mejor_persona.apellido} "
          f"(score: {mejor_score:.2f}, tipo: {mejor_persona.tipo_cliente}, edad: {mejor_persona.edad})")
    
    return mejor_persona


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


async def obtener_o_crear_asignacion(
    session_id: str,
    db: AsyncSession,
    contexto: Optional[ContextoAsignacion] = None,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> tuple[PersonaSimuladaDB, AsignacionPersonaDB, bool]:
    """
    Obtiene la asignación existente o crea una nueva con matching inteligente.
    
    Args:
        session_id: ID de sesión del usuario
        db: Sesión de base de datos
        contexto: Contexto del usuario para matching (opcional)
        user_agent: User agent del navegador
        ip_address: IP del cliente
    
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
        # Crear nueva asignación con matching inteligente
        persona = await obtener_persona_con_matching(db, contexto)
        
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
    contexto: Optional[ContextoAsignacion] = None,
    db: AsyncSession = Depends(get_db),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Asigna una persona simulada a un session_id usando matching inteligente.
    
    Si el session_id ya tiene una persona asignada, retorna esa misma.
    Si no, asigna una persona basándose en el contexto del usuario para mejor matching.
    
    Headers opcionales:
        X-Session-ID: ID de sesión del cliente (generado por frontend)
    
    Body opcional:
        contexto: Datos del usuario para matching inteligente (hora, región, dispositivo, etc.)
    
    Returns:
        {
            "persona": {...},
            "session_id": "...",
            "is_new_assignment": bool,
            "assignment_info": {...},
            "matching_score": float (solo si es nueva asignación)
        }
    """
    try:
        # Extraer o generar session_id
        session_id = extraer_session_id(request, x_session_id)
        
        # Obtener info del cliente
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None
        
        # Log del contexto recibido
        if contexto:
            print(f"[MATCHING] Contexto recibido: hora={contexto.hora_del_dia}, "
                  f"región={contexto.region}, móvil={contexto.es_movil}, "
                  f"fin_semana={contexto.es_fin_de_semana}")
        
        # Obtener o crear asignación con matching inteligente
        persona, asignacion, es_nueva = await obtener_o_crear_asignacion(
            session_id=session_id,
            db=db,
            contexto=contexto,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        response = {
            "success": True,
            "persona": persona_to_dict(persona),
            "session_id": session_id,
            "is_new_assignment": es_nueva,
            "assignment_info": {
                "assigned_at": asignacion.assigned_at.isoformat(),
                "last_seen_at": asignacion.last_seen_at.isoformat(),
                "page_views": asignacion.page_views
            },
            "message": "Nueva persona asignada con matching inteligente" if es_nueva else "Persona existente recuperada"
        }
        
        # Si es nueva asignación, incluir el score de matching
        if es_nueva and contexto:
            score = calcular_score_persona(persona, contexto)
            response["matching_score"] = round(score, 2)
            response["matching_info"] = {
                "used_context": True,
                "context_fields": {
                    "hora": contexto.hora_del_dia,
                    "region": contexto.region,
                    "dispositivo": "móvil" if contexto.es_movil else "tablet" if contexto.es_tablet else "desktop",
                    "fin_semana": contexto.es_fin_de_semana
                }
            }
        elif es_nueva:
            response["matching_info"] = {
                "used_context": False,
                "note": "Asignación aleatoria (sin contexto)"
            }
        
        return response
        
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


@router.post("/assign/{persona_id}")
async def asignar_persona_especifica(
    persona_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Asigna una persona simulada específica a un session_id.
    Útil para demos y testing de diferentes perfiles.
    
    Args:
        persona_id: ID de la persona a asignar
        
    Headers opcionales:
        X-Session-ID: ID de sesión del cliente
    
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
        
        # Buscar la persona específica
        query = select(PersonaSimuladaDB).where(
            PersonaSimuladaDB.id == persona_id,
            PersonaSimuladaDB.es_activa == True
        )
        result = await db.execute(query)
        persona = result.scalar_one_or_none()
        
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"Persona con ID {persona_id} no encontrada"
            )
        
        # Obtener info del cliente
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None
        
        # Verificar si ya existe asignación para este session_id
        query_asignacion = select(AsignacionPersonaDB).where(
            AsignacionPersonaDB.session_id == session_id
        )
        result_asignacion = await db.execute(query_asignacion)
        asignacion_existente = result_asignacion.scalar_one_or_none()
        
        es_nueva = False
        
        if asignacion_existente:
            # Actualizar asignación existente con la nueva persona
            asignacion_existente.persona_id = persona_id
            asignacion_existente.last_seen_at = datetime.utcnow()
            asignacion_existente.page_views += 1
            asignacion = asignacion_existente
            print(f"[MANUAL] Asignación actualizada: {session_id} → {persona.nombre} {persona.apellido}")
        else:
            # Crear nueva asignación
            asignacion = AsignacionPersonaDB(
                session_id=session_id,
                persona_id=persona_id,
                user_agent=user_agent,
                ip_address=ip_address
            )
            db.add(asignacion)
            es_nueva = True
            print(f"[MANUAL] Nueva asignación: {session_id} → {persona.nombre} {persona.apellido}")
        
        await db.commit()
        await db.refresh(asignacion)
        
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
            "message": "Persona asignada manualmente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Error asignando persona específica: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al asignar persona: {str(e)}"
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

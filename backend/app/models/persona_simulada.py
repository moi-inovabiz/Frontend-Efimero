"""
Modelos de Personas Simuladas y Asignaciones
Para proveer perfiles genéricos a usuarios no autenticados
"""

from sqlalchemy import Column, String, Integer, Date, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class PersonaSimuladaDB(Base):
    """
    Persona simulada con datos demográficos genéricos.
    Se asigna aleatoriamente a usuarios no autenticados para mantener UI consistente.
    """
    __tablename__ = "personas_simuladas"
    
    # Identificación
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    
    # Datos demográficos
    edad = Column(Integer, nullable=False)
    fecha_nacimiento = Column(Date, nullable=True)
    region = Column(String, nullable=False)
    tipo_cliente = Column(String, nullable=False)  # 'persona' o 'empresa'
    
    # Datos de perfil automotriz
    interes_principal = Column(String, nullable=True)  # 'compra', 'arriendo', 'comparacion'
    uso_previsto = Column(String, nullable=True)  # 'personal', 'comercial', 'familiar'
    presupuesto = Column(String, nullable=True)  # 'bajo', 'medio', 'alto', 'premium'
    tiene_vehiculo_actual = Column(Boolean, default=False)
    tamano_flota = Column(Integer, nullable=True)
    
    # Preferencias visuales (predichas o predefinidas)
    esquema_colores = Column(String, nullable=True)
    color_favorito = Column(String, nullable=True)
    estilo_tipografia = Column(String, nullable=True)
    densidad_informacion = Column(String, nullable=True)
    nivel_animaciones = Column(String, nullable=True)
    preferencia_layout = Column(String, nullable=True)
    estilo_navegacion = Column(String, nullable=True)
    
    # Metadata
    descripcion = Column(String, nullable=True)  # Descripción breve del perfil
    es_activa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con asignaciones
    asignaciones = relationship("AsignacionPersonaDB", back_populates="persona")


class AsignacionPersonaDB(Base):
    """
    Asignación de una Persona Simulada a un session_id específico.
    Permite mantener consistencia de UI para usuarios no autenticados.
    """
    __tablename__ = "asignaciones_personas"
    
    # Identificación
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, unique=True, nullable=False, index=True)  # ID único de sesión del usuario
    
    # Referencia a persona
    persona_id = Column(String, ForeignKey("personas_simuladas.id"), nullable=False)
    persona = relationship("PersonaSimuladaDB", back_populates="asignaciones")
    
    # Metadata de asignación
    assigned_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    page_views = Column(Integer, default=0)
    
    # Info del cliente
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

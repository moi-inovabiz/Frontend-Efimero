"""
SQLAlchemy database models for users
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON, Index
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


def generate_uuid():
    """Generate UUID as string."""
    return str(uuid.uuid4())


class UsuarioDB(Base):
    """
    Tabla de usuarios con autenticación y perfil completo.
    Incluye:
    - Autenticación (email, password)
    - Perfil Kaufmann (15 campos)
    - Preferencias visuales (12 campos)
    """
    
    __tablename__ = "usuarios"
    
    # Authentication fields
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Basic profile
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    rut = Column(String, unique=True, nullable=False, index=True)  # Chile RUT
    telefono = Column(String, nullable=True)
    
    # Kaufmann automotive profile (15 campos)
    tipo_cliente = Column(String, nullable=False, index=True)  # "persona" | "empresa"
    fecha_nacimiento = Column(String, nullable=True)  # ISO date string (persona)
    tamano_flota = Column(Integer, nullable=True)  # Fleet size (empresa)
    region = Column(String, nullable=False, index=True)  # Chilean region
    interes_principal = Column(JSON, nullable=True)  # Array: ["autos_lujo", "suvs", ...]
    uso_previsto = Column(String, nullable=True)  # "personal" | "ejecutivo" | "transporte" | etc.
    presupuesto = Column(String, nullable=True)  # "<30M" | "30-60M" | etc.
    tiene_vehiculo_actual = Column(Boolean, default=False)
    
    # Visual preferences (12 campos)
    esquema_colores = Column(String, default="automatico")  # "claro_elegante" | "oscuro_premium" | etc.
    color_favorito = Column(String, default="azul")  # "azul" | "rojo" | "plateado" | etc.
    estilo_tipografia = Column(String, default="moderna_geometrica")
    densidad_informacion = Column(String, default="comoda")  # "minimalista" | "comoda" | "compacta" | "maxima"
    estilo_imagenes = Column(String, default="fotograficas_realistas")
    nivel_animaciones = Column(String, default="moderadas")  # "ninguna" | "sutiles" | "moderadas" | "dinamicas"
    preferencia_layout = Column(String, default="grilla_cards")
    estilo_navegacion = Column(String, default="menu_tradicional")
    preferencia_visual = Column(String, default="iconos_con_labels")
    prioridades_info = Column(JSON, nullable=True)  # {"precio": 1, "consumo": 2, ...}
    modo_comparacion = Column(String, default="lado_a_lado")
    idioma_specs = Column(String, default="espanol_simple")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_tipo_cliente_region', 'tipo_cliente', 'region'),
        Index('idx_email_active', 'email', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email}, tipo_cliente={self.tipo_cliente})>"

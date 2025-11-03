"""
Modelos Pydantic para usuarios y autenticación
API schemas para validación y serialización
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class TipoCliente(str, Enum):
    """Tipo de cliente Kaufmann."""
    PERSONA = "persona"
    EMPRESA = "empresa"


class EsquemaColores(str, Enum):
    """Esquemas de colores disponibles."""
    AUTOMATICO = "automatico"
    CLARO = "claro"
    OSCURO = "oscuro"
    ALTO_CONTRASTE = "alto_contraste"
    LUJO = "lujo"
    CORPORATIVO = "corporativo"
    MODERNO = "moderno"


class ColorFavorito(str, Enum):
    """Colores favoritos."""
    AZUL = "azul"
    VERDE = "verde"
    ROJO = "rojo"
    AMARILLO = "amarillo"
    MORADO = "morado"
    ROSA = "rosa"
    CYAN = "cyan"
    NARANJA = "naranja"


class DensidadInformacion(str, Enum):
    """Niveles de densidad de información."""
    MINIMALISTA = "minimalista"
    COMODA = "comoda"
    COMPACTA = "compacta"
    MAXIMA = "maxima"


class NivelAnimaciones(str, Enum):
    """Niveles de animaciones."""
    NINGUNA = "ninguna"
    SUTILES = "sutiles"
    MODERADAS = "moderadas"
    DINAMICAS = "dinamicas"


# ==================== PYDANTIC MODELS ====================

class PrioridadesInfo(BaseModel):
    """Prioridades de información (ranking 1-5)."""
    precio: int = Field(ge=1, le=5)
    especificaciones: int = Field(ge=1, le=5)
    consumo: int = Field(ge=1, le=5)
    seguridad: int = Field(ge=1, le=5)
    tecnologia: int = Field(ge=1, le=5)


class VisualPreferences(BaseModel):
    """Preferencias visuales del usuario."""
    esquema_colores: EsquemaColores = EsquemaColores.AUTOMATICO
    color_favorito: ColorFavorito = ColorFavorito.AZUL
    estilo_tipografia: str = "moderna_geometrica"
    densidad_informacion: DensidadInformacion = DensidadInformacion.COMODA
    estilo_imagenes: str = "fotograficas_realistas"
    nivel_animaciones: NivelAnimaciones = NivelAnimaciones.MODERADAS
    preferencia_layout: str = "grilla_cards"
    estilo_navegacion: str = "menu_tradicional"
    preferencia_visual: str = "iconos_con_labels"
    prioridades_info: Optional[PrioridadesInfo] = None
    modo_comparacion: str = "lado_a_lado"
    idioma_specs: str = "espanol_simple"


class UsuarioBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=2, max_length=100)
    rut: str = Field(min_length=9, max_length=12)  # Format: XX.XXX.XXX-X
    telefono: Optional[str] = Field(None, max_length=20)
    tipo_cliente: TipoCliente
    
    # Profile fields
    fecha_nacimiento: Optional[str] = None  # ISO date (persona only)
    tamano_flota: Optional[int] = Field(None, ge=1, le=10000)  # empresa only
    region: str = Field(max_length=100)
    interes_principal: Optional[List[str]] = None
    uso_previsto: Optional[str] = None
    presupuesto: Optional[str] = None
    tiene_vehiculo_actual: bool = False
    
    @field_validator('rut')
    @classmethod
    def validate_rut_format(cls, v: str) -> str:
        """Validate RUT format (basic check, full validation in security.py)."""
        # Remove spaces
        v = v.strip()
        # Basic format check
        if not (9 <= len(v) <= 12):
            raise ValueError('RUT debe tener entre 9 y 12 caracteres')
        return v


class UsuarioCreate(UsuarioBase):
    """Schema for user registration."""
    password: str = Field(min_length=8, max_length=100)
    
    # Visual preferences (optional in registration)
    visual_preferences: Optional[VisualPreferences] = None
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UsuarioUpdate(BaseModel):
    """Schema for user profile update (partial)."""
    telefono: Optional[str] = None
    region: Optional[str] = None
    interes_principal: Optional[List[str]] = None
    uso_previsto: Optional[str] = None
    presupuesto: Optional[str] = None
    tiene_vehiculo_actual: Optional[bool] = None
    tamano_flota: Optional[int] = Field(None, ge=1, le=10000)


class UsuarioUpdateVisualPreferences(BaseModel):
    """Schema for updating visual preferences."""
    esquema_colores: Optional[EsquemaColores] = None
    color_favorito: Optional[ColorFavorito] = None
    estilo_tipografia: Optional[str] = None
    densidad_informacion: Optional[DensidadInformacion] = None
    estilo_imagenes: Optional[str] = None
    nivel_animaciones: Optional[NivelAnimaciones] = None
    preferencia_layout: Optional[str] = None
    estilo_navegacion: Optional[str] = None
    preferencia_visual: Optional[str] = None
    prioridades_info: Optional[PrioridadesInfo] = None
    modo_comparacion: Optional[str] = None
    idioma_specs: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    """Schema for user response (excludes password)."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Visual preferences
    esquema_colores: str
    color_favorito: str
    estilo_tipografia: str
    densidad_informacion: str
    estilo_imagenes: str
    nivel_animaciones: str
    preferencia_layout: str
    estilo_navegacion: str
    preferencia_visual: str
    prioridades_info: Optional[Dict] = None
    modo_comparacion: str
    idioma_specs: str
    
    class Config:
        from_attributes = True


class UsuarioInDB(UsuarioResponse):
    """Schema for user in database (includes hashed password)."""
    hashed_password: str


# ==================== AUTH SCHEMAS ====================

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """JWT token payload data."""
    user_id: str
    email: str
    tipo_cliente: str


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


# ==================== LEGACY MODELS (mantener para compatibilidad) ====================

class User(BaseModel):
    """Modelo de usuario (legacy - mantener para compatibilidad)."""
    
    user_id: str = Field(description="ID único del usuario")
    email: Optional[str] = None
    created_at: datetime
    last_login: datetime
    is_authenticated: bool = True
    
    # Zero-party data (configuraciones explícitas del usuario)
    preferences: Optional[dict] = None
    accessibility_settings: Optional[dict] = None


class AnonymousUser(BaseModel):
    """Usuario anónimo con tracking de primera parte."""
    
    user_temp_id: str = Field(description="ID temporal para usuarios anónimos")
    created_at: datetime
    last_seen: datetime
    session_count: int = 1
    is_authenticated: bool = False
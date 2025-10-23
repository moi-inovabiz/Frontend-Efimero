"""
Modelo de usuario y autenticación
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class User(BaseModel):
    """Modelo de usuario."""
    
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
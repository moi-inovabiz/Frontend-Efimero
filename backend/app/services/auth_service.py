"""
Servicio de autenticación
Maneja JWT y usuarios anónimos con cookies de primera parte
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import jwt
from jwt.exceptions import InvalidSignatureError, ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer
import uuid

from app.core.config import settings
from app.models.user import User, AnonymousUser

security = HTTPBearer(auto_error=False)


class AuthService:
    """
    Servicio de autenticación para Frontend Efímero.
    Soporta usuarios autenticados (JWT) y anónimos (cookies primera parte).
    """
    
    @staticmethod
    def create_access_token(user_data: Dict[str, Any]) -> str:
        """Crea un JWT para usuarios autenticados."""
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        to_encode = {
            **user_data,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verifica y decodifica un JWT."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
            
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except (InvalidSignatureError, InvalidTokenError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    
    
    @staticmethod
    def create_anonymous_user_id() -> str:
        """Crea un ID temporal para usuarios anónimos."""
        return f"anon_{uuid.uuid4().hex[:16]}"
    
    
    @staticmethod
    def get_user_from_request(request: Request) -> Dict[str, Any]:
        """
        Extrae información del usuario de la request.
        Soporta tanto JWT como cookies de primera parte.
        """
        # Intentar obtener JWT del header Authorization
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = AuthService.verify_token(token)
                return {
                    "user_id": payload.get("user_id"),
                    "email": payload.get("email"),
                    "is_authenticated": True,
                    "user_type": "authenticated"
                }
            except HTTPException:
                pass  # Fallback a usuario anónimo
        
        # Fallback: Usuario anónimo con cookie de primera parte
        user_temp_id = request.cookies.get("user_temp_id")
        if not user_temp_id:
            user_temp_id = AuthService.create_anonymous_user_id()
        
        return {
            "user_temp_id": user_temp_id,
            "is_authenticated": False,
            "user_type": "anonymous"
        }


def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency para obtener el usuario actual.
    Usado en los endpoints de FastAPI.
    """
    return AuthService.get_user_from_request(request)
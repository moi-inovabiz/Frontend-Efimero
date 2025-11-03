"""
FastAPI dependencies for authentication and database
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.security import decode_token
from app.models.db_models import UsuarioDB
from app.models.user import TokenData

# OAuth2 scheme for JWT authentication
# tokenUrl will be "/auth/login" when router is mounted
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UsuarioDB:
    """
    Dependency to get current authenticated user.
    
    Validates JWT token and retrieves user from database.
    Raises 401 if token is invalid or user not found.
    
    Usage:
        @router.get("/protected")
        async def protected_route(current_user: UsuarioDB = Depends(get_current_user)):
            return {"user_id": current_user.id}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    try:
        # Decode JWT token
        payload = decode_token(token)
        user_id: str = payload.get("user_id")
        
        if user_id is None:
            raise credentials_exception
        
        # Create token data
        token_data = TokenData(
            user_id=user_id,
            email=payload.get("email"),
            tipo_cliente=payload.get("tipo_cliente")
        )
        
    except ValueError:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(
        select(UsuarioDB).where(UsuarioDB.id == token_data.user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    return user


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[UsuarioDB]:
    """
    Dependency to get current user if authenticated, None otherwise.
    
    Does NOT raise exception if token is missing or invalid.
    Useful for endpoints that work for both authenticated and anonymous users.
    
    Usage:
        @router.post("/adaptive/recommendations")
        async def recommendations(
            context: UserContext,
            current_user: Optional[UsuarioDB] = Depends(get_optional_user)
        ):
            if current_user:
                # Use 80 features (45 automatic + 15 profile + 20 visual)
                pass
            else:
                # Use 45 automatic features only
                pass
    """
    if not token:
        return None
    
    try:
        # Decode JWT token
        payload = decode_token(token)
        user_id: str = payload.get("user_id")
        
        if user_id is None:
            return None
        
        # Get user from database
        result = await db.execute(
            select(UsuarioDB).where(UsuarioDB.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user and user.is_active:
            return user
        else:
            return None
            
    except Exception:
        # If any error occurs, just return None (fail silently)
        return None


async def get_current_active_user(
    current_user: UsuarioDB = Depends(get_current_user),
) -> UsuarioDB:
    """
    Dependency to ensure user is active.
    
    This is a convenience wrapper around get_current_user
    with explicit active user check.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user

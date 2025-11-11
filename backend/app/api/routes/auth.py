"""
Authentication routes: register, login, refresh, profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from typing import Dict, Any

from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    validate_rut,
    detect_tipo_cliente_from_rut,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.core.deps import get_current_user, get_current_active_user
from app.models.db_models import UsuarioDB
from app.models.user import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
    UsuarioUpdateVisualPreferences,
    Token,
    LoginRequest,
    RefreshTokenRequest,
    VisualPreferences
)

router = APIRouter(prefix="/auth", tags=["authentication"])


# ==================== HELPER FUNCTIONS ====================

def user_to_response(user: UsuarioDB) -> Dict[str, Any]:
    """Convert DB user model to response dict."""
    return {
        "id": user.id,
        "email": user.email,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "rut": user.rut,
        "telefono": user.telefono,
        "tipo_cliente": user.tipo_cliente,
        "fecha_nacimiento": user.fecha_nacimiento,
        "tamano_flota": user.tamano_flota,
        "region": user.region,
        "interes_principal": user.interes_principal,
        "uso_previsto": user.uso_previsto,
        "presupuesto": user.presupuesto,
        "tiene_vehiculo_actual": user.tiene_vehiculo_actual,
        "esquema_colores": user.esquema_colores,
        "color_favorito": user.color_favorito,
        "estilo_tipografia": user.estilo_tipografia,
        "densidad_informacion": user.densidad_informacion,
        "estilo_imagenes": user.estilo_imagenes,
        "nivel_animaciones": user.nivel_animaciones,
        "preferencia_layout": user.preferencia_layout,
        "estilo_navegacion": user.estilo_navegacion,
        "preferencia_visual": user.preferencia_visual,
        "prioridades_info": user.prioridades_info,
        "modo_comparacion": user.modo_comparacion,
        "idioma_specs": user.idioma_specs,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


# ==================== REGISTRATION ====================

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UsuarioCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new user with 3-step data collection.
    
    Steps:
    1. Basic data: email, password, nombre, apellido, RUT, telefono
    2. Profile data: tipo_cliente, region, interes_principal, uso_previsto, presupuesto
    3. Visual preferences: (optional) esquema_colores, color_favorito, densidad, etc.
    
    Returns JWT access token + refresh token on success.
    """
    
    try:
        # Log incoming data (without password)
        print(f"[REGISTER] Received registration data: {user_data.model_dump(exclude={'password'})}")
    except Exception as e:
        print(f"[REGISTER] Error logging data: {e}")
    
    # 1. Validate RUT
    if not validate_rut(user_data.rut):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="RUT inválido: dígito verificador incorrecto"
        )
    
    # 2. Check if email already exists
    result = await db.execute(
        select(UsuarioDB).where(UsuarioDB.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email ya registrado"
        )
    
    # 3. Check if RUT already exists
    result = await db.execute(
        select(UsuarioDB).where(UsuarioDB.rut == user_data.rut)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="RUT ya registrado"
        )
    
    # 4. Auto-detect tipo_cliente if not provided
    if not user_data.tipo_cliente:
        user_data.tipo_cliente = detect_tipo_cliente_from_rut(user_data.rut)
    
    # 5. Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # 6. Apply visual preferences defaults if not provided
    visual_prefs = user_data.visual_preferences or VisualPreferences()
    
    # 7. Create user in database
    new_user = UsuarioDB(
        email=user_data.email,
        hashed_password=hashed_password,
        nombre=user_data.nombre,
        apellido=user_data.apellido,
        rut=user_data.rut,
        telefono=user_data.telefono,
        tipo_cliente=user_data.tipo_cliente.value,
        fecha_nacimiento=user_data.fecha_nacimiento,
        tamano_flota=user_data.tamano_flota,
        region=user_data.region,
        interes_principal=user_data.interes_principal,
        uso_previsto=user_data.uso_previsto,
        presupuesto=user_data.presupuesto,
        tiene_vehiculo_actual=user_data.tiene_vehiculo_actual,
        # Visual preferences
        esquema_colores=visual_prefs.esquema_colores.value,
        color_favorito=visual_prefs.color_favorito.value,
        estilo_tipografia=visual_prefs.estilo_tipografia,
        densidad_informacion=visual_prefs.densidad_informacion.value,
        estilo_imagenes=visual_prefs.estilo_imagenes,
        nivel_animaciones=visual_prefs.nivel_animaciones.value,
        preferencia_layout=visual_prefs.preferencia_layout,
        estilo_navegacion=visual_prefs.estilo_navegacion,
        preferencia_visual=visual_prefs.preferencia_visual,
        prioridades_info=visual_prefs.prioridades_info.dict() if visual_prefs.prioridades_info else None,
        modo_comparacion=visual_prefs.modo_comparacion,
        idioma_specs=visual_prefs.idioma_specs,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # 8. Create JWT tokens
    access_token = create_access_token(
        data={
            "user_id": new_user.id,
            "email": new_user.email,
            "tipo_cliente": new_user.tipo_cliente
        }
    )
    refresh_token = create_refresh_token(new_user.id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )


# ==================== LOGIN ====================

@router.post("/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user with email and password.
    
    Returns JWT access token + refresh token on success.
    """
    
    # 1. Find user by email
    result = await db.execute(
        select(UsuarioDB).where(UsuarioDB.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    # 2. Verify password
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # 4. Create JWT tokens
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "tipo_cliente": user.tipo_cliente
        }
    )
    refresh_token = create_refresh_token(user.id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


# ==================== TOKEN REFRESH ====================

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Refresh tokens have longer expiration (30 days).
    """
    
    try:
        # 1. Decode refresh token
        payload = decode_token(refresh_data.refresh_token)
        
        # 2. Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")
        
        user_id: str = payload.get("user_id")
        if not user_id:
            raise ValueError("Missing user_id")
        
        # 3. Get user from database
        result = await db.execute(
            select(UsuarioDB).where(UsuarioDB.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        # 4. Create new access token
        access_token = create_access_token(
            data={
                "user_id": user.id,
                "email": user.email,
                "tipo_cliente": user.tipo_cliente
            }
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_data.refresh_token,  # Same refresh token
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de actualización inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ==================== GET CURRENT USER ====================

@router.get("/me", response_model=UsuarioResponse)
async def get_me(
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    """
    Get current authenticated user profile.
    
    Requires valid JWT token in Authorization header.
    """
    return user_to_response(current_user)


# ==================== UPDATE PROFILE ====================

@router.put("/me", response_model=UsuarioResponse)
async def update_profile(
    updates: UsuarioUpdate,
    current_user: UsuarioDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user profile (partial update).
    
    Immutable fields: email, rut, tipo_cliente
    Mutable fields: telefono, region, interes_principal, uso_previsto, presupuesto, etc.
    """
    
    # Apply updates (only non-None fields)
    update_data = updates.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return user_to_response(current_user)


# ==================== UPDATE VISUAL PREFERENCES ====================

@router.put("/me/visual-preferences", response_model=UsuarioResponse)
async def update_visual_preferences(
    preferences: UsuarioUpdateVisualPreferences,
    current_user: UsuarioDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user visual preferences.
    
    This endpoint allows changing UI theme, colors, typography, density, etc.
    Changes are applied immediately in the frontend.
    """
    
    # Apply updates (only non-None fields)
    update_data = preferences.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        # Convert enums to values
        if hasattr(value, 'value'):
            value = value.value
        # Convert nested Pydantic models to dicts
        elif isinstance(value, dict) or hasattr(value, 'dict'):
            if hasattr(value, 'dict'):
                value = value.dict()
        
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return user_to_response(current_user)


# ==================== AI PREDICTIONS ====================

@router.post("/predict-preferences")
async def predict_visual_preferences(
    demographic_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Predice preferencias visuales basadas en datos demográficos del usuario.
    
    Este endpoint utiliza el sistema de ML para generar predicciones de:
    - Densidad de información
    - Estilo de tipografía
    - Nivel de animaciones
    - Esquema de colores
    - Y otras preferencias visuales
    
    Args:
        demographic_data: Dict con datos demográficos (edad, región, tipo_cliente, etc.)
    
    Returns:
        Dict con preferencias visuales predichas y nivel de confianza
    """
    from app.ml.model_manager import ModelManager
    from app.ml.feature_processor import FeatureProcessor
    from app.models.adaptive_ui import UserContext
    from datetime import datetime
    import numpy as np
    
    try:
        # Extraer datos demográficos
        fecha_nacimiento = demographic_data.get('fecha_nacimiento')
        region = demographic_data.get('region', 'Metropolitana')
        tipo_cliente = demographic_data.get('tipo_cliente', 'persona')
        interes_principal = demographic_data.get('interes_principal', 'compra')
        uso_previsto = demographic_data.get('uso_previsto', 'personal')
        presupuesto = demographic_data.get('presupuesto', 'medio')
        
        # Calcular edad si hay fecha de nacimiento
        edad = None
        if fecha_nacimiento:
            try:
                if isinstance(fecha_nacimiento, str):
                    fecha_nac = datetime.fromisoformat(fecha_nacimiento.replace('Z', '+00:00'))
                else:
                    fecha_nac = fecha_nacimiento
                edad = (datetime.now() - fecha_nac).days // 365
            except Exception as e:
                print(f"[PREDICT] Error calculando edad: {e}")
                edad = 30  # Valor por defecto
        else:
            edad = 30  # Valor por defecto si no hay fecha
        
        # Crear contexto de usuario simulado basado en datos demográficos
        user_context = UserContext(
            hora_local=datetime.now(),
            prefers_color_scheme='light',  # Por defecto
            viewport_width=1920,
            viewport_height=1080,
            touch_enabled=False,
            device_pixel_ratio=1.0,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            session_id=f"prediction_{datetime.now().timestamp()}",
            page_path="/register",
            referer=None
        )
        
        # Preparar features usando FeatureProcessor
        feature_processor = FeatureProcessor()
        
        # Crear datos históricos simulados basados en demografía
        historical_data = []
        social_context = {
            'avg_session_duration': 300.0,
            'popular_preferences': {
                'color_scheme': 'light',
                'density': 'medium'
            }
        }
        
        # Generar features
        features = feature_processor.prepare_features_v2(
            user_context=user_context,
            historical_data=historical_data,
            social_context=social_context,
            is_authenticated=False
        )
        
        # PREDICCIÓN CON ML
        # Asegurarse de que los modelos estén cargados
        if not ModelManager._is_loaded:
            await ModelManager.load_models()
        
        # Hacer predicción dual
        prediction_result = ModelManager.predict_dual(
            user_context=user_context,
            historical_data=historical_data,
            social_context=social_context,
            is_authenticated=False
        )
        
        # Mapear predicciones a preferencias específicas del usuario
        css_classes = prediction_result["css_classes"]
        css_variables = prediction_result["css_variables"]
        confidence = prediction_result["confidence"]
        
        # Extraer preferencias específicas de las clases CSS
        preferencias_predichas = {
            # Densidad de información
            "densidad_informacion": _extract_density_preference(css_classes),
            
            # Estilo de tipografía
            "estilo_tipografia": _extract_typography_preference(css_classes),
            
            # Nivel de animaciones
            "nivel_animaciones": _extract_animation_level(css_classes, edad),
            
            # Esquema de colores
            "esquema_colores": _extract_color_scheme(css_classes),
            
            # Layout preferido
            "preferencia_layout": _extract_layout_preference(tipo_cliente, presupuesto),
            
            # Estilo de navegación
            "estilo_navegacion": _extract_navigation_style(edad, tipo_cliente),
            
            # Variables CSS predichas
            "css_variables": css_variables,
            
            # Información adicional
            "metadata": {
                "edad_estimada": edad,
                "region": region,
                "tipo_cliente": tipo_cliente,
                "interes_principal": interes_principal
            }
        }
        
        return {
            "success": True,
            "predictions": preferencias_predichas,
            "confidence": {
                "overall_score": confidence["combined"]["score"],
                "overall_quality": confidence["combined"]["quality"],
                "classifier_confidence": confidence["classifier"]["score"],
                "regressor_confidence": confidence["regressor"]["score"],
                "reliability": confidence["combined"]["breakdown"]
            },
            "raw_predictions": {
                "css_classes": css_classes,
                "css_variables": css_variables
            },
            "model_info": prediction_result["model_info"]
        }
        
    except Exception as e:
        print(f"[PREDICT] Error en predicción: {e}")
        import traceback
        traceback.print_exc()
        
        # Retornar predicciones por defecto en caso de error
        return {
            "success": False,
            "error": str(e),
            "predictions": _get_default_preferences(
                demographic_data.get('edad', 30),
                demographic_data.get('tipo_cliente', 'persona')
            ),
            "confidence": {
                "overall_score": 50.0,
                "overall_quality": "low",
                "classifier_confidence": 50.0,
                "regressor_confidence": 50.0,
                "reliability": {
                    "classification_contribution": 0.5,
                    "regression_contribution": 0.5,
                    "overall_certainty": "fallback"
                }
            }
        }


# ==================== HELPER FUNCTIONS FOR PREDICTIONS ====================

def _extract_density_preference(css_classes: list) -> str:
    """Extrae preferencia de densidad de las clases CSS."""
    for cls in css_classes:
        if 'densidad-alta' in cls or 'dense' in cls or 'compact' in cls:
            return 'compacta'
        elif 'densidad-baja' in cls or 'sparse' in cls or 'spacious' in cls:
            return 'espaciosa'
    return 'normal'


def _extract_typography_preference(css_classes: list) -> str:
    """Extrae preferencia de tipografía de las clases CSS."""
    for cls in css_classes:
        if 'fuente-serif' in cls or 'serif' in cls:
            return 'serif'
        elif 'fuente-mono' in cls or 'mono' in cls:
            return 'monospace'
    return 'sans-serif'


def _extract_animation_level(css_classes: list, edad: int) -> str:
    """Extrae nivel de animaciones considerando edad."""
    # Usuarios más jóvenes tienden a preferir más animaciones
    if edad < 25:
        base_level = 'alto'
    elif edad < 45:
        base_level = 'medio'
    else:
        base_level = 'bajo'
    
    # Ajustar basado en clases CSS
    for cls in css_classes:
        if 'animacion-alta' in cls or 'motion-high' in cls:
            return 'alto'
        elif 'animacion-baja' in cls or 'motion-low' in cls:
            return 'bajo'
    
    return base_level


def _extract_color_scheme(css_classes: list) -> str:
    """Extrae esquema de colores de las clases CSS."""
    for cls in css_classes:
        if 'modo-nocturno' in cls or 'dark' in cls:
            return 'dark'
        elif 'modo-auto' in cls or 'auto' in cls:
            return 'auto'
    return 'light'


def _extract_layout_preference(tipo_cliente: str, presupuesto: str) -> str:
    """Extrae preferencia de layout basada en tipo de cliente."""
    if tipo_cliente == 'empresa':
        return 'grid'  # Empresas prefieren ver más info
    elif presupuesto in ['alto', 'premium']:
        return 'cards'  # Usuarios premium prefieren cards elegantes
    return 'list'


def _extract_navigation_style(edad: int, tipo_cliente: str) -> str:
    """Extrae estilo de navegación basado en edad y tipo."""
    if edad < 30:
        return 'hamburger'  # Jóvenes familiarizados con mobile
    elif tipo_cliente == 'empresa':
        return 'sidebar'  # Empresas prefieren navegación completa
    return 'top'


def _get_default_preferences(edad: int, tipo_cliente: str) -> Dict[str, Any]:
    """Retorna preferencias por defecto basadas en demografía básica."""
    return {
        "densidad_informacion": "normal",
        "estilo_tipografia": "sans-serif",
        "nivel_animaciones": "medio" if edad < 45 else "bajo",
        "esquema_colores": "light",
        "preferencia_layout": "grid" if tipo_cliente == 'empresa' else "list",
        "estilo_navegacion": "hamburger" if edad < 30 else "top",
        "css_variables": {
            "--font-size-base": "1.000rem",
            "--spacing-factor": "1.000",
            "--color-primary-hue": "180",
            "--border-radius": "0.250rem",
            "--line-height": "1.400"
        },
        "metadata": {
            "edad_estimada": edad,
            "tipo_cliente": tipo_cliente,
            "source": "fallback"
        }
    }

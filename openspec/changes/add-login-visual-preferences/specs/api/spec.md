# API Specification - Delta

## ADDED Requirements

### Requirement: User Registration Endpoint
The system SHALL provide POST /auth/register endpoint for user registration.

#### Scenario: Registration Request
- **WHEN** POST /auth/register with valid data
  ```json
  {
    "email": "juan@example.com",
    "password": "SecurePass123!",
    "nombre": "Juan",
    "apellido": "Pérez",
    "rut": "12.345.678-5",
    "telefono": "+56912345678",
    "tipo_cliente": "persona",
    "fecha_nacimiento": "1985-03-15",
    "region": "Metropolitana",
    "interes_principal": ["autos_lujo", "suvs"],
    "uso_previsto": "ejecutivo",
    "presupuesto": "90-120M",
    "tiene_vehiculo_actual": true,
    "esquema_colores": "oscuro_premium",
    "color_favorito": "plateado",
    "densidad_informacion": "comoda",
    "prioridades_info": {
      "precio": 3,
      "tecnologia": 1,
      "seguridad": 2,
      "consumo": 4,
      "especificaciones": 5
    }
  }
  ```
- **THEN** system SHALL return 201 Created
- **AND** response body:
  ```json
  {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": "uuid",
      "email": "juan@example.com",
      "nombre": "Juan",
      "apellido": "Pérez",
      "tipo_cliente": "persona"
    }
  }
  ```

#### Scenario: Registration with Minimal Data (Skip Step 3)
- **WHEN** POST /auth/register with only basic + profile data (no visual preferences)
- **THEN** system SHALL use default visual preferences
- **AND** return 201 Created with tokens
- **AND** user record SHALL have esquema_colores="automatico", densidad_informacion="comoda", etc.

#### Scenario: Duplicate Email Error
- **WHEN** POST /auth/register with existing email
- **THEN** system SHALL return 409 Conflict
- **AND** response body:
  ```json
  {
    "detail": "Email ya registrado"
  }
  ```

#### Scenario: Invalid RUT Error
- **WHEN** POST /auth/register with invalid RUT check digit
- **THEN** system SHALL return 422 Unprocessable Entity
- **AND** response body:
  ```json
  {
    "detail": [
      {
        "loc": ["body", "rut"],
        "msg": "RUT inválido: dígito verificador incorrecto",
        "type": "value_error.rut"
      }
    ]
  }
  ```

### Requirement: User Login Endpoint
The system SHALL provide POST /auth/login endpoint for authentication.

#### Scenario: Login Success
- **WHEN** POST /auth/login
  ```json
  {
    "email": "juan@example.com",
    "password": "SecurePass123!"
  }
  ```
- **THEN** system SHALL return 200 OK
- **AND** response body:
  ```json
  {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 86400
  }
  ```

#### Scenario: Invalid Credentials Error
- **WHEN** POST /auth/login with wrong password
- **THEN** system SHALL return 401 Unauthorized
- **AND** response body:
  ```json
  {
    "detail": "Email o contraseña incorrectos"
  }
  ```
- **AND** SHALL NOT indicate which field is incorrect

### Requirement: Token Refresh Endpoint
The system SHALL provide POST /auth/refresh endpoint for token renewal.

#### Scenario: Token Refresh Success
- **WHEN** POST /auth/refresh
  ```json
  {
    "refresh_token": "eyJ..."
  }
  ```
- **THEN** system SHALL return 200 OK
- **AND** response body:
  ```json
  {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 86400
  }
  ```

#### Scenario: Invalid Refresh Token Error
- **WHEN** POST /auth/refresh with expired or invalid token
- **THEN** system SHALL return 401 Unauthorized
- **AND** response body:
  ```json
  {
    "detail": "Token de actualización inválido o expirado"
  }
  ```

### Requirement: Get Current User Endpoint
The system SHALL provide GET /auth/me endpoint to retrieve authenticated user profile.

#### Scenario: Get Profile Success
- **WHEN** GET /auth/me with valid Authorization: Bearer <token>
- **THEN** system SHALL return 200 OK
- **AND** response body:
  ```json
  {
    "id": "uuid",
    "email": "juan@example.com",
    "nombre": "Juan",
    "apellido": "Pérez",
    "rut": "12.345.678-5",
    "telefono": "+56912345678",
    "tipo_cliente": "persona",
    "fecha_nacimiento": "1985-03-15",
    "region": "Metropolitana",
    "interes_principal": ["autos_lujo", "suvs"],
    "uso_previsto": "ejecutivo",
    "presupuesto": "90-120M",
    "tiene_vehiculo_actual": true,
    "esquema_colores": "oscuro_premium",
    "color_favorito": "plateado",
    "densidad_informacion": "comoda",
    "prioridades_info": {
      "precio": 3,
      "tecnologia": 1,
      "seguridad": 2,
      "consumo": 4,
      "especificaciones": 5
    },
    "created_at": "2025-11-03T10:30:00Z",
    "updated_at": "2025-11-03T10:30:00Z"
  }
  ```
- **AND** SHALL NOT include hashed_password

#### Scenario: Unauthorized Access Error
- **WHEN** GET /auth/me without Authorization header
- **THEN** system SHALL return 401 Unauthorized
- **AND** response body:
  ```json
  {
    "detail": "No autenticado"
  }
  ```

### Requirement: Update User Profile Endpoint
The system SHALL provide PUT /auth/me endpoint to update user profile.

#### Scenario: Update Profile Success
- **WHEN** PUT /auth/me with Authorization header
  ```json
  {
    "telefono": "+56987654321",
    "region": "Valparaíso",
    "interes_principal": ["autos_lujo", "suvs", "electricos"],
    "presupuesto": "120-150M"
  }
  ```
- **THEN** system SHALL return 200 OK
- **AND** response body SHALL contain updated user profile
- **AND** updated_at timestamp SHALL be current time

#### Scenario: Immutable Field Update Rejection
- **WHEN** PUT /auth/me attempting to change email or rut
  ```json
  {
    "email": "newemail@example.com",
    "rut": "98.765.432-1"
  }
  ```
- **THEN** system SHALL return 422 Unprocessable Entity
- **AND** response body:
  ```json
  {
    "detail": "Los campos 'email' y 'rut' no pueden ser modificados"
  }
  ```

### Requirement: Update Visual Preferences Endpoint
The system SHALL provide PUT /auth/me/visual-preferences endpoint for theme customization.

#### Scenario: Update Visual Preferences Success
- **WHEN** PUT /auth/me/visual-preferences with Authorization header
  ```json
  {
    "esquema_colores": "claro_elegante",
    "color_favorito": "dorado",
    "densidad_informacion": "minimalista",
    "estilo_tipografia": "elegante_script",
    "nivel_animaciones": "sutiles",
    "prioridades_info": {
      "tecnologia": 1,
      "seguridad": 2,
      "precio": 3,
      "especificaciones": 4,
      "consumo": 5
    }
  }
  ```
- **THEN** system SHALL return 200 OK
- **AND** response body SHALL contain updated visual preferences
- **AND** updated_at timestamp SHALL be current time

---

## MODIFIED Requirements

### Requirement: Adaptive Recommendations Endpoint
The system SHALL support optional authentication for POST /adaptive/recommendations endpoint.

**Changes from previous version**:
- Now accepts optional Authorization: Bearer <token> header
- If authenticated, merges user profile + visual preferences with ephemeral context
- Response includes personalized recommendations based on 80 features instead of 45

#### Scenario: Authenticated Recommendations Request
- **WHEN** POST /adaptive/recommendations with Authorization header and UserContext
  ```json
  {
    "viewport_width": 1920,
    "viewport_height": 1080,
    "hora_local": "2025-11-03T14:30:00-03:00",
    "timezone": "America/Santiago",
    "is_touch": false,
    "color_scheme": "dark",
    "hardware_concurrency": 8,
    "connection_effective_type": "4g"
    // ... 37 more automatic fields
  }
  ```
- **THEN** system SHALL extract user_id from JWT token
- **AND** fetch user profile and visual preferences from database
- **AND** merge 45 automatic + 15 profile + 20 visual = 80 features
- **AND** pass to ML model (80-feature version)
- **AND** return personalized recommendations
- **AND** response includes user_segment field ("persona_lujo", "empresa_comercial", etc.)

#### Scenario: Anonymous Recommendations Request
- **WHEN** POST /adaptive/recommendations without Authorization header
- **THEN** system SHALL process 45 automatic features from UserContext
- **AND** use default values for profile and visual preference features
- **AND** pass 80-feature array (with defaults) to ML model
- **AND** return generic recommendations
- **AND** response includes user_segment field as "anonymous"

#### Scenario: Response Format (Authenticated)
- **WHEN** authenticated recommendations returned
- **THEN** response body SHALL include:
  ```json
  {
    "user_segment": "persona_lujo",
    "recommended_products": [
      {
        "id": "gle-450",
        "name": "Mercedes-Benz GLE 450",
        "confidence": 0.92,
        "reason": "Matches your interest in luxury SUVs and executive use"
      }
    ],
    "theme_suggestions": {
      "apply_user_preferences": true,
      "css_variables": {
        "--color-background": "#fafafa",
        "--color-accent": "#ffd700"
      }
    },
    "prediction_metadata": {
      "model_version": "v4",
      "features_used": 80,
      "processing_time_ms": 45
    }
  }
  ```

---

## REMOVED Requirements

None. All existing API requirements are preserved and extended.

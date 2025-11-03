# Authentication Specification - Delta

## ADDED Requirements

### Requirement: User Registration with 3-Step Wizard
The system SHALL provide user registration with email/password and a 3-step data collection wizard.

#### Scenario: Basic Registration Success
- **WHEN** user submits valid email, password, nombre, apellido, RUT, and teléfono
- **THEN** system SHALL create new user account with hashed password (bcrypt cost 12)
- **AND** return JWT access token (24-hour expiry) and refresh token (30-day expiry)
- **AND** detect tipo_cliente (persona/empresa) from RUT validation

#### Scenario: Duplicate Email Rejection
- **WHEN** user registers with existing email
- **THEN** system SHALL return 409 Conflict error
- **AND** message SHALL be "Email ya registrado"

#### Scenario: Invalid RUT Rejection
- **WHEN** user submits RUT that fails módulo 11 validation
- **THEN** system SHALL return 422 Validation Error
- **AND** message SHALL indicate "RUT inválido"

### Requirement: User Profile Data Collection
The system SHALL collect automotive-specific profile data for Kaufmann Mercedes-Benz personalization.

#### Scenario: Persona Natural Profile
- **WHEN** user with persona natural RUT completes profile
- **THEN** system SHALL collect fecha_nacimiento (age 18-100)
- **AND** collect región (15 Chilean regions)
- **AND** collect interés_principal (autos lujo, SUVs, vans, camiones, buses, eléctricos)
- **AND** collect uso_previsto (personal, ejecutivo)
- **AND** collect presupuesto (6 ranges: <$30M to >$150M)
- **AND** collect tiene_vehiculo_actual (boolean)

#### Scenario: Empresa Profile
- **WHEN** user with empresa RUT completes profile
- **THEN** system SHALL collect tamaño_flota (1-1000+ vehicles)
- **AND** collect región for business operations
- **AND** collect interés_principal focusing on commercial/heavy vehicles
- **AND** collect uso_previsto (transporte, minería, construcción, agrícola)
- **AND** collect presupuesto for fleet budget
- **AND** collect tiene_vehiculo_actual for trade-in detection

### Requirement: Visual Preferences Collection
The system SHALL collect 12 visual preference options to customize UI appearance.

#### Scenario: Visual Preferences Capture
- **WHEN** user completes visual preferences step (optional)
- **THEN** system SHALL collect esquema_colores (7 options: claro_elegante, oscuro_premium, alto_contraste, automatico, calido, frio, vibrante)
- **AND** collect color_favorito (9 colors: azul, rojo, verde, dorado, plateado, naranja, purpura, negro, blanco)
- **AND** collect estilo_tipografia (5 styles: moderna_geometrica, clasica_serif, tecnologica, elegante_script, bold_impactante)
- **AND** collect densidad_informacion (4 levels: minimalista, comoda, compacta, maxima)
- **AND** collect nivel_animaciones (4 levels: ninguna, sutiles, moderadas, dinamicas)
- **AND** collect preferencia_layout (4 types: lista_detallada, grilla_cards, carrusel_grande, tabla_comparativa)
- **AND** collect prioridades_info as JSON (precio, especificaciones, consumo, seguridad, tecnologia ranked 1-5)

#### Scenario: Skip Visual Preferences
- **WHEN** user clicks "Omitir" on visual preferences step
- **THEN** system SHALL use default preferences (automatico, moderna_geometrica, comoda, moderadas)
- **AND** complete registration successfully without visual customization

### Requirement: JWT Token Authentication
The system SHALL authenticate users using JWT access and refresh tokens.

#### Scenario: Login Success
- **WHEN** user submits valid email and password
- **THEN** system SHALL verify password with bcrypt
- **AND** return JWT access token with 24-hour expiration
- **AND** return refresh token with 30-day expiration
- **AND** access token payload SHALL include user_id, email, tipo_cliente

#### Scenario: Invalid Credentials
- **WHEN** user submits incorrect email or password
- **THEN** system SHALL return 401 Unauthorized
- **AND** message SHALL be "Email o contraseña incorrectos"
- **AND** SHALL NOT indicate which field is incorrect (security)

#### Scenario: Token Refresh
- **WHEN** valid refresh token is submitted
- **THEN** system SHALL generate new access token with fresh 24-hour expiry
- **AND** refresh token SHALL remain valid until its 30-day expiry
- **AND** return new access token in response

#### Scenario: Expired Token Rejection
- **WHEN** expired access token is used
- **THEN** system SHALL return 401 Unauthorized
- **AND** message SHALL be "Token expirado"
- **AND** client SHALL refresh token or prompt re-login

### Requirement: RUT Validation (Chile)
The system SHALL validate Chilean RUT using módulo 11 algorithm and detect customer type.

#### Scenario: Valid Persona Natural RUT
- **WHEN** RUT "12.345.678-5" is validated
- **THEN** system SHALL clean format (remove dots/hyphens)
- **AND** validate check digit using módulo 11
- **AND** detect tipo_cliente as "persona"
- **AND** accept registration

#### Scenario: Valid Empresa RUT
- **WHEN** RUT "76.123.456-K" is validated
- **THEN** system SHALL clean format
- **AND** validate check digit
- **AND** detect tipo_cliente as "empresa" (starts with 7x or 8x)
- **AND** accept registration

#### Scenario: Invalid Check Digit
- **WHEN** RUT "12.345.678-9" is submitted (wrong check digit)
- **THEN** system SHALL return validation error
- **AND** message SHALL be "RUT inválido: dígito verificador incorrecto"

### Requirement: Protected Profile Endpoints
The system SHALL provide authenticated endpoints for profile management.

#### Scenario: Get Current User Profile
- **WHEN** authenticated user requests GET /auth/me
- **THEN** system SHALL validate JWT token
- **AND** return user profile including basic data, profile data, and visual preferences
- **AND** exclude hashed_password from response

#### Scenario: Update Profile
- **WHEN** authenticated user submits PUT /auth/me with updated fields
- **THEN** system SHALL validate token
- **AND** update allowed fields (nombre, apellido, telefono, region, interes_principal, uso_previsto, presupuesto, tiene_vehiculo_actual)
- **AND** NOT allow updating email or RUT (immutable)
- **AND** return updated profile

#### Scenario: Update Visual Preferences
- **WHEN** authenticated user submits PUT /auth/me/visual-preferences
- **THEN** system SHALL validate token
- **AND** update visual preference fields
- **AND** return updated preferences
- **AND** client SHALL apply new CSS variables immediately

#### Scenario: Unauthorized Access
- **WHEN** request to protected endpoint without valid token
- **THEN** system SHALL return 401 Unauthorized
- **AND** message SHALL be "No autenticado"

---

## MODIFIED Requirements

### Requirement: Authentication Dependency Framework
The system SHALL provide get_current_user and get_optional_user dependencies for endpoint authentication.

**Changes from previous version**:
- Added `get_optional_user` dependency for endpoints supporting both authenticated and anonymous users
- Removed placeholder implementation, now uses real JWT validation with SECRET_KEY
- Added user profile and visual preferences to User model returned by dependencies

#### Scenario: JWT Token Processing (Production)
- **WHEN** get_current_user dependency is used
- **THEN** system SHALL validate JWT token using SECRET_KEY and HS256 algorithm
- **AND** extract user_id from token payload
- **AND** query database for full user profile (basic + profile + visual preferences)
- **AND** return Usuario model with all fields
- **AND** raise 401 Unauthorized if token invalid or expired

#### Scenario: Optional Authentication
- **WHEN** get_optional_user dependency is used
- **THEN** system SHALL validate JWT token if Authorization header present
- **AND** return Usuario model if valid token
- **AND** return None if no token or invalid token (without raising error)
- **AND** allow endpoint to handle both authenticated and anonymous flows

### Requirement: User Context Extraction
The system SHALL extract user context combining authentication state with ephemeral context.

**Changes from previous version**:
- UserContext model now includes optional user_id field linking to authenticated user
- Profile and visual preferences merged into context when user authenticated

#### Scenario: Authenticated User Context
- **WHEN** adaptive UI prediction requested with valid JWT token
- **THEN** system SHALL extract ephemeral context (45 automatic fields)
- **AND** extract user profile (tipo_cliente, region, interes_principal, uso_previsto, presupuesto, etc.)
- **AND** extract visual preferences (esquema_colores, color_favorito, densidad_informacion, etc.)
- **AND** merge into unified UserContext with user_id populated
- **AND** pass to ML feature processor for 80-feature prediction

#### Scenario: Anonymous User Context
- **WHEN** adaptive UI prediction requested without JWT token
- **THEN** system SHALL extract ephemeral context (45 automatic fields)
- **AND** user_id SHALL be None
- **AND** profile and visual preference fields SHALL be None
- **AND** ML feature processor SHALL use 45 features only

---

## REMOVED Requirements

None. All existing authentication requirements are preserved and extended.

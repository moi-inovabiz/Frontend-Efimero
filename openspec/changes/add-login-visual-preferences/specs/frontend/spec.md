# Frontend Specification - Delta

## ADDED Requirements

### Requirement: User Registration Wizard
The system SHALL provide a 3-step registration wizard with progress tracking and form validation.

#### Scenario: Step 1 - Basic Data Completion
- **WHEN** user fills email, nombre, apellido, RUT, teléfono in Step 1
- **THEN** form SHALL validate email format (RFC 5322)
- **AND** validate RUT with módulo 11 algorithm in real-time
- **AND** validate phone format for Chile (+569 XXXX XXXX)
- **AND** show validation errors inline below each field
- **AND** enable "Siguiente" button only when all fields valid
- **AND** auto-detect tipo_cliente from RUT and show badge

#### Scenario: Step 2 - Profile Completion (Persona)
- **WHEN** user with tipo_cliente="persona" reaches Step 2
- **THEN** form SHALL show fecha_nacimiento datepicker (age 18-100)
- **AND** show región dropdown with 15 Chilean regions
- **AND** show interés_principal multi-select (autos lujo, SUVs, vans, etc.)
- **AND** show uso_previsto radio (personal, ejecutivo)
- **AND** show presupuesto slider with 6 ranges
- **AND** show tiene_vehiculo_actual toggle
- **AND** "Atrás" button SHALL preserve Step 1 data

#### Scenario: Step 2 - Profile Completion (Empresa)
- **WHEN** user with tipo_cliente="empresa" reaches Step 2
- **THEN** form SHALL show tamaño_flota number input (1-1000+)
- **AND** show región for business location
- **AND** focus interés_principal on commercial vehicles (vans, camiones, buses)
- **AND** show uso_previsto radio (transporte, minería, construcción, agrícola)
- **AND** show presupuesto slider for fleet budget
- **AND** show tiene_vehiculo_actual for trade-in

#### Scenario: Step 3 - Visual Preferences Completion
- **WHEN** user reaches Step 3
- **THEN** form SHALL show esquema_colores as visual palette selector with 7 options
- **AND** show color_favorito as color swatch picker with 9 colors
- **AND** show densidad_informacion as slider (minimalista ← → máxima)
- **AND** show estilo_tipografia as radio with font previews
- **AND** show prioridades_info as drag-and-drop sorter (5 items)
- **AND** show "Omitir" button to skip and use defaults
- **AND** show "Finalizar" button to complete registration

#### Scenario: Visual Preferences Skip
- **WHEN** user clicks "Omitir" on Step 3
- **THEN** system SHALL apply default preferences (automatico, moderna_geometrica, comoda, moderadas)
- **AND** complete registration immediately
- **AND** redirect to dashboard or home
- **AND** show success message "Cuenta creada exitosamente"

#### Scenario: Registration Form Validation
- **WHEN** user submits invalid data
- **THEN** form SHALL show validation errors inline
- **AND** focus first invalid field
- **AND** prevent navigation to next step
- **AND** show error count badge on progress indicator

#### Scenario: Registration Success
- **WHEN** user completes all steps successfully
- **THEN** system SHALL submit registration to POST /auth/register
- **AND** store JWT tokens securely (httpOnly cookies or encrypted localStorage)
- **AND** redirect to /dashboard
- **AND** show welcome message with user name
- **AND** apply visual preferences immediately

### Requirement: Login Form
The system SHALL provide email/password login with error handling.

#### Scenario: Login Success
- **WHEN** user submits valid credentials
- **THEN** system SHALL POST to /auth/login
- **AND** store access and refresh tokens securely
- **AND** fetch user profile from /auth/me
- **AND** initialize auth context with user data
- **AND** redirect to previous page or /dashboard
- **AND** apply visual preferences within 500ms

#### Scenario: Login Failure
- **WHEN** user submits invalid credentials
- **THEN** system SHALL show error message "Email o contraseña incorrectos"
- **AND** clear password field
- **AND** focus password input
- **AND** NOT indicate which field is incorrect

#### Scenario: Remember Me
- **WHEN** user checks "Recordarme" checkbox
- **THEN** system SHALL extend token storage to 30 days
- **AND** use refresh token to maintain session

### Requirement: Authentication State Management
The system SHALL manage authentication state globally using React Context.

#### Scenario: Auth Context Initialization
- **WHEN** app mounts
- **THEN** system SHALL check for stored tokens
- **AND** validate tokens by calling /auth/me
- **AND** load user profile if tokens valid
- **AND** initialize auth state with user, loading, isAuthenticated
- **AND** set up token refresh timer (23 hours)

#### Scenario: Automatic Token Refresh
- **WHEN** access token nears expiry (< 1 hour remaining)
- **THEN** system SHALL POST refresh token to /auth/refresh
- **AND** store new access token
- **AND** continue user session without interruption
- **AND** reschedule next refresh

#### Scenario: Logout
- **WHEN** user clicks logout
- **THEN** system SHALL clear stored tokens
- **AND** reset auth context to initial state
- **AND** redirect to /login or home
- **AND** clear any cached user data

### Requirement: Visual Preferences Application
The system SHALL apply user visual preferences by dynamically updating CSS variables.

#### Scenario: Theme Application on Login
- **WHEN** authenticated user profile loads
- **THEN** system SHALL extract visual preferences
- **AND** generate CSS variables using theme-generator
- **AND** apply to document.documentElement.style
- **AND** update theme within 500ms
- **AND** show subtle transition animation

#### Scenario: Esquema Colores Application
- **WHEN** esquema_colores is "oscuro_premium"
- **THEN** system SHALL set --color-background: #0a0a0a
- **AND** set --color-surface: #1a1a1a
- **AND** set --color-primary: #c4c4c4
- **AND** set --color-accent: #ffd700
- **AND** set --color-text: #ffffff

#### Scenario: Color Favorito Application
- **WHEN** color_favorito is "dorado"
- **THEN** system SHALL set --color-accent: #ffd700
- **AND** set --color-accent-hover: #ffed4e
- **AND** set --color-button-primary: linear-gradient(135deg, #ffd700, #ffb700)
- **AND** apply to buttons, links, icons

#### Scenario: Densidad Informacion Application
- **WHEN** densidad_informacion is "minimalista"
- **THEN** system SHALL set --spacing-unit: 2rem
- **AND** set --card-padding: 3rem
- **AND** set --line-height: 1.8
- **AND** increase whitespace throughout UI

#### Scenario: Accessibility Override
- **WHEN** user has prefers-reduced-motion system setting
- **THEN** system SHALL override nivel_animaciones to "ninguna"
- **AND** set * { transition: none !important; animation: none !important; }
- **AND** show info message "Animaciones deshabilitadas por preferencias de accesibilidad"

### Requirement: Personalized Dashboards
The system SHALL render different dashboards based on user tipo_cliente.

#### Scenario: Dashboard for Persona Natural
- **WHEN** authenticated user with tipo_cliente="persona" loads /dashboard
- **THEN** system SHALL render DashboardPersonaNatural component
- **AND** show luxury cars and SUVs prominently
- **AND** highlight technology features (MBUX, asistencias)
- **AND** show lifestyle product images
- **AND** display sections: Vehículos recomendados, Agendar test drive, Financiamiento
- **AND** show nearby Kaufmann showrooms based on región

#### Scenario: Dashboard for Empresa
- **WHEN** authenticated user with tipo_cliente="empresa" loads /dashboard
- **THEN** system SHALL render DashboardEmpresa component
- **AND** show commercial vehicles, trucks, buses prominently
- **AND** highlight TCO, fuel efficiency, load capacity
- **AND** show technical specs and fleet comparison table
- **AND** display sections: Flotas recomendadas, Leasing empresarial, Servicio técnico
- **AND** show contact for fleet specialist

#### Scenario: Personalized Product Cards
- **WHEN** user with prioriza_consumo=true views product
- **THEN** product card SHALL show fuel efficiency prominently at top
- **AND** highlight "9.1 L/100km" with icon
- **AND** deprioritize other specs

#### Scenario: Product Card Density Adaptation
- **WHEN** user with densidad_informacion="compacta" views products
- **THEN** product cards SHALL show 3-4 vehicles per row
- **AND** reduce image size
- **AND** show specs in compact table format
- **AND** reduce padding to --card-padding: 1rem

### Requirement: Protected Routes
The system SHALL restrict access to authenticated-only pages.

#### Scenario: Protected Route Access (Authenticated)
- **WHEN** authenticated user navigates to /dashboard or /perfil
- **THEN** system SHALL allow access
- **AND** render page normally

#### Scenario: Protected Route Access (Unauthenticated)
- **WHEN** unauthenticated user navigates to /dashboard or /perfil
- **THEN** system SHALL redirect to /login
- **AND** store intended destination in state
- **AND** redirect back after successful login

#### Scenario: User Menu Display
- **WHEN** authenticated user is on any page
- **THEN** navbar SHALL show user avatar/name
- **AND** dropdown menu SHALL include: Mi perfil, Mis vehículos, Configuración, Cerrar sesión
- **AND** show tipo_cliente badge (Persona / Empresa)

---

## MODIFIED Requirements

### Requirement: Adaptive UI Context Integration
The system SHALL merge ephemeral context with user profile for ML predictions.

**Changes from previous version**:
- useEphemeralContext now checks for authenticated user and merges profile + visual preferences
- Recommendations endpoint receives combined 80-feature context instead of 45

#### Scenario: Context Merge for Authenticated User
- **WHEN** useEphemeralContext hook executes with authenticated user
- **THEN** system SHALL collect 45 automatic ephemeral fields
- **AND** add user.tipo_cliente, user.region, user.interes_principal, etc. (15 profile fields)
- **AND** add user.esquema_colores, user.color_favorito, user.densidad_informacion, etc. (20 visual fields)
- **AND** create unified context object with 80 fields
- **AND** pass to /adaptive/recommendations endpoint

#### Scenario: Context for Anonymous User
- **WHEN** useEphemeralContext hook executes without authenticated user
- **THEN** system SHALL collect 45 automatic ephemeral fields only
- **AND** profile and visual fields SHALL be null
- **AND** pass to /adaptive/recommendations endpoint with 45 fields

---

## REMOVED Requirements

None. All existing frontend requirements are preserved and extended.

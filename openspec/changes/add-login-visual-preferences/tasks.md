# Implementation Tasks

## 1. Backend: Database & Models

- [ ] 1.1 Create Alembic migration for `usuarios` table
  - Columns: id (UUID), email (unique), hashed_password, created_at, updated_at
  - Profile columns: nombre, apellido, rut (unique), telefono, tipo_cliente, fecha_nacimiento, tamano_flota, region, interes_principal, uso_previsto, presupuesto, tiene_vehiculo_actual
  - Visual columns: esquema_colores, color_favorito, estilo_tipografia, densidad_informacion, estilo_imagenes, nivel_animaciones, preferencia_layout, estilo_navegacion, preferencia_visual, prioridades_info (JSONB), modo_comparacion, idioma_specs
  - Indexes: email, rut, tipo_cliente, region
- [ ] 1.2 Create `backend/app/models/user.py` with Usuario Pydantic model
  - UsuarioBase, UsuarioCreate, UsuarioUpdate, UsuarioInDB schemas
  - Field validators: email format, RUT módulo 11, phone format, tipo_cliente enum
- [ ] 1.3 Create `backend/app/models/visual_preferences.py` with VisualPreferences model
  - Enums: EsquemaColores, ColorFavorito, EstiloTipografia, DensidadInformacion, etc.
  - PrioridadesInfo as nested Pydantic model
- [ ] 1.4 Add optional `user_id: Optional[UUID]` field to UserContext in `adaptive_ui.py`

## 2. Backend: Security & Authentication

- [ ] 2.1 Create `backend/app/core/security.py`
  - `get_password_hash(password: str) -> str` using bcrypt (cost 12)
  - `verify_password(plain: str, hashed: str) -> bool`
  - `create_access_token(data: dict, expires_delta: timedelta) -> str` using JWT
  - `create_refresh_token(user_id: UUID) -> str`
- [ ] 2.2 Create `backend/app/core/config.py` additions
  - SECRET_KEY for JWT (from environment variable)
  - ACCESS_TOKEN_EXPIRE_MINUTES = 1440 (24 hours)
  - REFRESH_TOKEN_EXPIRE_DAYS = 30
  - ALGORITHM = "HS256"
- [ ] 2.3 Create `backend/app/core/rut_validator.py`
  - `validate_rut(rut: str) -> bool` - Chile módulo 11 algorithm
  - `clean_rut(rut: str) -> str` - Remove dots/hyphens
  - `detect_tipo_cliente_from_rut(rut: str) -> str` - Persona vs Empresa heuristic

## 3. Backend: Authentication Endpoints

- [ ] 3.1 Create `backend/app/routers/auth.py`
  - `POST /auth/register` - Create new user, return access token
  - `POST /auth/login` - Authenticate user, return access + refresh tokens
  - `POST /auth/refresh` - Refresh access token using refresh token
  - `GET /auth/me` - Get current user profile (requires auth)
  - `PUT /auth/me` - Update user profile (requires auth)
  - `PUT /auth/me/visual-preferences` - Update visual preferences (requires auth)
- [ ] 3.2 Create `backend/app/core/deps.py`
  - `get_current_user(token: str = Depends(oauth2_scheme)) -> Usuario` dependency
  - `get_optional_user(token: Optional[str]) -> Optional[Usuario]` for optional auth
- [ ] 3.3 Add authentication to existing endpoints
  - Modify `POST /adaptive/recommendations` to accept optional Authorization header
  - If authenticated, merge user profile + visual preferences with ephemeral context

## 4. Backend: ML Feature Expansion

- [ ] 4.1 Create `backend/app/ml/feature_processor_v4.py`
  - `prepare_features_v4(context: UserContext, user: Optional[Usuario]) -> np.ndarray`
  - Process 45 automatic features (existing)
  - Add 15 profile features: es_empresa, rango_edad, region_norte/centro/sur, interesa_lujo/comercial/pesado, presupuesto_alto/medio/bajo, tiene_trade_in, edad_exacta, tamano_flota_normalizado
  - Add 20 visual features: esquema_colores_encoded, color_favorito_encoded, prefiere_colores_oscuros, densidad_ui_normalizada, prefiere_serif, sin_animaciones, prioriza_consumo, prioriza_tecnologia, es_usuario_minimalista
- [ ] 4.2 Update `backend/scripts/generate_80_features_dataset.py`
  - Generate 10,000 synthetic samples with 80 features
  - Realistic distributions for Kaufmann customer segments (luxury B2C, commercial B2B, fleet)
  - Correlations: empresa → large fleet → budget high → interest heavy trucks
- [ ] 4.3 Update `backend/scripts/train_xgboost_80_features.py`
  - Train classifier and regressor with 80 features
  - L2 regularization: `reg_lambda=1.0`
  - Feature importance analysis, save top 60 features
  - Cross-validation: 5-fold, stratified by tipo_cliente
  - Target metrics: F1-Score ≥ 0.90, R² ≥ 0.80

## 5. Frontend: Authentication State Management

- [ ] 5.1 Create `frontend/src/lib/auth-client.ts`
  - `login(email: string, password: string): Promise<AuthResponse>`
  - `register(data: RegistrationData): Promise<AuthResponse>`
  - `logout(): void`
  - `refreshToken(): Promise<string>`
  - `getCurrentUser(): Promise<Usuario>`
- [ ] 5.2 Create `frontend/src/hooks/useAuth.ts`
  - State: `user`, `loading`, `isAuthenticated`
  - Methods: `login()`, `register()`, `logout()`, `updateProfile()`
  - Store tokens in httpOnly cookies or localStorage (decide based on security needs)
  - Auto-refresh token before expiry
- [ ] 5.3 Create `frontend/src/contexts/AuthContext.tsx`
  - AuthProvider wrapping app
  - Provide auth state to all components
  - Handle token refresh on app mount

## 6. Frontend: Registration Wizard (3 Steps)

- [ ] 6.1 Create `frontend/src/components/auth/RegistrationWizard.tsx`
  - Multi-step form with progress indicator (1/3, 2/3, 3/3)
  - Navigation: Back, Next, Skip (Step 3 only)
  - Form state management with Zustand or React Hook Form
- [ ] 6.2 Create `frontend/src/components/auth/Step1BasicData.tsx`
  - Fields: email, nombre, apellido, RUT, teléfono
  - Validation: email format, RUT módulo 11, phone Chile format (+569)
  - Real-time RUT validation with feedback
  - Auto-detect tipo_cliente from RUT
- [ ] 6.3 Create `frontend/src/components/auth/Step2Profile.tsx`
  - Conditional fields based on tipo_cliente (persona vs empresa)
  - If persona: fecha_nacimiento (datepicker, age 18-100)
  - If empresa: tamano_flota (number input, 1-1000+)
  - Dropdown: region (15 Chilean regions)
  - Multi-select: interes_principal (autos lujo, SUVs, vans, camiones livianos, pesados, buses, eléctricos)
  - Radio: uso_previsto (personal, ejecutivo, transporte, minería, construcción, agrícola)
  - Slider: presupuesto (<$30M, $30-60M, $60-90M, $90-120M, $120-150M, >$150M)
  - Toggle: tiene_vehiculo_actual
- [ ] 6.4 Create `frontend/src/components/auth/Step3VisualPreferences.tsx`
  - Visual color palette selector (6 options with previews)
  - Color favorite picker (9 colors with swatches)
  - Density slider (minimalista → máxima)
  - Typography style radio (5 options with font previews)
  - Priorities drag-and-drop sorter (precio, consumo, tech, seguridad, specs)
  - "Omitir" button to skip this step and use defaults

## 7. Frontend: Login & Profile UI

- [ ] 7.1 Create `frontend/src/app/login/page.tsx`
  - Email + password form
  - "Olvidé mi contraseña" link (future feature)
  - "Crear cuenta" link to registration
  - Remember me checkbox (extend token expiry)
- [ ] 7.2 Create `frontend/src/app/register/page.tsx`
  - Render RegistrationWizard component
  - Success redirect to dashboard or home
- [ ] 7.3 Create `frontend/src/components/auth/UserMenu.tsx`
  - Avatar dropdown in navbar
  - Links: Mi perfil, Mis vehículos, Configuración, Cerrar sesión
  - Show user name and tipo_cliente badge
- [ ] 7.4 Create `frontend/src/app/perfil/page.tsx`
  - Edit profile information
  - Edit visual preferences
  - Delete account option

## 8. Frontend: Visual Preferences System

- [ ] 8.1 Create `frontend/src/lib/theme-generator.ts`
  - `generateCSSVariables(prefs: VisualPreferences): CSSVariables`
  - Map esquema_colores to color values
  - Map color_favorito to accent color
  - Map densidad_informacion to spacing values
  - Map estilo_tipografia to font-family
- [ ] 8.2 Create `frontend/src/hooks/useVisualPreferences.ts`
  - Load user visual preferences from auth context
  - Apply CSS variables to document root
  - Handle real-time preference updates
  - Override with system accessibility preferences if needed
- [ ] 8.3 Create `frontend/src/styles/themes.css`
  - Define CSS variable structure
  - Default theme (Mercedes-Benz official)
  - 6 color scheme variants (claro elegante, oscuro premium, etc.)
- [ ] 8.4 Update `frontend/src/components/adaptive/AdaptiveUIProvider.tsx`
  - Check if user authenticated
  - If yes, apply visual preferences
  - If no, use automatic detection only

## 9. Frontend: Personalized Dashboards

- [ ] 9.1 Create `frontend/src/components/dashboard/DashboardPersonaNatural.tsx`
  - Focus: Luxury cars, SUVs, personal use
  - Highlight: Technology, safety, lifestyle images
  - Sections: Vehículos recomendados, Test drive, Financiamiento
- [ ] 9.2 Create `frontend/src/components/dashboard/DashboardEmpresa.tsx`
  - Focus: Commercial vehicles, trucks, fleet management
  - Highlight: TCO, fuel efficiency, load capacity
  - Sections: Flotas recomendadas, Leasing, Servicio técnico
- [ ] 9.3 Create `frontend/src/app/dashboard/page.tsx`
  - Conditional render based on user.tipo_cliente
  - Show personalized product recommendations using ML
  - Display nearby Kaufmann locations based on region
- [ ] 9.4 Create `frontend/src/components/products/ProductCardPersonalized.tsx`
  - Adapt card content based on prioridades_info
  - If prioriza_consumo, show fuel efficiency prominently
  - If prioriza_tecnologia, show tech features first
  - If densidad_minimalista, show large image + price only

## 10. Integration & Testing

- [ ] 10.1 Update `frontend/src/hooks/useEphemeralContext.ts`
  - Merge automatic context (45 fields) with user profile if authenticated
  - Send combined data to ML recommendations endpoint
- [ ] 10.2 Create integration tests for auth flow
  - Test: Register → Login → Get profile → Update preferences → Logout
  - Test: Token refresh before expiry
  - Test: Invalid RUT rejection
  - Test: Duplicate email rejection
- [ ] 10.3 Create unit tests for visual preference application
  - Test: CSS variables correctly generated for each theme
  - Test: Accessibility overrides work correctly
  - Test: Density changes affect spacing values
- [ ] 10.4 Create E2E tests for registration wizard
  - Test: Complete 3-step registration successfully
  - Test: Skip visual preferences and use defaults
  - Test: Back button navigation preserves form data
  - Test: RUT validation shows correct error messages

## 11. ML Retraining & Validation

- [ ] 11.1 Generate synthetic dataset with 80 features (10,000 samples)
- [ ] 11.2 Train XGBoost classifier with 80 features
  - Validate F1-Score ≥ 0.90 on test set
  - Analyze feature importance, identify top 60 features
- [ ] 11.3 Train XGBoost regressor with 80 features
  - Validate R² ≥ 0.80 on test set
  - Compare with baseline (45 features) to measure improvement
- [ ] 11.4 Deploy new models to production
  - Save models: `xgboost_classifier_80f_v4.json`, `xgboost_regressor_80f_v4.json`
  - Update model loading in `adaptive_service.py`

## 12. Documentation & Compliance

- [ ] 12.1 Update `docs/POLITICA_PRIVACIDAD.md`
  - List all 80+ fields collected (automatic + profile + visual)
  - Explain data usage for ML personalization
  - Add user rights: access, modify, delete account
  - GDPR compliance: data retention policy, right to be forgotten
- [ ] 12.2 Create `docs/API_AUTH.md`
  - Document all authentication endpoints
  - Example requests/responses
  - JWT token structure
  - Error codes
- [ ] 12.3 Create `docs/VISUAL_PREFERENCES_GUIDE.md`
  - Explain each visual preference option
  - Show CSS variable mappings
  - Guide for designers to add new themes
- [ ] 12.4 Update `README.md`
  - Add authentication setup instructions
  - Environment variables: SECRET_KEY, TOKEN_EXPIRE_MINUTES
  - Database migration commands

## 13. Deployment & Monitoring

- [ ] 13.1 Add environment variables to production
  - SECRET_KEY (generate secure random key)
  - DATABASE_URL with usuarios table access
  - Configure CORS for auth endpoints
- [ ] 13.2 Run database migration in production
  - Backup database before migration
  - Test migration on staging first
  - Run `alembic upgrade head`
- [ ] 13.3 Add monitoring for auth endpoints
  - Track registration success rate
  - Monitor login failures (security)
  - Alert on unusual authentication patterns
- [ ] 13.4 Add analytics events
  - Track wizard completion rate (% who finish Step 3)
  - Track visual preference adoption
  - A/B test: personalized vs default theme engagement

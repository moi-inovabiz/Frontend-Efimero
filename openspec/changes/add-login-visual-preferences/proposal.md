# Add User Login with Visual Preferences System

**Change ID**: `add-login-visual-preferences`  
**Created**: 2025-11-03  
**Status**: Proposed

---

## Why

The current adaptive UI system collects 45 automatic ephemeral context fields (browser, hardware, network, behavior) without user authentication, limiting personalization capabilities. To improve ML model accuracy from F1-Score 0.75 to 0.90-0.95 and enable persistent personalization across sessions, we need:

1. **User authentication** - Enable persistent profiles tied to user accounts
2. **Automotive-specific profile data** - Collect customer type (persona/empresa), product interests, budget, region for Kaufmann Mercedes-Benz Chile business context
3. **Visual preferences** - Capture color schemes, typography, layout density, and UI priorities to personalize the interface appearance

This will increase total ML features from 45 (automatic) to 75+ (automatic + profile + visual preferences), enabling better product recommendations and UI adaptation for luxury car buyers, commercial fleet operators, and mining/transport companies.

---

## What Changes

### Core Changes
- **Add user authentication system** with JWT tokens, password hashing, email/password login
- **Create 3-step registration wizard**:
  - Step 1: Basic data (email, nombre, apellido, RUT, teléfono)
  - Step 2: Automotive profile (tipo_cliente, región, interés_principal, uso_previsto, presupuesto, vehículo_actual)
  - Step 3: Visual preferences (esquema_colores, color_favorito, densidad_información, prioridades)
- **Implement visual preference system** with 12 customization options affecting CSS variables, theme, layout density
- **Integrate login data with ML pipeline** - Expand FeatureProcessor from 45 to 75+ features
- **Add backend User model** with Pydantic validation, RUT validation (Chile módulo 11 algorithm)
- **Create personalized dashboards** - Different UI for persona natural (luxury focus) vs empresa (fleet/commercial focus)

### Technical Changes
- New backend endpoints: `/auth/register`, `/auth/login`, `/auth/me`, `/auth/refresh`
- New frontend components: `RegistrationWizard`, `LoginForm`, `VisualPreferencesForm`
- New database models: `Usuario` with authentication fields + profile fields + visual preferences
- CSS theming system with dynamic CSS variables based on user preferences
- ML feature expansion: 45 automatic + 15 profile + 20 visual = 80 total features

### Breaking Changes
- **BREAKING**: `UserContext` model expanded with optional `user_id` field linking to authenticated user
- **BREAKING**: `/adaptive/recommendations` endpoint now accepts optional `Authorization: Bearer <token>` header for personalized responses

---

## Impact

### Affected Specs
- **auth** - Major expansion: Add registration, login, JWT authentication, user profile management
- **frontend** - Add registration wizard, login forms, visual preferences UI, theme switching
- **api** - Add authentication endpoints, modify UserContext to include user_id
- **ml** - Expand FeatureProcessor from 45 to 80 features, retrain models with profile + visual data

### Affected Code
- `backend/app/models/user.py` (NEW) - Usuario model with authentication + profile + visual preferences
- `backend/app/routers/auth.py` (NEW) - Authentication endpoints
- `backend/app/core/security.py` (NEW) - JWT token creation, password hashing
- `backend/app/models/adaptive_ui.py` (MODIFIED) - Add optional user_id field to UserContext
- `backend/app/ml/feature_processor.py` (MODIFIED) - Add prepare_features_v4() with 80 features
- `frontend/src/components/auth/RegistrationWizard.tsx` (NEW) - 3-step registration form
- `frontend/src/components/auth/LoginForm.tsx` (NEW) - Login page
- `frontend/src/components/auth/VisualPreferencesForm.tsx` (NEW) - Visual customization UI
- `frontend/src/hooks/useAuth.ts` (NEW) - Authentication state management
- `frontend/src/hooks/useVisualPreferences.ts` (NEW) - Theme management
- `frontend/src/styles/theme-generator.ts` (NEW) - Dynamic CSS variable generation

### Database Changes
- New table: `usuarios` with columns:
  - Authentication: id, email, hashed_password, created_at, updated_at
  - Profile: nombre, apellido, rut, telefono, tipo_cliente, fecha_nacimiento, tamano_flota, region, interes_principal, uso_previsto, presupuesto, tiene_vehiculo_actual
  - Visual: esquema_colores, color_favorito, estilo_tipografia, densidad_informacion, estilo_imagenes, nivel_animaciones, preferencia_layout, estilo_navegacion, preferencia_visual, prioridades_info (JSON), modo_comparacion, idioma_specs

### ML Improvements
- **Current**: 45 automatic features → F1-Score 0.75, R² 0.46
- **Expected**: 80 features (45 automatic + 15 profile + 20 visual) → F1-Score 0.90-0.95, R² 0.80-0.85
- **New features**:
  - Profile: `es_empresa`, `rango_edad`, `region_norte/centro/sur`, `interesa_lujo/comercial/pesado`, `presupuesto_alto/medio/bajo`, `tiene_trade_in`
  - Visual: `prefiere_colores_oscuros`, `densidad_ui_normalizada`, `prioriza_consumo`, `es_usuario_minimalista`, `sin_animaciones`

---

## Success Criteria

1. Users can register with email/password and complete 3-step wizard in < 3 minutes
2. RUT validation correctly detects persona natural vs empresa (Chile módulo 11)
3. Visual preferences apply in < 500ms after login with correct CSS variables
4. Different dashboards render for persona natural vs empresa with appropriate product focus
5. ML models retrained with 80 features achieve F1-Score ≥ 0.90 and R² ≥ 0.80
6. JWT tokens expire after 24 hours and refresh tokens work for 30 days
7. All passwords hashed with bcrypt (cost factor 12)
8. Login data integrates with existing 45 automatic ephemeral context fields

---

## Risks & Mitigations

### Risk 1: User friction from 3-step registration
**Mitigation**: 
- Make Step 3 (Visual Preferences) optional with "Omitir" button
- Save progress after each step (partial registration recovery)
- Prefill fields from automatic detection where possible (region from timezone, device type)

### Risk 2: Visual preferences conflicts with accessibility settings
**Mitigation**:
- Always respect `prefers-reduced-motion`, `prefers-contrast` system settings
- Override visual preferences if they conflict with accessibility needs
- Show warning: "Tus preferencias de accesibilidad del sistema tienen prioridad"

### Risk 3: ML overfitting with 80 features
**Mitigation**:
- Use feature importance analysis to prune low-value features
- Implement L2 regularization in XGBoost training
- Cross-validation with separate test set (80/20 split)

### Risk 4: Database migration complexity
**Mitigation**:
- Create migration script with rollback capability
- Test on staging with synthetic user data first
- Backup production database before migration

---

## Open Questions

1. **Social login**: Should we support Google/Apple sign-in for faster registration? (Can add in future iteration)
2. **Profile completion incentive**: Offer discount/benefit for completing visual preferences?
3. **A/B testing**: Test default theme vs personalized theme to measure engagement impact?
4. **Data retention**: How long to keep inactive user accounts? (GDPR compliance)

---

## Timeline Estimate

- **Week 1**: Backend authentication + User model + database migration
- **Week 2**: Frontend registration wizard + login forms
- **Week 3**: Visual preferences system + CSS theming
- **Week 4**: ML integration + model retraining
- **Week 5**: Testing + bug fixes + documentation

**Total**: ~5 weeks for full implementation

# Implementation Tasks: Google Auth & Country Events System

## 1. Backend - Authentication Infrastructure
- [ ] 1.1 Configure Firebase Admin SDK with Google OAuth provider
- [ ] 1.2 Create `/auth/google` endpoint for OAuth token verification
- [ ] 1.3 Implement `UserService` for user profile CRUD operations
- [ ] 1.4 Create Pydantic models for `GoogleAuthRequest`, `GoogleAuthResponse`, `UserProfile`
- [ ] 1.5 Implement JWT token generation and verification with user claims
- [ ] 1.6 Add middleware for JWT authentication on protected routes

## 2. Backend - User Profile Management
- [ ] 2.1 Create Firestore schema for `users/{google_id}` collection
- [ ] 2.2 Implement `get_or_create_user()` method in UserService
- [ ] 2.3 Add Google People API integration for birthday data
- [ ] 2.4 Add Google Calendar API integration for timezone data
- [ ] 2.5 Implement locale parsing (extract country code from locale string)
- [ ] 2.6 Create age range calculator from birthday date
- [ ] 2.7 Implement anonymous data migration (`user_temp_id` → `google_id`)

## 3. Backend - Country Events Service
- [ ] 3.1 Create `EventsService` class with Nager.Date API integration
- [ ] 3.2 Implement `fetch_nager_holidays()` method for official holidays
- [ ] 3.3 Create local cultural events database (JSON/dict structure)
- [ ] 3.4 Implement `get_cultural_events()` method with date calculations
- [ ] 3.5 Add Easter/Carnival date calculation algorithms
- [ ] 3.6 Create Firestore cache layer for events (30-day TTL)
- [ ] 3.7 Implement `/events/country/{country_code}` API endpoint
- [ ] 3.8 Add country emoji mapping utility

## 4. Backend - API Endpoints
- [ ] 4.1 Create `POST /api/v1/auth/google` for OAuth authentication
- [ ] 4.2 Create `GET /api/v1/auth/me` for current user profile
- [ ] 4.3 Create `POST /api/v1/auth/logout` for session invalidation
- [ ] 4.4 Create `GET /api/v1/events/{country_code}` for country events
- [ ] 4.5 Create `GET /api/v1/events/upcoming` for user's next events
- [ ] 4.6 Update existing `/predict` endpoint to use authenticated user context
- [ ] 4.7 Add error handling for missing/invalid Google tokens

## 5. Frontend - Authentication UI
- [ ] 5.1 Create `GoogleLoginButton.tsx` component with Google branding
- [ ] 5.2 Create `AuthProvider.tsx` context for auth state management
- [ ] 5.3 Implement `useAuth()` hook with login/logout/user state
- [ ] 5.4 Create `/lib/auth/google-auth.ts` with Firebase Auth integration
- [ ] 5.5 Add Google OAuth scopes configuration (openid, email, profile, calendar, birthday)
- [ ] 5.6 Create login page with Google sign-in button
- [ ] 5.7 Implement JWT storage in localStorage with secure handling
- [ ] 5.8 Add auth loading states and error handling

## 6. Frontend - Protected Routes & Navigation
- [ ] 6.1 Create route protection HOC/middleware for authenticated pages
- [ ] 6.2 Implement redirect logic (login → dashboard, logout → home)
- [ ] 6.3 Update navigation header with user avatar and dropdown menu
- [ ] 6.4 Create user profile dropdown (avatar, name, logout button)
- [ ] 6.5 Add auth state persistence across page refreshes
- [ ] 6.6 Implement token refresh logic before expiration

## 7. Frontend - Events Display
- [ ] 7.1 Create `EventsWidget.tsx` component for dashboard
- [ ] 7.2 Create `useCountryEvents()` hook to fetch and cache events
- [ ] 7.3 Implement "Next Holiday" countdown display
- [ ] 7.4 Create events calendar view component (optional)
- [ ] 7.5 Add event notifications/reminders (optional)
- [ ] 7.6 Style events with country-specific colors/emojis

## 8. Frontend - API Client Integration
- [ ] 8.1 Update `api-client.ts` with auth header injection
- [ ] 8.2 Add `authWithGoogle()` method to API client
- [ ] 8.3 Add `getCurrentUser()` method to fetch user profile
- [ ] 8.4 Add `getCountryEvents()` method to fetch events
- [ ] 8.5 Implement automatic token refresh on 401 responses
- [ ] 8.6 Add request interceptor for JWT token attachment

## 9. Database - Firestore Setup
- [ ] 9.1 Create `users` collection structure and indexes
- [ ] 9.2 Create `events_cache` collection structure and indexes
- [ ] 9.3 Create `user_migrations` collection for tracking anonymous→auth migrations
- [ ] 9.4 Implement Firestore security rules for user data
- [ ] 9.5 Add composite indexes for efficient event queries
- [ ] 9.6 Set up TTL policy for events cache (30 days)

## 10. Data Migration System
- [ ] 10.1 Create migration service to link `user_temp_id` with `google_id`
- [ ] 10.2 Implement batch migration of `behaviors/{user_temp_id}` → `users/{google_id}/behaviors`
- [ ] 10.3 Add migration status tracking in Firestore
- [ ] 10.4 Create rollback mechanism for failed migrations
- [ ] 10.5 Implement de-duplication logic for existing user data

## 11. ML Feature Enhancement
- [ ] 11.1 Add `timezone` feature to FeatureProcessor
- [ ] 11.2 Add `locale` feature (language + country code)
- [ ] 11.3 Add `age_range` categorical feature
- [ ] 11.4 Add `days_until_next_holiday` temporal feature
- [ ] 11.5 Add `is_holiday_season` boolean feature
- [ ] 11.6 Update feature scaler with new features
- [ ] 11.7 Retrain models with enhanced feature set

## 12. Testing - Backend
- [ ] 12.1 Unit tests for `UserService` CRUD operations
- [ ] 12.2 Unit tests for `EventsService` with mocked API responses
- [ ] 12.3 Integration tests for `/auth/google` endpoint
- [ ] 12.4 Integration tests for `/events` endpoints
- [ ] 12.5 Test data migration with sample anonymous users
- [ ] 12.6 Test JWT token generation and validation
- [ ] 12.7 Test Firestore security rules

## 13. Testing - Frontend
- [ ] 13.1 Unit tests for `useAuth()` hook
- [ ] 13.2 Unit tests for `GoogleLoginButton` component
- [ ] 13.3 Integration tests for auth flow (login → dashboard)
- [ ] 13.4 Test token refresh logic
- [ ] 13.5 Test protected route redirects
- [ ] 13.6 E2E test for complete login flow with Google

## 14. Documentation
- [ ] 14.1 Document Google OAuth setup in README
- [ ] 14.2 Create API documentation for new auth endpoints
- [ ] 14.3 Document Firestore schema and security rules
- [ ] 14.4 Create user guide for login process
- [ ] 14.5 Document cultural events database maintenance process
- [ ] 14.6 Add architecture diagrams for auth flow
- [ ] 14.7 Document cost monitoring and free tier limits

## 15. Monitoring & Observability
- [ ] 15.1 Add logging for auth events (login, logout, token refresh)
- [ ] 15.2 Add metrics for Nager.Date API usage
- [ ] 15.3 Add alerts for Firestore quota approaching limits
- [ ] 15.4 Create dashboard for monitoring active users
- [ ] 15.5 Track events cache hit rate
- [ ] 15.6 Monitor anonymous→auth migration success rate

## Dependencies & Prerequisites
- Firebase Admin SDK configured with service account
- Google Cloud Console project with OAuth 2.0 credentials
- Enable Google People API and Calendar API
- Nager.Date API endpoint accessible (no authentication needed)
- Firestore database initialized with proper indexes

## Success Criteria per Task Group
1. **Auth Infrastructure**: Users can login with Google and receive valid JWT
2. **Profile Management**: All Google scopes data captured and stored correctly
3. **Events Service**: Returns accurate holidays for user's country with <500ms latency
4. **API Endpoints**: All endpoints return proper responses with auth validation
5. **Frontend UI**: Smooth login flow with no friction, professional Google branding
6. **Protected Routes**: Only authenticated users can access dashboard
7. **Events Display**: Next holiday widget shows accurate countdown
8. **Database**: Firestore stores user data securely with proper indexes
9. **Data Migration**: Anonymous users successfully linked to Google accounts
10. **ML Enhancement**: New features integrated into prediction pipeline
11. **Testing**: >90% code coverage for critical auth paths
12. **Documentation**: Complete setup guide for developers
13. **Monitoring**: Real-time visibility into auth system health
14. **Performance**: Login completes in <3 seconds, API responses <500ms
15. **Cost**: System operates 100% within free tier limits

## Rollout Plan
1. **Phase 1** (Tasks 1-4): Backend auth infrastructure
2. **Phase 2** (Tasks 5-8): Frontend auth UI and integration
3. **Phase 3** (Tasks 9-10): Database setup and migration
4. **Phase 4** (Tasks 11): ML feature enhancement
5. **Phase 5** (Tasks 12-13): Testing
6. **Phase 6** (Tasks 14-15): Documentation and monitoring

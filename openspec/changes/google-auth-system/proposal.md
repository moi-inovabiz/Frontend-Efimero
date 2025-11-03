# Google Authentication & Country Events System

**Status**: 🔵 In Progress  
**Priority**: High  
**Complexity**: Medium  
**Impact**: Major user experience improvement

## Overview

Implement complete Google OAuth 2.0 authentication system with extended user profile data (email, name, photo, locale, timezone, birthday) and integrate free country-specific events system (national holidays + cultural events) using Nager.Date API and local curated database.

## Objectives

1. **User Authentication**: Single-click Google OAuth login without onboarding friction
2. **Extended Profile**: Capture locale, timezone, birthday, age range from Google
3. **Country Events**: Provide national holidays and cultural events based on user's country
4. **Data Migration**: Seamlessly migrate anonymous user data (`user_temp_id`) to authenticated profile
5. **Zero Cost**: Implement using 100% free services within Firestore/Nager.Date limits
6. **ML Enhancement**: Enrich ML features with timezone, locale, age_range, upcoming events

## Technical Approach

### Authentication Flow
```
User clicks "Sign in with Google"
    ↓
Google OAuth popup (scopes: openid, email, profile, calendar.readonly, birthday.read)
    ↓
Backend verifies token with Firebase Auth
    ↓
Create/update user profile in Firestore
    ↓
Migrate anonymous behavior data (user_temp_id → google_id)
    ↓
Generate JWT token
    ↓
Return to dashboard (no onboarding)
```

### Events System Architecture
```
Nager.Date API (free)
    ↓ Fetch official holidays
Events Service
    ↓ Combine with
Local Cultural Events DB
    ↓ Cache in Firestore (30 days)
API Response
```

## Affected Systems

- **Frontend**: Login page, auth provider, user context, events widget
- **Backend**: Auth endpoints, user service, events service, Firebase integration
- **Database**: Firestore collections (users, events_cache, behaviors migration)
- **External APIs**: Google OAuth, Nager.Date API

## Dependencies

- Firebase Authentication SDK
- Google People API (birthday scope)
- Google Calendar API (timezone scope)
- Nager.Date API (public holidays - free, no API key)
- Firestore for user profiles and events cache

## Success Metrics

- [ ] User can login with Google in <3 seconds
- [ ] Profile captures: email, name, photo, locale, timezone, birthday, age_range
- [ ] Events system returns accurate holidays for 100+ countries
- [ ] Anonymous data successfully migrates to authenticated profile
- [ ] Zero API costs (within free tier limits)
- [ ] Cache reduces API calls by >90%

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Google API quota exceeded | High | Implement aggressive caching, use Firestore cache layer |
| Nager.Date API unavailable | Medium | Fallback to cached data, local database backup |
| User denies birthday/calendar scopes | Low | Make scopes optional, graceful degradation |
| Firestore costs exceed free tier | Medium | Monitor usage, implement data retention policies |

## Estimated Effort

- **Frontend**: 8 hours
- **Backend**: 10 hours
- **Testing**: 4 hours
- **Documentation**: 2 hours
- **Total**: ~24 hours (~3 days)

## Related Specs

- `auth.md` - Authentication system specification
- `api.md` - API endpoints for auth and events
- `frontend.md` - UI components for login and events display

## Notes

- No onboarding flow - users go directly to dashboard after Google login
- System learns preferences automatically from behavior (no explicit questions)
- Cultural events database maintained manually (1-2 hours/year maintenance)
- All external APIs used are 100% free with generous limits

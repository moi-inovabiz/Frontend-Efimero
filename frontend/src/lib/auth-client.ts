/**
 * Authentication API client
 * Handles all auth-related HTTP requests to backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface RegistrationData {
  // Step 1: Basic data
  email: string;
  password: string;
  nombre: string;
  apellido: string;
  rut: string;
  telefono?: string;
  tipo_cliente: 'persona' | 'empresa';
  
  // Step 2: Profile
  fecha_nacimiento?: string; // ISO date (persona)
  tamano_flota?: number; // (empresa)
  region: string;
  interes_principal?: string[];
  uso_previsto?: string;
  presupuesto?: string;
  tiene_vehiculo_actual?: boolean;
  
  // Step 3: Visual preferences (optional)
  visual_preferences?: {
    esquema_colores?: string;
    color_favorito?: string;
    estilo_tipografia?: string;
    densidad_informacion?: string;
    estilo_imagenes?: string;
    nivel_animaciones?: string;
    preferencia_layout?: string;
    estilo_navegacion?: string;
    preferencia_visual?: string;
    prioridades_info?: {
      precio: number;
      especificaciones: number;
      consumo: number;
      seguridad: number;
      tecnologia: number;
    };
    modo_comparacion?: string;
    idioma_specs?: string;
  };
}

export interface Usuario {
  id: string;
  email: string;
  nombre: string;
  apellido: string;
  rut: string;
  telefono?: string;
  tipo_cliente: 'persona' | 'empresa';
  fecha_nacimiento?: string;
  tamano_flota?: number;
  region: string;
  interes_principal?: string[];
  uso_previsto?: string;
  presupuesto?: string;
  tiene_vehiculo_actual: boolean;
  
  // Visual preferences
  esquema_colores: string;
  color_favorito: string;
  estilo_tipografia: string;
  densidad_informacion: string;
  estilo_imagenes: string;
  nivel_animaciones: string;
  preferencia_layout: string;
  estilo_navegacion: string;
  preferencia_visual: string;
  prioridades_info?: Record<string, number>;
  modo_comparacion: string;
  idioma_specs: string;
  
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

// ==================== TOKEN MANAGEMENT ====================

const TOKEN_KEY = 'frontend_efimero_access_token';
const REFRESH_TOKEN_KEY = 'frontend_efimero_refresh_token';

export const TokenManager = {
  getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
  },

  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },

  setTokens(accessToken: string, refreshToken: string): void {
    if (typeof window === 'undefined') return;
    
    // Guardar en localStorage
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    
    // También guardar en cookies para SSR
    document.cookie = `access_token=${accessToken}; path=/; max-age=86400; SameSite=Lax`;
    document.cookie = `refresh_token=${refreshToken}; path=/; max-age=2592000; SameSite=Lax`;
  },

  clearTokens(): void {
    if (typeof window === 'undefined') return;
    
    // Limpiar localStorage
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    
    // Limpiar cookies
    document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
  },

  getAuthHeaders(): HeadersInit {
    const token = this.getAccessToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  },
};

// ==================== API ERROR HANDLING ====================

export class AuthError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'AuthError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    
    // Si hay detalles de validación de Pydantic, formatearlos
    let errorMessage = errorData.detail || 'Error en la solicitud';
    
    if (Array.isArray(errorData.detail)) {
      // FastAPI validation errors format
      const validationErrors = errorData.detail.map((err: any) => {
        const field = err.loc?.join('.') || 'unknown';
        return `${field}: ${err.msg}`;
      }).join(', ');
      errorMessage = `Errores de validación: ${validationErrors}`;
    }
    
    console.error('[AUTH] API Error:', {
      status: response.status,
      message: errorMessage,
      details: errorData
    });
    
    throw new AuthError(
      errorMessage,
      response.status,
      errorData
    );
  }
  return response.json();
}

// ==================== AUTH API FUNCTIONS ====================

/**
 * Register new user
 */
export async function register(data: RegistrationData): Promise<AuthResponse> {
  console.log('[AUTH] Registering user with data:', {
    ...data,
    password: '***REDACTED***'
  });
  
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  console.log('[AUTH] Register response status:', response.status);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    console.error('[AUTH] Register error:', errorData);
  }

  const authResponse = await handleResponse<AuthResponse>(response);
  
  // Store tokens
  TokenManager.setTokens(authResponse.access_token, authResponse.refresh_token);
  
  return authResponse;
}

/**
 * Login with email and password
 */
export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  const authResponse = await handleResponse<AuthResponse>(response);
  
  // Store tokens
  TokenManager.setTokens(authResponse.access_token, authResponse.refresh_token);
  
  return authResponse;
}

/**
 * Refresh access token
 */
export async function refreshAccessToken(): Promise<AuthResponse> {
  const refreshToken = TokenManager.getRefreshToken();
  
  if (!refreshToken) {
    throw new AuthError('No refresh token available');
  }

  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  const authResponse = await handleResponse<AuthResponse>(response);
  
  // Store new access token
  TokenManager.setTokens(authResponse.access_token, authResponse.refresh_token);
  
  return authResponse;
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<Usuario> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...TokenManager.getAuthHeaders(),
    },
  });

  return handleResponse<Usuario>(response);
}

/**
 * Update user profile
 */
export async function updateProfile(updates: Partial<Usuario>): Promise<Usuario> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...TokenManager.getAuthHeaders(),
    },
    body: JSON.stringify(updates),
  });

  return handleResponse<Usuario>(response);
}

/**
 * Update visual preferences
 */
export async function updateVisualPreferences(
  preferences: RegistrationData['visual_preferences']
): Promise<Usuario> {
  const response = await fetch(`${API_BASE_URL}/auth/me/visual-preferences`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...TokenManager.getAuthHeaders(),
    },
    body: JSON.stringify(preferences),
  });

  return handleResponse<Usuario>(response);
}

/**
 * Logout (clear tokens)
 */
export function logout(): void {
  TokenManager.clearTokens();
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return TokenManager.getAccessToken() !== null;
}

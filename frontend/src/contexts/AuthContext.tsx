/**
 * Authentication Context Provider
 * Global state management for user authentication
 */

'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  Usuario,
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  getCurrentUser,
  refreshAccessToken,
  isAuthenticated as checkAuth,
  RegistrationData,
  LoginCredentials,
  TokenManager,
  AuthError,
} from '@/lib/auth-client';

interface AuthContextType {
  user: Usuario | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegistrationData) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  /**
   * Load user profile on mount if token exists
   */
  const loadUser = useCallback(async () => {
    try {
      if (checkAuth()) {
        const userData = await getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
        
        // Aplicar tema inmediatamente después de cargar el usuario
        if (typeof window !== 'undefined' && userData) {
          console.log('[AuthContext] Aplicando tema después de loadUser para usuario:', userData.email);
          const { generateTheme, themeToCSS } = await import('@/lib/theme-generator');
          const theme = generateTheme(userData);
          const css = themeToCSS(theme);
          
          let style = document.getElementById('user-theme-ssr') || document.getElementById('user-theme') || document.getElementById('user-theme-preview');
          if (!style) {
            style = document.createElement('style');
            style.id = 'user-theme';
            document.head.appendChild(style);
          }
          style.textContent = css;
          document.body.style.fontFamily = theme.fontFamily;
          
          console.log('[AuthContext] Tema aplicado en loadUser');
        }
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }
    } catch (err) {
      console.error('Error loading user:', err);
      
      // If token expired, try to refresh
      if (err instanceof AuthError && err.statusCode === 401) {
        try {
          await refreshAccessToken();
          const userData = await getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
          
          // Aplicar tema después del refresh
          if (typeof window !== 'undefined' && userData) {
            console.log('[AuthContext] Aplicando tema después de refresh token');
            const { generateTheme, themeToCSS } = await import('@/lib/theme-generator');
            const theme = generateTheme(userData);
            const css = themeToCSS(theme);
            
            let style = document.getElementById('user-theme-ssr') || document.getElementById('user-theme') || document.getElementById('user-theme-preview');
            if (!style) {
              style = document.createElement('style');
              style.id = 'user-theme';
              document.head.appendChild(style);
            }
            style.textContent = css;
            document.body.style.fontFamily = theme.fontFamily;
          }
        } catch (refreshErr) {
          // Refresh failed, clear tokens
          TokenManager.clearTokens();
          setUser(null);
          setIsAuthenticated(false);
        }
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  /**
   * Login user
   */
  const login = useCallback(async (credentials: LoginCredentials) => {
    setLoading(true);
    setError(null);
    
    try {
      await apiLogin(credentials);
      const userData = await getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
      
      // Aplicar tema inmediatamente después del login
      if (typeof window !== 'undefined') {
        const { generateTheme, themeToCSS } = await import('@/lib/theme-generator');
        const theme = generateTheme(userData);
        const css = themeToCSS(theme);
        
        let style = document.getElementById('user-theme-preview') || document.getElementById('user-theme-ssr') || document.getElementById('user-theme');
        if (!style) {
          style = document.createElement('style');
          style.id = 'user-theme';
          document.head.appendChild(style);
        }
        style.id = 'user-theme';
        style.textContent = css;
        document.body.style.fontFamily = theme.fontFamily;
      }
    } catch (err) {
      const errorMessage = err instanceof AuthError 
        ? err.message 
        : 'Error al iniciar sesión';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Register new user
   */
  const register = useCallback(async (data: RegistrationData) => {
    setLoading(true);
    setError(null);
    
    try {
      await apiRegister(data);
      const userData = await getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
      
      // Aplicar tema inmediatamente después del registro
      // Esto asegura que las preferencias visuales se apliquen antes del redirect
      if (typeof window !== 'undefined') {
        console.log('[AuthContext] Aplicando tema después del registro para usuario:', userData.email);
        console.log('[AuthContext] Preferencias visuales:', {
          esquema_colores: userData.esquema_colores,
          color_favorito: userData.color_favorito,
          estilo_tipografia: userData.estilo_tipografia
        });
        
        // Importar dinámicamente para evitar problemas de SSR
        const { generateTheme, themeToCSS } = await import('@/lib/theme-generator');
        const theme = generateTheme(userData);
        const css = themeToCSS(theme);
        
        console.log('[AuthContext] Tema generado:', theme);
        
        // Reusar el style tag de preview si existe, o crear uno nuevo
        let style = document.getElementById('user-theme-preview') || document.getElementById('user-theme-ssr') || document.getElementById('user-theme');
        if (!style) {
          style = document.createElement('style');
          style.id = 'user-theme';
          document.head.appendChild(style);
        }
        // Cambiar el ID a user-theme para que sea consistente
        style.id = 'user-theme';
        style.textContent = css;
        document.body.style.fontFamily = theme.fontFamily;
        
        console.log('[AuthContext] Tema aplicado exitosamente');
      }
    } catch (err) {
      const errorMessage = err instanceof AuthError 
        ? err.message 
        : 'Error al registrarse';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Logout user
   */
  const logout = useCallback(() => {
    apiLogout();
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
  }, []);

  /**
   * Refresh user data
   */
  const refreshUser = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (err) {
      console.error('Error refreshing user:', err);
    }
  }, [isAuthenticated]);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Set up automatic token refresh (23 hours)
   */
  useEffect(() => {
    if (!isAuthenticated) return;

    const refreshInterval = setInterval(
      async () => {
        try {
          await refreshAccessToken();
          console.log('Token refreshed successfully');
        } catch (err) {
          console.error('Failed to refresh token:', err);
          logout();
        }
      },
      23 * 60 * 60 * 1000 // 23 hours
    );

    return () => clearInterval(refreshInterval);
  }, [isAuthenticated, logout]);

  const value: AuthContextType = {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    refreshUser,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use auth context
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

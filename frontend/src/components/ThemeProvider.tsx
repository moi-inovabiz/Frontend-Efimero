/**
 * ThemeProvider Client Component
 * Actualiza CSS variables cuando el usuario cambia sus preferencias
 * El tema inicial se renderiza en el servidor (ver layout.tsx)
 */

'use client';

import { useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { generateTheme, themeToCSS } from '@/lib/theme-generator';

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();

  useEffect(() => {
    // Solo actualizar si el usuario cambió (para cambios en preferencias)
    if (!user) {
      console.log('[ThemeProvider] No hay usuario, no aplicando tema');
      return;
    }

    console.log('[ThemeProvider] Usuario detectado, aplicando tema:', {
      email: user.email,
      esquema_colores: user.esquema_colores,
      color_favorito: user.color_favorito
    });

    // Generar tema basado en preferencias del usuario
    const theme = generateTheme(user);
    const css = themeToCSS(theme);

    // Actualizar el style tag del servidor o crear uno nuevo
    let style = document.getElementById('user-theme-ssr') || document.getElementById('user-theme');
    
    if (!style) {
      console.log('[ThemeProvider] Creando nuevo style tag');
      style = document.createElement('style');
      style.id = 'user-theme';
      document.head.appendChild(style);
    } else {
      console.log('[ThemeProvider] Actualizando style tag existente:', style.id);
    }

    style.textContent = css;

    // Aplicar font-family al body
    document.body.style.fontFamily = theme.fontFamily;
    
    console.log('[ThemeProvider] Tema aplicado exitosamente');
  }, [user]);

  return <>{children}</>;
}

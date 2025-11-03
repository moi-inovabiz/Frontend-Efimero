/**
 * Server-Side Theme Generation
 * Genera CSS variables en el servidor para evitar FOUC (Flash of Unstyled Content)
 */

import { cookies } from 'next/headers';
import { generateTheme, themeToCSS } from './theme-generator';

// En Docker, el frontend debe conectarse al backend usando el nombre del servicio
// API_URL es para llamadas desde el servidor (SSR)
// NEXT_PUBLIC_API_URL es para llamadas desde el cliente (browser)
const API_BASE_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000/api/v1';

interface Usuario {
  esquema_colores?: string;
  color_favorito?: string;
  estilo_tipografia?: string;
  densidad_informacion?: string;
  nivel_animaciones?: string;
}

/**
 * Obtiene el usuario desde el servidor usando el token de las cookies
 */
async function getUserFromServer(): Promise<Usuario | null> {
  try {
    const cookieStore = await cookies();
    const accessToken = cookieStore.get('access_token')?.value;

    if (!accessToken) {
      console.log('[SSR Theme] No access token found in cookies');
      return null;
    }

    console.log('[SSR Theme] Fetching user from backend with token:', accessToken.substring(0, 20) + '...');

    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
      cache: 'no-store', // No cachear para obtener datos frescos
    });

    if (!response.ok) {
      console.error('[SSR Theme] Failed to fetch user:', response.status, response.statusText);
      return null;
    }

    const user = await response.json();
    console.log('[SSR Theme] User fetched successfully:', {
      esquema_colores: user.esquema_colores,
      color_favorito: user.color_favorito,
      estilo_tipografia: user.estilo_tipografia,
    });

    return user;
  } catch (error) {
    console.error('[SSR Theme] Error fetching user from server:', error);
    return null;
  }
}

/**
 * Genera el CSS del tema en el servidor
 * Se ejecuta en Server Components para inyectar CSS antes del render inicial
 */
export async function generateServerThemeCSS(): Promise<string> {
  console.log('[SSR Theme] Generating server theme CSS...');
  const user = await getUserFromServer();
  
  if (!user) {
    console.log('[SSR Theme] No user found, using default theme');
  }
  
  const theme = generateTheme(user as any); // Cast porque solo necesitamos las preferencias visuales
  const css = themeToCSS(theme);
  
  console.log('[SSR Theme] Theme CSS generated successfully');
  return css;
}

/**
 * Genera un <style> tag con el tema del usuario
 * Para usar en Server Components: <style dangerouslySetInnerHTML={{ __html: await generateServerThemeTag() }} />
 */
export async function generateServerThemeTag(): Promise<string> {
  const css = await generateServerThemeCSS();
  return css;
}

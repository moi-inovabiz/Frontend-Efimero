/**
 * Theme Generator - Server & Client Side
 * Genera CSS variables dinámicas basadas en las preferencias del usuario
 */

import { Usuario } from './auth-client';

export interface ThemeColors {
  background: string;
  surface: string;
  primary: string;
  secondary: string;
  accent: string;
  text: string;
  textSecondary: string;
  border: string;
}

export interface ThemeConfig {
  colors: ThemeColors;
  fontFamily: string;
  fontSize: {
    base: string;
    heading: string;
    small: string;
  };
  spacing: {
    base: string;
    tight: string;
    loose: string;
  };
  animation: {
    duration: string;
    easing: string;
  };
  borderRadius: string;
}

// Esquemas de colores predefinidos
const COLOR_SCHEMES: Record<string, ThemeColors> = {
  automatico: {
    background: '#0f172a',
    surface: '#1e293b',
    primary: '#06b6d4',
    secondary: '#3b82f6',
    accent: '#8b5cf6',
    text: '#f1f5f9',
    textSecondary: '#94a3b8',
    border: '#334155',
  },
  claro: {
    background: '#ffffff',
    surface: '#f8fafc',
    primary: '#0284c7',
    secondary: '#2563eb',
    accent: '#7c3aed',
    text: '#0f172a',
    textSecondary: '#475569',
    border: '#e2e8f0',
  },
  oscuro: {
    background: '#000000',
    surface: '#0a0a0a',
    primary: '#22d3ee',
    secondary: '#60a5fa',
    accent: '#a78bfa',
    text: '#fafafa',
    textSecondary: '#a1a1aa',
    border: '#27272a',
  },
  alto_contraste: {
    background: '#000000',
    surface: '#1a1a1a',
    primary: '#00ffff',
    secondary: '#ffff00',
    accent: '#ff00ff',
    text: '#ffffff',
    textSecondary: '#e0e0e0',
    border: '#ffffff',
  },
  lujo: {
    background: '#0a0a0a',
    surface: '#1a1410',
    primary: '#d4af37',
    secondary: '#c9a961',
    accent: '#b8860b',
    text: '#faf8f3',
    textSecondary: '#d4c5a9',
    border: '#3d3428',
  },
  corporativo: {
    background: '#1e3a5f',
    surface: '#2c4f7c',
    primary: '#4a90e2',
    secondary: '#50c878',
    accent: '#ffa500',
    text: '#ffffff',
    textSecondary: '#b0c4de',
    border: '#4169e1',
  },
  moderno: {
    background: '#18181b',
    surface: '#27272a',
    primary: '#a855f7',
    secondary: '#ec4899',
    accent: '#f59e0b',
    text: '#fafafa',
    textSecondary: '#a1a1aa',
    border: '#3f3f46',
  },
};

// Colores de acento
const ACCENT_COLORS: Record<string, string> = {
  azul: '#3b82f6',
  verde: '#10b981',
  rojo: '#ef4444',
  amarillo: '#f59e0b',
  morado: '#8b5cf6',
  rosa: '#ec4899',
  cyan: '#06b6d4',
  naranja: '#f97316',
  negro: '#000000',
  blanco: '#ffffff',
};

// Familias tipográficas
const FONT_FAMILIES: Record<string, string> = {
  moderna_geometrica: 'Inter, system-ui, -apple-system, sans-serif',
  elegante_serif: 'Playfair Display, Georgia, serif',
  technica_monospace: 'Fira Code, Monaco, monospace',
  humanista_sans: 'Open Sans, Helvetica, Arial, sans-serif',
  clasica_tradicional: 'Times New Roman, Times, serif',
};

// Niveles de densidad de información
const DENSITY_CONFIG: Record<string, { spacing: string; fontSize: string }> = {
  minimalista: { spacing: '2rem', fontSize: '1.125rem' },
  comoda: { spacing: '1.5rem', fontSize: '1rem' },
  compacta: { spacing: '1rem', fontSize: '0.875rem' },
  maxima: { spacing: '0.75rem', fontSize: '0.8125rem' },
};

// Niveles de animaciones
const ANIMATION_CONFIG: Record<string, { duration: string; easing: string }> = {
  ninguna: { duration: '0ms', easing: 'linear' },
  sutiles: { duration: '150ms', easing: 'ease-out' },
  moderadas: { duration: '300ms', easing: 'cubic-bezier(0.4, 0, 0.2, 1)' },
  dinamicas: { duration: '500ms', easing: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)' },
};

/**
 * Genera la configuración del tema basada en las preferencias del usuario
 */
export function generateTheme(user: Usuario | null): ThemeConfig {
  // Valores por defecto si no hay usuario
  const esquemaColores = user?.esquema_colores || 'automatico';
  const colorFavorito = user?.color_favorito || 'azul';
  const estiloTipografia = user?.estilo_tipografia || 'moderna_geometrica';
  const densidadInformacion = user?.densidad_informacion || 'comoda';
  const nivelAnimaciones = user?.nivel_animaciones || 'moderadas';

  // Obtener colores base del esquema
  const baseColors = COLOR_SCHEMES[esquemaColores] || COLOR_SCHEMES.automatico;

  // Aplicar color de acento favorito
  const accentColor = ACCENT_COLORS[colorFavorito] || ACCENT_COLORS.azul;
  const colors: ThemeColors = {
    ...baseColors,
    accent: accentColor,
  };

  // Configuración de densidad
  const density = DENSITY_CONFIG[densidadInformacion] || DENSITY_CONFIG.comoda;

  // Configuración de animaciones
  const animation = ANIMATION_CONFIG[nivelAnimaciones] || ANIMATION_CONFIG.moderadas;

  // Familia tipográfica
  const fontFamily = FONT_FAMILIES[estiloTipografia] || FONT_FAMILIES.moderna_geometrica;

  return {
    colors,
    fontFamily,
    fontSize: {
      base: density.fontSize,
      heading: `calc(${density.fontSize} * 1.5)`,
      small: `calc(${density.fontSize} * 0.875)`,
    },
    spacing: {
      base: density.spacing,
      tight: `calc(${density.spacing} * 0.5)`,
      loose: `calc(${density.spacing} * 1.5)`,
    },
    animation,
    borderRadius: densidadInformacion === 'minimalista' ? '0.75rem' : '0.5rem',
  };
}

/**
 * Convierte la configuración del tema a CSS variables
 */
export function themeToCSS(theme: ThemeConfig): string {
  return `
    :root {
      /* Colors */
      --color-background: ${theme.colors.background};
      --color-surface: ${theme.colors.surface};
      --color-primary: ${theme.colors.primary};
      --color-secondary: ${theme.colors.secondary};
      --color-accent: ${theme.colors.accent};
      --color-text: ${theme.colors.text};
      --color-text-secondary: ${theme.colors.textSecondary};
      --color-border: ${theme.colors.border};

      /* Typography */
      --font-family: ${theme.fontFamily};
      --font-size-base: ${theme.fontSize.base};
      --font-size-heading: ${theme.fontSize.heading};
      --font-size-small: ${theme.fontSize.small};

      /* Spacing */
      --spacing-base: ${theme.spacing.base};
      --spacing-tight: ${theme.spacing.tight};
      --spacing-loose: ${theme.spacing.loose};

      /* Animation */
      --animation-duration: ${theme.animation.duration};
      --animation-easing: ${theme.animation.easing};

      /* Border Radius */
      --border-radius: ${theme.borderRadius};
    }
  `.trim();
}

/**
 * Genera un inline style tag con las CSS variables
 */
export function generateThemeStyleTag(user: Usuario | null): string {
  const theme = generateTheme(user);
  const css = themeToCSS(theme);
  return `<style id="user-theme">${css}</style>`;
}

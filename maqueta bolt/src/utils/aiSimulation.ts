import { UserContext } from '../hooks/useContextCapture';

export interface DesignTokens {
  '--font-size-base': string;
  '--font-size-heading': string;
  '--font-weight': string;
  '--line-height': string;
  '--spacing-unit': string;
  '--spacing-compact': string;
  '--spacing-comfortable': string;
  '--border-radius': string;
  '--border-radius-large': string;
  '--primary-color': string;
  '--secondary-color': string;
  '--bg-primary': string;
  '--bg-secondary': string;
  '--text-primary': string;
  '--text-secondary': string;
  '--shadow': string;
  '--transition-speed': string;
}

export async function predictDesignTokens(context: UserContext): Promise<DesignTokens> {
  const delay = Math.floor(Math.random() * 200) + 100;
  await new Promise(resolve => setTimeout(resolve, delay));

  const { isNight, isSmallScreen, prefersDark, hour } = context;

  const isMorning = hour >= 6 && hour < 12;
  const isAfternoon = hour >= 12 && hour < 18;
  const isEvening = hour >= 18 || hour < 6;

  let fontSizeBase = '1rem';
  let fontSizeHeading = '2rem';
  let fontWeight = '400';
  let lineHeight = '1.5';

  if (isNight) {
    fontSizeBase = '1.1rem';
    fontSizeHeading = '2.25rem';
    fontWeight = '300';
    lineHeight = '1.6';
  } else if (isMorning) {
    fontSizeBase = '0.95rem';
    fontSizeHeading = '1.875rem';
    fontWeight = '500';
    lineHeight = '1.4';
  }

  const spacingUnit = isSmallScreen ? '0.75rem' : '1rem';
  const spacingCompact = isSmallScreen ? '0.5rem' : '0.75rem';
  const spacingComfortable = isSmallScreen ? '1rem' : '1.5rem';

  let borderRadius = '8px';
  let borderRadiusLarge = '16px';

  if (prefersDark) {
    borderRadius = '12px';
    borderRadiusLarge = '20px';
  } else if (isMorning) {
    borderRadius = '4px';
    borderRadiusLarge = '12px';
  }

  let primaryColor = '#3b82f6';
  let secondaryColor = '#8b5cf6';
  let bgPrimary = '#ffffff';
  let bgSecondary = '#f3f4f6';
  let textPrimary = '#111827';
  let textSecondary = '#6b7280';
  let shadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';

  if (isNight || prefersDark) {
    primaryColor = '#60a5fa';
    secondaryColor = '#a78bfa';
    bgPrimary = '#1f2937';
    bgSecondary = '#111827';
    textPrimary = '#f9fafb';
    textSecondary = '#d1d5db';
    shadow = '0 4px 6px -1px rgba(0, 0, 0, 0.3)';
  } else if (isAfternoon) {
    primaryColor = '#f59e0b';
    secondaryColor = '#ef4444';
    bgPrimary = '#fffbeb';
    bgSecondary = '#fef3c7';
    textPrimary = '#78350f';
    textSecondary = '#92400e';
    shadow = '0 4px 6px -1px rgba(245, 158, 11, 0.15)';
  } else if (isEvening) {
    primaryColor = '#8b5cf6';
    secondaryColor = '#ec4899';
    bgPrimary = '#faf5ff';
    bgSecondary = '#f3e8ff';
    textPrimary = '#5b21b6';
    textSecondary = '#7c3aed';
    shadow = '0 4px 6px -1px rgba(139, 92, 246, 0.15)';
  }

  const transitionSpeed = isSmallScreen ? '200ms' : '300ms';

  return {
    '--font-size-base': fontSizeBase,
    '--font-size-heading': fontSizeHeading,
    '--font-weight': fontWeight,
    '--line-height': lineHeight,
    '--spacing-unit': spacingUnit,
    '--spacing-compact': spacingCompact,
    '--spacing-comfortable': spacingComfortable,
    '--border-radius': borderRadius,
    '--border-radius-large': borderRadiusLarge,
    '--primary-color': primaryColor,
    '--secondary-color': secondaryColor,
    '--bg-primary': bgPrimary,
    '--bg-secondary': bgSecondary,
    '--text-primary': textPrimary,
    '--text-secondary': textSecondary,
    '--shadow': shadow,
    '--transition-speed': transitionSpeed,
  };
}

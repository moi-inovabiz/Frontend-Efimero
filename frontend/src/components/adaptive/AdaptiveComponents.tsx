/**
 * Componente adaptativo que consume variables CSS predichas por IA
 * Ejemplo de implementación del Frontend Efímero
 */

'use client';

import React from 'react';
import { useAdaptiveUI } from './AdaptiveUIProvider';

interface AdaptiveButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  className?: string;
}

export function AdaptiveButton({ 
  children, 
  onClick, 
  variant = 'primary',
  className = ''
}: AdaptiveButtonProps) {
  const { sendFeedback } = useAdaptiveUI();

  const handleClick = () => {
    // Enviar feedback de interacción (FASE 3)
    sendFeedback('click', undefined, `adaptive-button-${variant}`);
    onClick?.();
  };

  const baseStyles = `
    px-[var(--spacing-unit)] 
    py-[calc(var(--spacing-unit)*0.5)] 
    rounded-[var(--border-radius)]
    font-size-[var(--font-size-base)]
    transition-all duration-200
    focus:outline-none
    focus:ring-2 focus:ring-offset-2
  `;

  const variantStyles = {
    primary: `
      bg-blue-600 text-white 
      hover:bg-blue-700 
      focus:ring-blue-500
    `,
    secondary: `
      bg-gray-200 text-gray-900 
      hover:bg-gray-300 
      focus:ring-gray-500
    `
  };

  return (
    <button
      onClick={handleClick}
      className={`${baseStyles} ${variantStyles[variant]} ${className}`.trim()}
    >
      {children}
    </button>
  );
}

interface AdaptiveCardProps {
  children: React.ReactNode;
  title?: string;
  className?: string;
}

export function AdaptiveCard({ children, title, className = '' }: AdaptiveCardProps) {
  const { sendFeedback } = useAdaptiveUI();

  return (
    <div
      className={`
        p-[var(--spacing-unit)]
        rounded-[var(--border-radius)]
        bg-white shadow-md
        border border-gray-200
        ${className}
      `.trim()}
      onMouseEnter={() => sendFeedback('hover', undefined, 'adaptive-card')}
    >
      {title && (
        <h3 
          className="
            text-[calc(var(--font-size-base)*1.25)] 
            font-semibold 
            mb-[calc(var(--spacing-unit)*0.5)]
            text-gray-900
          "
        >
          {title}
        </h3>
      )}
      {children}
    </div>
  );
}

interface AdaptiveTextProps {
  children: React.ReactNode;
  size?: 'sm' | 'base' | 'lg' | 'xl';
  className?: string;
}

export function AdaptiveText({ children, size = 'base', className = '' }: AdaptiveTextProps) {
  const sizeMultipliers = {
    sm: '0.875',
    base: '1',
    lg: '1.125', 
    xl: '1.25'
  };

  return (
    <p
      className={`
        text-[calc(var(--font-size-base)*${sizeMultipliers[size]})]
        leading-relaxed
        text-gray-700
        ${className}
      `.trim()}
    >
      {children}
    </p>
  );
}
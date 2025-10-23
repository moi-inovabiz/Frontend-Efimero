import React from 'react';

interface AdaptiveButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
}

export function AdaptiveButton({ children, onClick, variant = 'primary' }: AdaptiveButtonProps) {
  return (
    <button
      onClick={onClick}
      className="adaptive-button"
      data-variant={variant}
      style={{
        fontSize: 'var(--font-size-base)',
        fontWeight: 'var(--font-weight)',
        padding: 'var(--spacing-unit) var(--spacing-comfortable)',
        borderRadius: 'var(--border-radius)',
        backgroundColor: variant === 'primary' ? 'var(--primary-color)' : 'var(--secondary-color)',
        color: '#ffffff',
        border: 'none',
        cursor: 'pointer',
        boxShadow: 'var(--shadow)',
        transition: `all var(--transition-speed) ease-in-out`,
      }}
    >
      {children}
    </button>
  );
}

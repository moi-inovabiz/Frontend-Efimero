import React from 'react';

interface AdaptiveTextProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'heading';
}

export function AdaptiveText({ children, variant = 'primary' }: AdaptiveTextProps) {
  const getStyles = () => {
    if (variant === 'heading') {
      return {
        fontSize: 'var(--font-size-heading)',
        fontWeight: '700',
        color: 'var(--text-primary)',
        lineHeight: '1.2',
      };
    }

    return {
      fontSize: 'var(--font-size-base)',
      fontWeight: 'var(--font-weight)',
      color: variant === 'primary' ? 'var(--text-primary)' : 'var(--text-secondary)',
      lineHeight: 'var(--line-height)',
    };
  };

  const Component = variant === 'heading' ? 'h2' : 'p';

  return (
    <Component
      className="adaptive-text"
      style={{
        ...getStyles(),
        transition: `all var(--transition-speed) ease-in-out`,
        margin: 0,
      }}
    >
      {children}
    </Component>
  );
}

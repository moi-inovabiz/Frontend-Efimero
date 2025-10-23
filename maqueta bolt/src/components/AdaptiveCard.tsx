import React from 'react';

interface AdaptiveCardProps {
  children: React.ReactNode;
  title?: string;
}

export function AdaptiveCard({ children, title }: AdaptiveCardProps) {
  return (
    <div
      className="adaptive-card"
      style={{
        backgroundColor: 'var(--bg-primary)',
        borderRadius: 'var(--border-radius-large)',
        padding: 'var(--spacing-comfortable)',
        boxShadow: 'var(--shadow)',
        transition: `all var(--transition-speed) ease-in-out`,
      }}
    >
      {title && (
        <h3
          style={{
            fontSize: 'var(--font-size-heading)',
            fontWeight: '600',
            color: 'var(--text-primary)',
            marginBottom: 'var(--spacing-unit)',
            transition: `all var(--transition-speed) ease-in-out`,
          }}
        >
          {title}
        </h3>
      )}
      <div
        style={{
          color: 'var(--text-secondary)',
          fontSize: 'var(--font-size-base)',
          lineHeight: 'var(--line-height)',
          transition: `all var(--transition-speed) ease-in-out`,
        }}
      >
        {children}
      </div>
    </div>
  );
}

import React from 'react';
import { UserContext } from '../hooks/useContextCapture';
import { Activity } from 'lucide-react';

interface ContextDisplayProps {
  context: UserContext;
}

export function ContextDisplay({ context }: ContextDisplayProps) {
  return (
    <div
      style={{
        backgroundColor: 'var(--bg-secondary)',
        borderRadius: 'var(--border-radius)',
        padding: 'var(--spacing-unit)',
        fontFamily: 'monospace',
        fontSize: '0.875rem',
        transition: `all var(--transition-speed) ease-in-out`,
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-compact)',
          marginBottom: 'var(--spacing-compact)',
          color: 'var(--text-primary)',
          fontWeight: '600',
        }}
      >
        <Activity size={16} />
        <span>PHASE 1: Context Captured</span>
      </div>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'auto 1fr',
          gap: 'var(--spacing-compact)',
          color: 'var(--text-secondary)',
        }}
      >
        <span>Hour:</span>
        <span>{context.hour}:00</span>

        <span>Screen:</span>
        <span>{context.screenWidth}x{context.screenHeight}px</span>

        <span>Prefers Dark:</span>
        <span>{context.prefersDark ? 'Yes' : 'No'}</span>

        <span>Is Night:</span>
        <span>{context.isNight ? 'Yes' : 'No'}</span>

        <span>Is Small:</span>
        <span>{context.isSmallScreen ? 'Yes' : 'No'}</span>

        <span>Timestamp:</span>
        <span>{new Date(context.timestamp).toLocaleTimeString()}</span>
      </div>
    </div>
  );
}

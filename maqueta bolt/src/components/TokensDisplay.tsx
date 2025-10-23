import React from 'react';
import { DesignTokens } from '../utils/aiSimulation';
import { Sparkles } from 'lucide-react';

interface TokensDisplayProps {
  tokens: DesignTokens | null;
  isLoading: boolean;
}

export function TokensDisplay({ tokens, isLoading }: TokensDisplayProps) {
  if (isLoading) {
    return (
      <div
        style={{
          backgroundColor: 'var(--bg-secondary)',
          borderRadius: 'var(--border-radius)',
          padding: 'var(--spacing-unit)',
          fontFamily: 'monospace',
          fontSize: '0.875rem',
          color: 'var(--text-secondary)',
          transition: `all var(--transition-speed) ease-in-out`,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-compact)' }}>
          <Sparkles size={16} className="animate-pulse" />
          <span>PHASE 2: AI Predicting Tokens...</span>
        </div>
      </div>
    );
  }

  if (!tokens) return null;

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
        <Sparkles size={16} />
        <span>PHASE 3: Design Tokens Applied</span>
      </div>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'auto 1fr',
          gap: 'var(--spacing-compact)',
          color: 'var(--text-secondary)',
          maxHeight: '300px',
          overflowY: 'auto',
        }}
      >
        {Object.entries(tokens).map(([key, value]) => (
          <React.Fragment key={key}>
            <span>{key}:</span>
            <span style={{ color: 'var(--primary-color)' }}>{value}</span>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

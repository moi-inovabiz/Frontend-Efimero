import { useEffect, useState } from 'react';

interface LoadingScreenProps {
  onLoadingComplete: () => void;
}

export function LoadingScreen({ onLoadingComplete }: LoadingScreenProps) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(onLoadingComplete, 300);
          return 100;
        }
        return prev + 2;
      });
    }, 30);

    return () => clearInterval(interval);
  }, [onLoadingComplete]);

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #000000 0%, #1a1a1a 100%)',
        color: '#ffffff',
      }}
    >
      <div style={{ textAlign: 'center', maxWidth: '600px', padding: '2rem' }}>
        <h1
          style={{
            fontSize: '3rem',
            fontWeight: '700',
            marginBottom: '1rem',
            letterSpacing: '0.05em',
          }}
        >
          Bienvenido
        </h1>
        <p
          style={{
            fontSize: '1.2rem',
            marginBottom: '3rem',
            color: '#a0a0a0',
          }}
        >
          Preparando tu experiencia Mercedes-Benz
        </p>

        <div
          style={{
            width: '100%',
            height: '4px',
            backgroundColor: '#333',
            borderRadius: '2px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${progress}%`,
              height: '100%',
              background: 'linear-gradient(90deg, #00adef 0%, #0066cc 100%)',
              transition: 'width 0.3s ease',
            }}
          />
        </div>

        <p
          style={{
            marginTop: '1rem',
            fontSize: '0.9rem',
            color: '#666',
          }}
        >
          {progress}%
        </p>
      </div>
    </div>
  );
}

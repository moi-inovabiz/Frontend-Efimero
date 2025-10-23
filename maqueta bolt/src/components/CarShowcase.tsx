import { Car, Gauge, Settings, Zap, Shield, Smartphone } from 'lucide-react';

export function CarShowcase() {
  const features = [
    { icon: Gauge, label: 'Motor 4.0L V8 Biturbo' },
    { icon: Zap, label: '577 HP de Potencia' },
    { icon: Car, label: 'Tracción 4MATIC+' },
    { icon: Settings, label: 'Transmisión AMG Speedshift' },
    { icon: Shield, label: 'Sistema de Seguridad Activo' },
    { icon: Smartphone, label: 'MBUX Multimedia' },
  ];

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(to bottom, #0a0a0a 0%, #1a1a1a 100%)',
        color: '#ffffff',
        padding: '2rem',
      }}
    >
      <div
        style={{
          maxWidth: '1400px',
          margin: '0 auto',
        }}
      >
        <header style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h1
            style={{
              fontSize: 'clamp(1.5rem, 4vw, 2.5rem)',
              fontWeight: '700',
              marginBottom: '0.5rem',
              letterSpacing: '0.02em',
            }}
          >
            Mercedes-Benz AMG GT 2025
          </h1>
          <p
            style={{
              fontSize: 'clamp(1rem, 2vw, 1.3rem)',
              color: '#00adef',
              fontWeight: '500',
            }}
          >
            GT 63 AMG 4.0 AUT
          </p>
        </header>

        <div
          style={{
            width: '100%',
            maxWidth: '1200px',
            margin: '0 auto 3rem',
            borderRadius: '20px',
            overflow: 'hidden',
            boxShadow: '0 20px 60px rgba(0, 173, 239, 0.3)',
          }}
        >
          <img
            src="https://images.pexels.com/photos/3849168/pexels-photo-3849168.jpeg?auto=compress&cs=tinysrgb&w=1200"
            alt="Mercedes-Benz AMG GT"
            style={{
              width: '100%',
              height: 'auto',
              display: 'block',
            }}
          />
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1.5rem',
            marginBottom: '3rem',
          }}
        >
          {features.map((feature, index) => (
            <button
              key={index}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                padding: '1.5rem',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '12px',
                color: '#ffffff',
                fontSize: '1rem',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                textAlign: 'left',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(0, 173, 239, 0.1)';
                e.currentTarget.style.borderColor = '#00adef';
                e.currentTarget.style.transform = 'translateY(-4px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <feature.icon size={24} style={{ color: '#00adef', flexShrink: 0 }} />
              <span>{feature.label}</span>
            </button>
          ))}
        </div>

        <div style={{ textAlign: 'center' }}>
          <button
            style={{
              padding: '1.5rem 4rem',
              fontSize: '1.3rem',
              fontWeight: '700',
              background: 'linear-gradient(135deg, #00adef 0%, #0066cc 100%)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '50px',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 10px 30px rgba(0, 173, 239, 0.4)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 15px 40px rgba(0, 173, 239, 0.6)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 173, 239, 0.4)';
            }}
          >
            Comprar
          </button>
        </div>

        <footer
          style={{
            marginTop: '4rem',
            paddingTop: '2rem',
            borderTop: '1px solid rgba(255, 255, 255, 0.1)',
            textAlign: 'center',
            color: '#666',
            fontSize: '0.9rem',
          }}
        >
          <p>© 2025 Mercedes-Benz. Todos los derechos reservados.</p>
        </footer>
      </div>
    </div>
  );
}

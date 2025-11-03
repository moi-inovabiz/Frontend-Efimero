/**
 * Loading Dashboard Page
 * Página intermedia que se muestra después del registro/login
 * para dar tiempo a que las cookies se guarden y el SSR se prepare
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function LoadingDashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Preparando tu experiencia...');

  useEffect(() => {
    if (!isAuthenticated) {
      // Si no está autenticado, redirigir al login
      router.push('/login');
      return;
    }

    // Simular progreso de carga
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + 10;
      });
    }, 200);

    // Secuencia de estados
    const statusTimeout1 = setTimeout(() => {
      setStatus('Aplicando tus preferencias visuales...');
    }, 800);

    const statusTimeout2 = setTimeout(() => {
      setStatus('Configurando tu dashboard personalizado...');
    }, 1600);

    const statusTimeout3 = setTimeout(() => {
      setStatus('¡Casi listo!');
    }, 2400);

    // Esperar 3 segundos para que:
    // 1. Las cookies se guarden correctamente
    // 2. El tema se aplique en el cliente
    // 3. El SSR tenga tiempo de prepararse para la próxima carga
    const redirectTimeout = setTimeout(() => {
      // Forzar una navegación completa (no client-side) para que el SSR se ejecute
      window.location.href = '/dashboard';
    }, 3000);

    return () => {
      clearInterval(progressInterval);
      clearTimeout(statusTimeout1);
      clearTimeout(statusTimeout2);
      clearTimeout(statusTimeout3);
      clearTimeout(redirectTimeout);
    };
  }, [isAuthenticated, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      <div className="w-full max-w-md p-8">
        {/* Logo o icono animado */}
        <div className="flex justify-center mb-8">
          <div className="relative w-24 h-24">
            {/* Círculo exterior rotando */}
            <div className="absolute inset-0 border-4 border-cyan-500/20 rounded-full animate-spin border-t-cyan-500"></div>
            {/* Círculo interior rotando en dirección opuesta */}
            <div className="absolute inset-3 border-4 border-blue-500/20 rounded-full animate-spin-reverse border-t-blue-500"></div>
            {/* Centro */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-8 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>

        {/* Mensaje de bienvenida */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-2">
            ¡Bienvenido{user?.nombre ? `, ${user.nombre}` : ''}!
          </h1>
          <p className="text-gray-400 text-sm">
            {status}
          </p>
        </div>

        {/* Barra de progreso */}
        <div className="w-full bg-gray-700/50 rounded-full h-3 overflow-hidden backdrop-blur-sm">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-300 ease-out relative overflow-hidden"
            style={{ width: `${progress}%` }}
          >
            {/* Efecto de brillo animado */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
          </div>
        </div>

        {/* Porcentaje */}
        <div className="text-center mt-4 text-cyan-400 font-mono text-sm">
          {progress}%
        </div>

        {/* Mensaje adicional */}
        <div className="text-center mt-8 text-gray-500 text-xs">
          <p>Estamos preparando tu dashboard con tus preferencias personalizadas</p>
        </div>
      </div>

      {/* CSS para animaciones personalizadas */}
      <style jsx>{`
        @keyframes spin-reverse {
          from {
            transform: rotate(360deg);
          }
          to {
            transform: rotate(0deg);
          }
        }

        @keyframes shimmer {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }

        .animate-spin-reverse {
          animation: spin-reverse 2s linear infinite;
        }

        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
      `}</style>
    </div>
  );
}
